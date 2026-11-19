#!/usr/bin/env python3
"""Locución generada fuera del pipeline (web de ElevenLabs): el video se adapta al audio descargado.

Uso:
  python3 -I scripts/externa.py guion --guion canonico.txt [--etiquetado etiquetado.txt] [--equiv equiv.json]
  python3 -I scripts/externa.py importar <slug> --project-dir DIR --audio ARCHIVO --guion canonico.txt
      --modelo RUTA [--motor faster-whisper|whisper-cpp] [--etiquetado etiquetado.txt] [--equiv equiv.json]
      [--umbral -45] [--reemplazar] [--rehacer-asr]
  python3 -I scripts/externa.py entregar <slug> --project-dir DIR [--normalizar] [--nombre N] [--reemplazar]

canonico.txt: una frase por línea no vacía, tal como se verá en pantalla y subtítulos («id|texto» fija el id;
  sin él, p01, p02…). Las líneas que empiezan con # se ignoran.
etiquetado.txt: el texto que se pega en la web de ElevenLabs, con etiquetas entre corchetes o <break …/>.
equiv.json: {"patrón": "reemplazo"} sobre texto en minúsculas y sin acentos, para que el guion y lo que oye
  el ASR se comparen igual (p. ej. {"\\b4\\b": "cuatro"}).

importar no modifica el audio: copia el original, transcribe con un modelo local, empareja las palabras con el
guion canónico y ajusta los bordes a los silencios medidos. No descarga modelos. Detalle en el SKILL.md.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata

for _s in (sys.stdout, sys.stderr):  # con -I se ignora PYTHONIOENCODING: que un símbolo no tumbe la salida
    try:
        _s.reconfigure(errors='replace')
    except Exception:
        pass

SR = 16000
HOP = 0.01
SLUG_RE = re.compile(r'^[a-z0-9][a-z0-9-]*$')
ID_RE = re.compile(r'^([A-Za-z0-9_-]+)\s*\|\s*(.+)$')
TAG_RE = re.compile(r'\[[^\]]*\]|<break[^>]*>', re.I)
NOMBRE_RE = re.compile(r'^ElevenLabs_(?P<fecha>\d{4}-\d{2}-\d{2}T\d{2}_\d{2}_\d{2})_(?P<resto>.+)$')
RESTO_RE = re.compile(r'^(?P<voz>.*?)(?:_(?P<tipo>pvc|ivc))?(?:_s(?P<s>\d+))?(?:_sim(?P<sim>\d+))?(?:_(?P<v>v\d+\w*))?$')
FFMPEG = os.environ.get('FFMPEG') or 'ffmpeg'
FFPROBE = os.environ.get('FFPROBE') or 'ffprobe'
PAUSA_INFORME = 0.30  # s: huecos entre palabras que se listan en el informe


def die(msg: str) -> None:
    sys.exit('externa.py: ' + msg)


def run(cmd: list, binario: bool = False) -> subprocess.CompletedProcess:
    try:
        r = subprocess.run(cmd, capture_output=True, **({} if binario else {'text': True, 'encoding': 'utf-8', 'errors': 'replace'}))
    except FileNotFoundError:
        die(f'no encuentro {cmd[0]} (ponlo en PATH o usa las variables FFMPEG/FFPROBE)')
    if r.returncode != 0:
        err = r.stderr.decode('utf-8', 'replace') if binario else r.stderr
        die(f'falló {os.path.basename(cmd[0])} (código {r.returncode}):\n{err[-1500:]}')
    return r


# ---------- guion ----------
def leer_guion(path: str) -> list[tuple[str, str]]:
    if not os.path.isfile(path):
        die(f'no existe el guion: {path}')
    frases = []
    for linea in open(path, encoding='utf-8-sig'):
        linea = linea.strip()
        if not linea or linea.startswith('#'):
            continue
        m = ID_RE.match(linea)
        pid, texto = (m.group(1), m.group(2).strip()) if m else (f'p{len(frases) + 1:02d}', linea)
        frases.append((pid, texto))
    if not frases:
        die(f'guion vacío: {path}')
    ids = [p for p, _ in frases]
    if len(set(ids)) != len(ids):
        die('hay ids de frase repetidos en el guion')
    return frases


def leer_equiv(path: str | None) -> list[tuple[str, str]]:
    if not path:
        return []
    try:
        d = json.load(open(path, encoding='utf-8'))
    except (OSError, ValueError) as e:
        die(f'--equiv no es un JSON legible: {e}')
    if not isinstance(d, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in d.items()):
        die('--equiv debe ser un objeto {"patrón": "reemplazo"}')
    for k in d:
        if re.search(r'[\x00-\x1f]', k):
            die(f'--equiv: el patrón {k!r} tiene un carácter de control; en JSON la barra de las regex va doble ("\\\\b2026\\\\b")')
        try:
            re.compile(k)
        except re.error as e:
            die(f'--equiv: patrón inválido {k!r}: {e}')
    return list(d.items())


def sin_etiquetas(texto: str) -> str:
    return re.sub(r'\s+', ' ', TAG_RE.sub(' ', texto)).strip()


def tokens(texto: str, equiv: list[tuple[str, str]]) -> list[str]:
    t = ''.join(c for c in unicodedata.normalize('NFD', texto.lower()) if unicodedata.category(c) != 'Mn')
    for pat, rep in equiv:
        t = re.sub(pat, rep, t)
    return re.findall(r'\w+', t)


def avisos_texto(texto: str) -> list[str]:
    """Rasgos del texto hablado que han dado problemas con las voces de ElevenLabs."""
    out = []
    limpio = sin_etiquetas(texto)
    if re.search(r'\d', limpio):
        out.append('Hay cifras: la voz decide cómo leerlas. Si importa la lectura, escríbelas en palabras en el texto '
                   'etiquetado (en pantalla pueden seguir en cifras) y declara la equivalencia en --equiv.')
    mayus = sorted({w for w in re.findall(r'\b[A-ZÁÉÍÓÚÑ]{2,}\b', limpio)})
    if mayus:
        out.append(f'Palabras en mayúsculas ({", ".join(mayus[:8])}): pueden deletrearse o sonar forzadas.')
    if '...' in limpio or '…' in limpio:
        out.append('Puntos suspensivos: producen pausas irregulares y suenan a duda.')
    if re.search(r'\bapps?\b', limpio, re.I):
        out.append('«app» se ha oído como «AP»: mejor «aplicación».')
    if re.search(r'<break', texto, re.I) and re.search(r'\[[^\]]*\]', texto):
        out.append('Mezcla <break …/> (Multilingual v2) con etiquetas entre corchetes (modelos con etiquetas): usa un solo marcado.')
    return out


def cmd_guion(a) -> None:
    frases = leer_guion(a.guion)
    equiv = leer_equiv(a.equiv)
    canon = ' '.join(t for _, t in frases)
    palabras = canon.split()
    print(f'guion canónico: {len(frases)} frases · {len(palabras)} palabras · {len(canon)} caracteres')
    print('duración estimada del habla: ' + ' · '.join(f'{len(canon) / r:.1f} s a {r:g} car/s' for r in (16.0, 14.5, 13.0)))
    hablado = canon
    ok = True
    if a.etiquetado:
        if not os.path.isfile(a.etiquetado):
            die(f'no existe el texto etiquetado: {a.etiquetado}')
        etiq = open(a.etiquetado, encoding='utf-8-sig').read()
        etiquetas = TAG_RE.findall(etiq)
        hablado = sin_etiquetas(etiq)
        print(f'texto etiquetado: {len(etiq.strip())} caracteres pegados (con etiquetas; el gasto real se ve en la web) · '
              f'{len(etiquetas)} etiquetas: {", ".join(sorted(set(etiquetas))) or "ninguna"}')
        ca, cb = tokens(canon, equiv), tokens(hablado, equiv)
        if ca == cb:
            print('OK     sin etiquetas, el texto etiquetado dice lo mismo que el guion canónico')
        else:
            ok = False
            print('NO     el texto etiquetado no coincide con el guion canónico (sin contar etiquetas ni puntuación):')
            sm = difflib.SequenceMatcher(a=ca, b=cb, autojunk=False)
            for op, i1, i2, j1, j2 in [o for o in sm.get_opcodes() if o[0] != 'equal'][:12]:
                print(f'       {op}: guion «{" ".join(ca[i1:i2])}» / etiquetado «{" ".join(cb[j1:j2])}»')
            print('       Corrige uno de los dos o declara la equivalencia en --equiv (p. ej. cifras escritas en palabras).')
    for aviso in avisos_texto(a.etiquetado and open(a.etiquetado, encoding='utf-8-sig').read() or canon):
        print('AVISO  ' + aviso)
    sys.exit(0 if ok else 1)


# ---------- proyecto y audio ----------
def proyecto(slug: str, project_dir: str | None) -> str:
    if not SLUG_RE.match(slug or ''):
        die(f'slug inválido: {slug!r}')
    if not project_dir:
        die('indica --project-dir con la carpeta del proyecto (debe tener video.json)')
    p = os.path.abspath(project_dir)
    if not os.path.isfile(os.path.join(p, 'video.json')):
        die(f'no existe video.json en {p}')
    return p


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def meta_nombre(nombre: str) -> dict | None:
    """Lo que el nombre del archivo descargado de ElevenLabs dice de la toma (no se verifica contra la cuenta)."""
    m = NOMBRE_RE.match(os.path.splitext(nombre)[0])
    if not m:
        return None
    r = RESTO_RE.match(m.group('resto'))
    d = {'fecha': m.group('fecha').replace('_', ':'), 'voz': r.group('voz').strip()}
    if r.group('tipo'):
        d['tipo_voz'] = r.group('tipo')
    if r.group('s'):
        d['estabilidad'] = int(r.group('s')) / 100
    if r.group('sim'):
        d['similitud'] = int(r.group('sim')) / 100
    if r.group('v'):
        d['version_en_nombre'] = r.group('v')
    return d


def sonda(path: str) -> dict:
    r = run([FFPROBE, '-v', 'error', '-select_streams', 'a:0', '-show_entries',
             'stream=codec_name,sample_rate,channels:format=duration', '-of', 'json', path])
    d = json.loads(r.stdout)
    s = d['streams'][0] if d.get('streams') else {}
    return {'codec': s.get('codec_name'), 'sample_rate': int(s.get('sample_rate') or 0),
            'canales': s.get('channels'), 'duracion': round(float(d.get('format', {}).get('duration') or 0), 3)}


def sonoridad(path: str) -> dict:
    r = run([FFMPEG, '-hide_banner', '-nostats', '-i', path, '-map', '0:a:0', '-af', 'ebur128=peak=true', '-f', 'null', '-'])
    tail = r.stderr[r.stderr.rfind('Summary:'):]
    i = re.search(r'I:\s+(-?[\d.]+) LUFS', tail)
    p = re.search(r'Peak:\s+(-?[\d.]+) dBFS', tail)
    return {'lufs': float(i.group(1)) if i else None, 'pico_real_dbtp': float(p.group(1)) if p else None}


def decodificar(path: str):
    import numpy as np
    r = run([FFMPEG, '-v', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], binario=True)
    return np.frombuffer(r.stdout, dtype='<i2').astype(np.float32) / 32768.0


def niveles(x):
    """Nivel RMS en dBFS por ventana de 10 ms."""
    import numpy as np
    n = int(HOP * SR)
    fr = x[: len(x) // n * n].reshape(-1, n)
    return 20 * np.log10(np.sqrt((fr.astype(np.float64) ** 2).mean(axis=1)) + 1e-9)


def silencios(lv, umbral: float, minimo: float = 0.12) -> list[tuple[float, float]]:
    import numpy as np
    bajo = lv < umbral
    out, ini = [], None
    for i, q in enumerate(np.append(bajo, False)):
        if q and ini is None:
            ini = i
        elif not q and ini is not None:
            if (i - ini) * HOP >= minimo:
                out.append((round(ini * HOP, 3), round(i * HOP, 3)))
            ini = None
    return out


# ---------- ASR ----------
def etiqueta_modelo(modelo: str) -> str:
    """Nombre legible del modelo: la carpeta models--… de una caché de Hugging Face, o el archivo/carpeta."""
    partes = os.path.normpath(modelo).split(os.sep)
    hf = [p for p in partes if p.startswith('models--')]
    return hf[-1].split('--', 2)[-1] if hf else partes[-1]


def asr_faster(x, modelo: str) -> list[dict]:
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        die('este Python no tiene faster-whisper: usa el entorno que lo tenga o --motor whisper-cpp')
    m = WhisperModel(modelo, device='cpu', compute_type='int8')
    segs, _ = m.transcribe(x, language='es', beam_size=5, temperature=0, word_timestamps=True,
                           condition_on_previous_text=False, vad_filter=False)
    return [{'w': p.word.strip(), 's': round(p.start, 3), 'e': round(p.end, 3), 'p': round(p.probability, 3)}
            for s in segs for p in s.words if p.word.strip()]


def asr_whispercpp(x, modelo: str, w: str) -> list[dict]:
    import numpy as np
    wav = os.path.join(w, 'externa-16k.wav')
    pcm = (np.clip(x, -1, 1) * 32767).astype('<i2').tobytes()
    p = subprocess.run([FFMPEG, '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-',
                        '-c:a', 'pcm_s16le', wav], input=pcm, capture_output=True)
    if p.returncode:
        die('falló ffmpeg al escribir el WAV de 16 kHz')
    base = os.path.join(w, 'externa-whisper')
    run(['whisper-cli', '-m', modelo, '-l', 'es', '-f', wav, '-oj', '-ojf', '-ml', '42', '-sow', '-t', '8', '-of', base])
    d = json.load(open(base + '.json', encoding='utf-8'))
    words = []
    for seg in d['transcription']:
        for t in seg['tokens']:
            tx = t['text']
            if tx.startswith('[_') or (not tx.strip() and not words):
                continue
            if tx.startswith(' ') or not words:
                words.append([tx.strip(), t['offsets']['from'], t['offsets']['to']])
            else:
                words[-1][0] += tx
                words[-1][2] = t['offsets']['to']
    return [{'w': a, 's': b / 1000, 'e': c / 1000} for a, b, c in words if a]


# ---------- alineación ----------
def alinear(palabras: list[str], asr: list[dict], equiv) -> tuple[list, list, float, int]:
    """Cada palabra del guion toma los tiempos de la palabra que el ASR oyó igual; el resto se reparte."""
    ct, cm = [], []
    for i, w in enumerate(palabras):
        for t in tokens(w, equiv):
            ct.append(t)
            cm.append(i)
    at, am = [], []
    for j, x in enumerate(asr):
        for t in tokens(x['w'], equiv):
            at.append(t)
            am.append(j)
    tiempos: list = [None] * len(palabras)
    directas = set()
    sm = difflib.SequenceMatcher(a=ct, b=at, autojunk=False)
    difs = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal':
            for k in range(i2 - i1):
                ci, x = cm[i1 + k], asr[am[j1 + k]]
                tiempos[ci] = (min(tiempos[ci][0], x['s']), max(tiempos[ci][1], x['e'])) if tiempos[ci] else (x['s'], x['e'])
                directas.add(ci)
            continue
        difs.append({'op': {'replace': 'cambio', 'delete': 'no oída', 'insert': 'añadida'}[op],
                     'guion': ' '.join(ct[i1:i2]), 'oido': ' '.join(at[j1:j2]),
                     't': asr[am[j1]]['s'] if j2 > j1 else None})
        if op == 'replace':
            js = sorted({am[j] for j in range(j1, j2)})
            s, e = asr[js[0]]['s'], asr[js[-1]]['e']
            cis = sorted({cm[i] for i in range(i1, i2)})
            lens = [len(palabras[c]) for c in cis]
            acc = s
            for c, n in zip(cis, lens):
                d = (e - s) * n / sum(lens)
                tiempos[c] = (acc, acc + d) if tiempos[c] is None else (min(tiempos[c][0], acc), max(tiempos[c][1], acc + d))
                acc += d
    i = 0
    while i < len(tiempos):  # palabras que el ASR no oyó: entre sus vecinas, por longitud
        if tiempos[i] is not None:
            i += 1
            continue
        j = i
        while j < len(tiempos) and tiempos[j] is None:
            j += 1
        e = tiempos[j][0] if j < len(tiempos) else (tiempos[i - 1][1] if i else 0.0) + 0.4 * (j - i)
        s = tiempos[i - 1][1] if i else max(0.0, e - 0.4 * (j - i))
        lens = [len(palabras[k]) for k in range(i, j)]
        acc = s
        for k, n in zip(range(i, j), lens):
            d = (e - s) * n / sum(lens)
            tiempos[k] = (acc, acc + d)
            acc += d
        i = j
    return tiempos, difs, sm.ratio(), len(directas)


def ajustar_a_silencios(tiempos: list, sil: list, lv, umbral: float) -> int:
    """Whisper suele pegar una pausa a la palabra vecina: el silencio más largo entre dos palabras fija su frontera.
    La primera palabra empieza donde el nivel supera el umbral y la última acaba donde deja de superarlo."""
    import numpy as np
    n = 0
    for k in range(len(tiempos) - 1):
        (s0, e0), (s1, e1) = tiempos[k], tiempos[k + 1]
        dentro = [(a, b) for a, b in sil if a > s0 + 0.05 and b < e1 - 0.03]
        if not dentro:
            continue
        a, b = max(dentro, key=lambda z: z[1] - z[0])
        tiempos[k] = (s0, a)
        tiempos[k + 1] = (b, max(e1, b + 0.03))
        n += 1
    alto = np.where(lv >= umbral)[0]
    if len(alto):
        ini, fin = alto[0] * HOP, (alto[-1] + 1) * HOP
        if ini < tiempos[0][1] - 0.03:
            tiempos[0] = (round(ini, 3), tiempos[0][1])
        if fin > tiempos[-1][0] + 0.03:
            tiempos[-1] = (tiempos[-1][0], round(fin, 3))
    for k in range(1, len(tiempos)):  # monotonía sin solapes
        s, e = tiempos[k]
        s = max(s, tiempos[k - 1][0] + 0.01)
        if s < tiempos[k - 1][1]:
            tiempos[k - 1] = (tiempos[k - 1][0], s)
        tiempos[k] = (s, max(e, s + 0.03))
    return n


def vocabulario_etiquetas(path: str | None) -> set[str]:
    voc = {'pausa', 'pause', 'short', 'long', 'break'}
    if path and os.path.isfile(path):
        for tag in TAG_RE.findall(open(path, encoding='utf-8-sig').read()):
            if tag.startswith('['):
                voc.update(tokens(tag, []))
    return voc


def cmd_importar(a) -> None:
    p = proyecto(a.slug, a.project_dir)
    w = os.path.join(p, '.work', 'voz')
    os.makedirs(w, exist_ok=True)
    src = os.path.abspath(a.audio)
    if not os.path.isfile(src):
        die(f'no existe el audio: {src}')
    if not a.modelo or not os.path.exists(os.path.expanduser(a.modelo)):
        die(f'falta el modelo local de transcripción (--modelo): {a.modelo}')
    modelo = os.path.expanduser(a.modelo)
    frases = leer_guion(a.guion)
    equiv = leer_equiv(a.equiv)

    ext = os.path.splitext(src)[1].lower() or '.mp3'
    copia = os.path.join(w, '00-externa' + ext)
    h = sha256(src)
    previas = [f for f in os.listdir(w) if f.startswith('00-externa.') and f != '00-externa.json']
    for f in previas:
        if sha256(os.path.join(w, f)) != h and not a.reemplazar:
            die(f'ya hay otra locución importada ({f}); usa --reemplazar o una carpeta de proyecto nueva')
    for f in previas:
        if os.path.join(w, f) != copia:
            os.remove(os.path.join(w, f))
    if not os.path.isfile(copia) or sha256(copia) != h:
        shutil.copy2(src, copia)
    info = sonda(copia)
    son = sonoridad(copia)
    meta = {'archivo_original': os.path.basename(src), 'copia': os.path.basename(copia), 'sha256': h,
            'segun_nombre': meta_nombre(os.path.basename(src)), **info, 'sonoridad_original': son,
            'fuente': 'elevenlabs-web', 'audio_modificado': False}
    json.dump(meta, open(os.path.join(w, '00-externa.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    x = decodificar(copia)
    dur = len(x) / SR
    cache = os.path.join(w, 'externa-asr.json')
    clave = {'sha256': h, 'motor': a.motor, 'modelo': etiqueta_modelo(modelo)}
    asr = None
    if os.path.isfile(cache) and not a.rehacer_asr:
        c = json.load(open(cache, encoding='utf-8'))
        if c.get('clave') == clave:
            asr = c['palabras']
            print('ASR    caché (externa-asr.json)')
    if asr is None:
        print(f'ASR    {a.motor} · {clave["modelo"]} · {dur:.1f} s de audio…', flush=True)
        asr = asr_faster(x, modelo) if a.motor == 'faster-whisper' else asr_whispercpp(x, modelo, w)
        json.dump({'clave': clave, 'palabras': asr}, open(cache, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if not asr:
        die('el ASR no devolvió palabras: revisa el audio y el modelo')

    palabras, de_frase = [], []
    for fi, (_, texto) in enumerate(frases):
        for wd in texto.split():
            palabras.append(wd)
            de_frase.append(fi)
    tiempos, difs, ratio, directas = alinear(palabras, asr, equiv)
    lv = niveles(x)
    ajustes = ajustar_a_silencios(tiempos, silencios(lv, a.umbral), lv, a.umbral)

    out, k = [], 0
    for fi, (pid, texto) in enumerate(frases):
        ws = []
        while k < len(palabras) and de_frase[k] == fi:
            ws.append({'w': palabras[k], 's': round(tiempos[k][0], 3), 'e': round(tiempos[k][1], 3)})
            k += 1
        out.append({'id': pid, 'texto': texto, 's': ws[0]['s'], 'e': ws[-1]['e'], 'palabras': ws})
    voc = vocabulario_etiquetas(a.etiquetado)
    leidas = [d for d in difs if d['oido'] and set(d['oido'].split()) & voc]
    huecos = []
    planas = [(f['id'], wd) for f in out for wd in f['palabras']]
    for (pa, wa), (pb, wb) in zip(planas, planas[1:]):
        g = wb['s'] - wa['e']
        if g >= PAUSA_INFORME:
            huecos.append({'tras': wa['w'], 'antes_de': wb['w'], 'frase': pa if pa == pb else f'{pa}→{pb}',
                           's': wa['e'], 'dur': round(g, 3)})
    canon = ' '.join(t for _, t in frases)
    habla = (out[-1]['e'] - out[0]['s']) or 1e-9
    res = {'fuente': meta['archivo_original'], 'sha256': h, 'duracion': round(dur, 3), 'habla': [out[0]['s'], out[-1]['e']],
           'car_s': round(len(canon) / habla, 2), 'coincidencia_asr': round(ratio, 4),
           'palabras_con_tiempo_del_asr': directas, 'palabras': len(palabras), 'fronteras_ajustadas_a_silencio': ajustes,
           'diferencias_asr': difs, 'etiquetas_leidas': leidas, 'pausas': huecos, 'frases': out,
           'metodo': f'{a.motor} (tiempos por palabra) + emparejamiento con el guion canónico + fronteras en silencios < {a.umbral:g} dBFS'}
    json.dump(res, open(os.path.join(w, 'externa-palabras.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    informe(w, meta, res, frases)

    print(f'OK     {len(frases)} frases · {len(palabras)} palabras · habla {out[0]["s"]:.2f}–{out[-1]["e"]:.2f} s de {dur:.2f} s · '
          f'{res["car_s"]:.1f} car/s')
    print(f'       {directas}/{len(palabras)} palabras con tiempo directo del ASR (coincidencia {ratio:.1%}) · '
          f'{ajustes} fronteras ajustadas a silencios')
    for d in difs[:15]:
        print(f'REVISA {d["op"]}: guion «{d["guion"]}» / oído «{d["oido"]}»' + (f' ({d["t"]:.2f} s)' if d['t'] is not None else ''))
    if len(difs) > 15:
        print(f'       … {len(difs) - 15} diferencias más en EXTERNA.md')
    for d in leidas:
        print(f'REVISA posible etiqueta leída en voz alta: «{d["oido"]}» ({d["t"]:.2f} s)')
    print(f'informe: {os.path.join(w, "EXTERNA.md")}')
    print(f'siguiente: escucha el original y revisa las diferencias; luego `externa.py entregar {a.slug} --project-dir …`')


def informe(w: str, meta: dict, res: dict, frases) -> None:
    sn = meta.get('segun_nombre') or {}
    L = ['# Locución externa', '',
         f'Archivo: `{meta["archivo_original"]}` · {meta["codec"]} {meta["sample_rate"]} Hz, {meta["canales"]} canal(es) · '
         f'{res["duracion"]:.2f} s · SHA256 `{meta["sha256"][:16]}…`', '']
    if sn:
        L.append('Según el nombre del archivo (no verificado contra la cuenta): ' +
                 ', '.join(f'{k} {v}' for k, v in sn.items()) + '.')
        L.append('')
    so = meta['sonoridad_original']
    L += [f'Sonoridad del original: {so["lufs"]} LUFS, pico real {so["pico_real_dbtp"]} dBTP. Al importar no se modifica el audio.', '',
          f'Habla: {res["habla"][0]:.2f}–{res["habla"][1]:.2f} s · {res["car_s"]:.1f} car/s (pausas incluidas) · '
          f'{res["palabras_con_tiempo_del_asr"]}/{res["palabras"]} palabras con tiempo directo del ASR · '
          f'coincidencia {res["coincidencia_asr"]:.1%} · {res["fronteras_ajustadas_a_silencio"]} fronteras ajustadas a silencios.', '',
          f'Método: {res["metodo"]}. No es alineación fonética: junto a una pausa la frontera es fiable; en habla continua '
          'Whisper suele adelantar las palabras (medido con faster-whisper small: mediana ≈ 70 ms, p90 ≈ 200 ms). Basta para '
          'subtítulos y cortes de plano; verifica a mano las anclas de tipografía palabra a palabra o de golpes sonoros. '
          'Esta herramienta no escucha: la escucha del original sigue pendiente.', '',
          '## Diferencias entre el guion y lo que oyó el ASR', '']
    if res['diferencias_asr']:
        L += ['| Tipo | Guion | Oído | s |', '|---|---|---|---|']
        L += [f'| {d["op"]} | {d["guion"]} | {d["oido"]} | {"" if d["t"] is None else f"{d['t']:.2f}"} |' for d in res['diferencias_asr']]
        L += ['', 'Suelen ser errores de reconocimiento (cifras, nombres propios). Una palabra «añadida» puede ser una etiqueta '
              'leída en voz alta o un sonido espurio en una pausa: escucha ese tramo.']
    else:
        L.append('Ninguna.')
    L += ['', '## Pausas entre palabras (≥ 0.30 s)', '', '| Tras | Antes de | Frase | s | Dura |', '|---|---|---|---|---|']
    L += [f'| {h["tras"]} | {h["antes_de"]} | {h["frase"]} | {h["s"]:.2f} | {h["dur"]:.2f} |' for h in res['pausas']]
    L += ['', '## Frases', '', '| Id | Inicio | Fin | car/s | Texto |', '|---|---|---|---|---|']
    for f in res['frases']:
        d = max(f['e'] - f['s'], 1e-9)
        L.append(f'| {f["id"]} | {f["s"]:.2f} | {f["e"]:.2f} | {len(f["texto"]) / d:.1f} | {f["texto"]} |')
    open(os.path.join(w, 'EXTERNA.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')


# ---------- entrega ----------
def cmd_entregar(a) -> None:
    p = proyecto(a.slug, a.project_dir)
    w = os.path.join(p, '.work', 'voz')
    pal = os.path.join(w, 'externa-palabras.json')
    copias = [f for f in os.listdir(w) if f.startswith('00-externa.') and f != '00-externa.json'] if os.path.isdir(w) else []
    if not os.path.isfile(pal) or not copias:
        die('falta importar la locución: corre antes `externa.py importar`')
    res = json.load(open(pal, encoding='utf-8'))
    src = os.path.join(w, copias[0])
    if sha256(src) != res['sha256']:
        die('la locución importada cambió después de alinear: vuelve a correr importar')
    nombre = a.nombre or f'voz-{a.slug}'
    wav = os.path.join(p, 'public', nombre + '.wav')
    pjs = os.path.join(p, 'src', nombre + '.palabras.json')
    fjs = os.path.join(p, 'src', nombre + '.frases.json')
    for f in (wav, pjs, fjs):
        if os.path.exists(f) and not a.reemplazar:
            die(f'ya existe {f}; usa --reemplazar para sobrescribirlo')
    os.makedirs(os.path.dirname(wav), exist_ok=True)
    os.makedirs(os.path.dirname(pjs), exist_ok=True)
    sr = sonda(src)['sample_rate'] or 44100
    af = []
    if a.normalizar:  # ganancia global en dos pasadas (lineal): no cambia ritmo, pausas ni dinámica interna
        r = run([FFMPEG, '-hide_banner', '-nostats', '-i', src, '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'])
        m = json.loads(r.stderr[r.stderr.rfind('{'):r.stderr.rfind('}') + 1])
        af = ['-af', (f'loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={m["input_i"]}:measured_TP={m["input_tp"]}:'
                      f'measured_LRA={m["input_lra"]}:measured_thresh={m["input_thresh"]}:offset={m["target_offset"]}:linear=true')]
    run([FFMPEG, '-hide_banner', '-nostdin', '-y', '-i', src, *af, '-ar', str(sr), '-c:a', 'pcm_s16le', wav])
    plano = [{'text': wd['w'], 'startMs': int(round(wd['s'] * 1000)), 'endMs': int(round(wd['e'] * 1000))}
             for f in res['frases'] for wd in f['palabras']]
    json.dump(plano, open(pjs, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump({'fuente': res['fuente'], 'sha256': res['sha256'], 'duracion': res['duracion'], 'normalizada': bool(a.normalizar),
               'tiempos': 'segundos desde el inicio del archivo; la composición suma su propio desfase de entrada',
               'frases': res['frases']}, open(fjs, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    so = sonoridad(wav)
    print(f'escrito {wav} ({"ganancia global a −16 LUFS" if a.normalizar else "sin procesar"}: {so["lufs"]} LUFS, '
          f'pico real {so["pico_real_dbtp"]} dBTP)')
    print(f'escrito {pjs} ({len(plano)} palabras, mismo formato que voz-whisper)')
    print(f'escrito {fjs} ({len(res["frases"])} frases con id)')
    print('Los tiempos cuentan desde el inicio del archivo: si la voz entra tras una cortinilla, súmale ese desfase en la composición.')


def main() -> None:
    ap = argparse.ArgumentParser(prog='externa.py', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    g = sub.add_parser('guion', help='comprueba el guion canónico y el texto etiquetado antes de generar en la web')
    g.add_argument('--guion', required=True)
    g.add_argument('--etiquetado')
    g.add_argument('--equiv')
    i = sub.add_parser('importar', help='copia la locución descargada y calcula sus tiempos por palabra')
    i.add_argument('slug')
    i.add_argument('--project-dir', required=True)
    i.add_argument('--audio', required=True, help='MP3/WAV descargado de ElevenLabs (no se modifica)')
    i.add_argument('--guion', required=True)
    i.add_argument('--modelo', required=True, help='modelo local: carpeta de faster-whisper o .bin GGML de whisper.cpp')
    i.add_argument('--motor', choices=['faster-whisper', 'whisper-cpp'], default='faster-whisper')
    i.add_argument('--etiquetado', help='texto pegado en la web (para buscar etiquetas leídas en voz alta)')
    i.add_argument('--equiv')
    i.add_argument('--umbral', type=float, default=-45.0, help='dBFS bajo los que hay silencio (default -45)')
    i.add_argument('--reemplazar', action='store_true', help='permite sustituir otra locución ya importada')
    i.add_argument('--rehacer-asr', action='store_true', help='ignora la caché de transcripción')
    e = sub.add_parser('entregar', help='copia la voz a public/ y los tiempos a src/')
    e.add_argument('slug')
    e.add_argument('--project-dir', required=True)
    e.add_argument('--nombre', help='base de los archivos (default voz-<slug>)')
    e.add_argument('--normalizar', action='store_true', help='ganancia global en dos pasadas a −16 LUFS / −1.5 dBTP')
    e.add_argument('--reemplazar', action='store_true')
    a = ap.parse_args()
    {'guion': cmd_guion, 'importar': cmd_importar, 'entregar': cmd_entregar}[a.cmd](a)


if __name__ == '__main__':
    main()
