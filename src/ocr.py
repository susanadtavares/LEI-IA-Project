# ocr.py
# Reconhecimento de matrículas Portuguesas via OCR (EasyOCR)

import re
import os

try:
    import easyocr
    _EASYOCR_AVAILABLE = True
except ImportError:
    _EASYOCR_AVAILABLE = False

# Padrões de matrícula Portuguesa:
#   Novo formato (desde 2005):  XX-00-XX  (letras-números-letras)
#   Formato intermédio:         00-XX-00  (números-letras-números)
#   Formato antigo:             00-00-XX  (números-números-letras)
_PLATE_PATTERNS = [
    re.compile(r'\b[A-Z]{2}[-\s]?\d{2}[-\s]?[A-Z]{2}\b', re.IGNORECASE),  # AA-00-AA
    re.compile(r'\b\d{2}[-\s]?[A-Z]{2}[-\s]?\d{2}\b',    re.IGNORECASE),  # 00-AA-00
    re.compile(r'\b\d{2}[-\s]?\d{2}[-\s]?[A-Z]{2}\b',    re.IGNORECASE),  # 00-00-AA
]

_reader = None  # instância reutilizável


def _get_reader():
    global _reader
    if _reader is None:
        print("  A carregar modelo OCR (primeira vez pode demorar)...")
        _reader = easyocr.Reader(['pt', 'en'], gpu=False)
    return _reader


def _normalise_plate(text: str) -> str:
    """Normaliza uma matrícula para o formato XX-00-XX."""
    clean = re.sub(r'[-\s]', '', text).upper()
    if len(clean) == 6:
        return f"{clean[0:2]}-{clean[2:4]}-{clean[4:6]}"
    return clean


def read_plate_from_image(image_path: str) -> str | None:
    """
    Lê uma imagem e tenta extrair uma matrícula Portuguesa.

    Parâmetros:
        image_path: caminho absoluto ou relativo para a imagem.

    Retorna:
        Matrícula formatada (ex: "AB-12-CD") ou None se não encontrada.
    """
    if not _EASYOCR_AVAILABLE:
        raise ImportError(
            "EasyOCR não está instalado. Execute: pip install easyocr"
        )

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Imagem não encontrada: {image_path}")

    reader = _get_reader()
    results = reader.readtext(image_path)

    # Ordenar por confiança (descendente) e tentar reconhecer padrão
    results.sort(key=lambda r: r[2], reverse=True)

    candidates = []
    for _, text, confidence in results:
        if confidence < 0.2:
            continue
        for pattern in _PLATE_PATTERNS:
            match = pattern.search(text)
            if match:
                candidates.append((confidence, _normalise_plate(match.group())))

    if candidates:
        candidates.sort(key=lambda c: c[0], reverse=True)
        return candidates[0][1]

    # Fallback: concatenar todo o texto reconhecido e tentar novamente
    full_text = ' '.join(t for _, t, _ in results)
    for pattern in _PLATE_PATTERNS:
        match = pattern.search(full_text)
        if match:
            return _normalise_plate(match.group())

    return None
