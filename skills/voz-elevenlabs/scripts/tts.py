#!/usr/bin/env python3
"""TTS opcional vía ElevenLabs → WAV para el pipeline de voz.

Uso:
  python3 -I scripts/tts.py listar [--voces RUTA]
  python3 -I scripts/tts.py sintetizar <slug> --project-dir DIR (--texto STR | --guion FILE)
      [--voz ALIAS | --voice-id ID] [--modelo ID] [--api-key KEY] [--voces RUTA]

Requiere ELEVENLABS_API_KEY (o --api-key), Python 3 y FFmpeg para WAV.
No escribe la API key en disco. Detalle en el SKILL.md de voz-elevenlabs.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

API_BASE = 'https://api.elevenlabs.io/v1'
SLUG_RE = re.compile(r'^[a-z0-9][a-z0-9-]*$')
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_VOCES = os.path.join(HERE, 'voces.json')


def die(msg: str) -> None:
    sys.exit('tts.py: ' + msg)


def api_key(a) -> str:
    key = (a.api_key or os.environ.get('ELEVENLABS_API_KEY') or '').strip()
    if not key:
        die('falta ELEVENLABS_API_KEY o --api-key (síntesis opcional; no hay clave)')
    return key


def load_voces(path: str) -> dict:
    p = os.path.abspath(path or DEFAULT_VOCES)
    if not os.path.isfile(p):
        die(f'no existe el registro de voces: {p}')
    with open(p, encoding='utf-8') as f:
        data = json.load(f)
    if not isinstance(data.get('voces'), dict) or not data['voces']:
        die(f'registro inválido (falta voces{{}}): {p}')
    return data


def resolve_voice(reg: dict, alias: str | None, voice_id: str | None) -> tuple[str, str, dict]:
    """Devuelve (voice_id, alias_o_id, entrada_registro)."""
    if voice_id:
        voces = reg['voces']
        for name, meta in voces.items():
            if meta.get('voice_id') == voice_id:
                return voice_id, name, meta
        return voice_id, voice_id, {
            'voice_id': voice_id,
            'model_id': reg.get('modelo_default', 'eleven_multilingual_v2'),
        }
    name = alias or reg.get('default')
    if not name:
        die('indica --voz, --voice-id o default en voces.json')
    meta = reg['voces'].get(name)
    if not meta:
        known = ', '.join(sorted(reg['voces']))
        die(f'alias desconocido {name!r}; disponibles: {known}')
    vid = meta.get('voice_id')
    if not vid or not isinstance(vid, str):
        die(f'falta voice_id en voces[{name}]')
    return vid, name, meta


def http_json(method: str, url: str, key: str, body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            'xi-api-key': key,
            'Accept': 'application/json',
            **({'Content-Type': 'application/json'} if body is not None else {}),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            raw = r.read()
            return json.loads(raw.decode('utf-8')) if raw else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode('utf-8', 'replace')[-1500:]
        die(f'HTTP {e.code} en {url}:\n{err}')
    except urllib.error.URLError as e:
        die(f'no se pudo conectar a ElevenLabs: {e.reason}')


def http_audio(url: str, key: str, body: dict, dest: str) -> None:
    data = json.dumps(body).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data,
        method='POST',
        headers={
            'xi-api-key': key,
            'Accept': 'audio/mpeg',
            'Content-Type': 'application/json',
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            audio = r.read()
    except urllib.error.HTTPError as e:
        err = e.read().decode('utf-8', 'replace')[-1500:]
        die(f'HTTP {e.code} TTS:\n{err}')
    except urllib.error.URLError as e:
        die(f'no se pudo conectar a ElevenLabs: {e.reason}')
    if not audio:
        die('respuesta de audio vacía')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, 'wb') as f:
        f.write(audio)


def ffmpeg_wav(src_mp3: str, dst_wav: str) -> None:
    cmd = [
        'ffmpeg', '-hide_banner', '-nostdin', '-y',
        '-i', src_mp3,
        '-ac', '1', '-ar', '44100', '-c:a', 'pcm_s16le',
        dst_wav,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        die(f'fallo ffmpeg:\n{r.stderr[-1500:]}')


def proyecto(slug: str, project_dir: str | None) -> str:
    if not SLUG_RE.match(slug or ''):
        die(f'slug inválido: {slug!r}')
    if not project_dir:
        die('indica --project-dir con la carpeta del proyecto (debe tener video.json)')
    p = os.path.abspath(project_dir)
    if not os.path.isfile(os.path.join(p, 'video.json')):
        die(f'no existe video.json en {p}')
    return p


def workdir(project: str) -> str:
    w = os.path.join(project, '.work', 'voz')
    os.makedirs(w, exist_ok=True)
    return w


def cmd_listar(a) -> None:
    reg = load_voces(a.voces)
    print('Registro local:', os.path.abspath(a.voces or DEFAULT_VOCES))
    print('default:', reg.get('default'))
    print('modelo_default:', reg.get('modelo_default'))
    for name, meta in sorted(reg['voces'].items()):
        print(f"  {name}: voice_id={meta.get('voice_id')}  ({meta.get('label', '')})")
    if a.remoto:
        key = api_key(a)
        data = http_json('GET', f'{API_BASE}/voices', key)
        print('\nVoces en la cuenta ElevenLabs:')
        for v in data.get('voices') or []:
            print(f"  {v.get('name')}: {v.get('voice_id')}")


def leer_texto(a) -> str:
    if a.texto and a.guion:
        die('usa solo uno: --texto o --guion')
    if a.texto:
        t = a.texto.strip()
    elif a.guion:
        path = os.path.abspath(a.guion)
        if not os.path.isfile(path):
            die(f'no existe el guion: {path}')
        with open(path, encoding='utf-8') as f:
            t = f.read().strip()
    else:
        die('indica --texto o --guion')
    if not t:
        die('texto vacío')
    return t


def cmd_sintetizar(a) -> None:
    key = api_key(a)
    reg = load_voces(a.voces)
    vid, alias, meta = resolve_voice(reg, a.voz, a.voice_id)
    texto = leer_texto(a)
    model = a.modelo or meta.get('model_id') or reg.get('modelo_default') or 'eleven_multilingual_v2'
    project = proyecto(a.slug, a.project_dir)
    w = workdir(project)
    mp3 = os.path.join(w, '00-elevenlabs.mp3')
    wav = os.path.join(w, '00-entrada.wav')
    meta_out = os.path.join(w, '00-elevenlabs.json')

    body: dict = {
        'text': texto,
        'model_id': model,
    }
    settings = meta.get('voice_settings')
    if isinstance(settings, dict) and settings:
        body['voice_settings'] = settings
    # language_code no aplica a multilingual_v2; solo si el usuario/modelo lo pediría en otros modelos
    lang = meta.get('language_code')
    if lang and model != 'eleven_multilingual_v2':
        body['language_code'] = lang

    url = f'{API_BASE}/text-to-speech/{vid}?output_format=mp3_44100_128'
    print(f'sintetizando alias={alias} voice_id={vid} modelo={model} chars={len(texto)}')
    http_audio(url, key, body, mp3)
    ffmpeg_wav(mp3, wav)

    info = {
        'alias': alias,
        'voice_id': vid,
        'model_id': model,
        'chars': len(texto),
        'mp3': os.path.basename(mp3),
        'wav': os.path.basename(wav),
        'label': meta.get('label'),
        'fuente': 'elevenlabs',
    }
    with open(meta_out, 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print('escrito', mp3)
    print('escrito', wav)
    print('escrito', meta_out)
    print('siguiente: voz-whisper entrada con --entrada', wav)


def main() -> None:
    ap = argparse.ArgumentParser(prog='tts.py', description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)

    p_list = sub.add_parser('listar', help='lista aliases locales y, con --remoto, voces de la API')
    p_list.add_argument('--voces', help=f'registro JSON (default {DEFAULT_VOCES})')
    p_list.add_argument('--remoto', action='store_true', help='también lista voces de la cuenta')
    p_list.add_argument('--api-key', help='override de ELEVENLABS_API_KEY')

    p_syn = sub.add_parser('sintetizar', help='genera MP3+WAV en .work/voz del proyecto')
    p_syn.add_argument('slug', help='etiqueta del proyecto (minúsculas, números, guiones)')
    p_syn.add_argument('--project-dir', required=True, help='proyecto con video.json')
    p_syn.add_argument('--texto', help='texto a sintetizar')
    p_syn.add_argument('--guion', help='archivo de texto/guion')
    p_syn.add_argument('--voz', help='alias en voces.json')
    p_syn.add_argument('--voice-id', help='ID directo de ElevenLabs')
    p_syn.add_argument('--modelo', help='model_id (default del registro o eleven_multilingual_v2)')
    p_syn.add_argument('--voces', help=f'registro JSON (default {DEFAULT_VOCES})')
    p_syn.add_argument('--api-key', help='override de ELEVENLABS_API_KEY')

    a = ap.parse_args()
    if a.cmd == 'listar':
        cmd_listar(a)
    elif a.cmd == 'sintetizar':
        cmd_sintetizar(a)
    else:
        die(f'comando desconocido: {a.cmd}')


if __name__ == '__main__':
    main()
