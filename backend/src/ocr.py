# =============================================================================
# ocr.py
# =============================================================================
# Módulo de reconhecimento óptico de carateres (OCR) para leitura de matrículas
# de veículos Portugueses a partir de imagens.
#
# Utiliza a biblioteca EasyOCR (https://github.com/JaidedAI/EasyOCR) que corre
# localmente sem necessidade de API externa.
#
# Formatos de matrícula suportados (Portugal):
#   AA-00-AA  — novo formato (desde 2005), ex: AB-12-CD
#   00-AA-00  — formato intermédio (1992–2005), ex: 12-AB-34
#   00-00-AA  — formato antigo (antes de 1992), ex: 12-34-AB
#
# Função pública principal:
#   read_plate_from_image(image_path) -> str | None
# =============================================================================

import re
import os

try:
    import numpy as np
    from PIL import Image, ImageEnhance, ImageOps
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False

# Tentativa de importar o EasyOCR. Se não estiver instalado, a flag
# _EASYOCR_AVAILABLE fica False e read_plate_from_image lança ImportError
# com instruções de instalação em vez de um erro genérico.
try:
    import easyocr
    _EASYOCR_AVAILABLE = True
except ImportError:
    _EASYOCR_AVAILABLE = False

# -----------------------------------------------------------------------------
# Expressões regulares para detetar patrões de matrícula Portuguesa
# -----------------------------------------------------------------------------
# re.IGNORECASE: aceita letras maiúsculas e minúsculas (OCR pode gerar ambas).
# [-\s]? : o separador pode ser '-', espaço, ou estar ausente (OCR inconsistente).
# \b     : word boundary — evita falsos positivos dentro de palavras maiores.
_PLATE_PATTERNS = [
    re.compile(r'\b[A-Z]{2}[-\s]?\d{2}[-\s]?[A-Z]{2}\b', re.IGNORECASE),  # AA-00-AA (novo)
    re.compile(r'\b\d{2}[-\s]?[A-Z]{2}[-\s]?\d{2}\b',    re.IGNORECASE),  # 00-AA-00 (intermédio)
    re.compile(r'\b\d{2}[-\s]?\d{2}[-\s]?[A-Z]{2}\b',    re.IGNORECASE),  # 00-00-AA (antigo)
]

_PLATE_PATTERNS_CLEAN = [
    re.compile(r'^[A-Z]{2}\d{2}[A-Z]{2}$'),
    re.compile(r'^\d{2}[A-Z]{2}\d{2}$'),
    re.compile(r'^\d{4}[A-Z]{2}$'),
]

_LETTER_TO_DIGIT = {
    'O': '0', 'Q': '0',
    'I': '1', 'L': '1',
    'Z': '2',
    'S': '5',
    'G': '6',
    'B': '8',
}

_DIGIT_TO_LETTER = {
    '0': 'O',
    '1': 'I',
    '2': 'Z',
    '5': 'S',
    '6': 'G',
    '8': 'B',
}

# Instância do leitor EasyOCR reutilizável entre chamadas.
# Criá-la é lento (carrega modelos de rede neuronal), por isso é feito
# apenas uma vez e guardado nesta variável global.
_reader = None


def _get_reader():
    """
    Devolve a instância do leitor EasyOCR, criando-a na primeira chamada.
    Padrão Singleton: garante que o modelo é carregado apenas uma vez.
    """
    global _reader
    if _reader is None:
        print("  A carregar modelo OCR (primeira vez pode demorar)...")
        # ['pt', 'en']: suporte para português e inglês
        # gpu=False    : usa CPU (compatível com máquinas sem GPU dedicada)
        _reader = easyocr.Reader(['pt', 'en'], gpu=False)
    return _reader


def _normalise_plate(text: str) -> str:
    """
    Normaliza o texto de uma matrícula para o formato canónico XX-YY-ZZ.
    Remove separadores existentes, converte para maiúsculas e reinsere
    hífenes fixos de 2 em 2 carateres.

    Exemplo: 'ab 12cd' -> 'AB-12-CD'
    """
    clean = re.sub(r'[-\s]', '', text).upper()
    if len(clean) == 6:
        # Inserir hífenes nas posições corretas: posições 2 e 4
        return f"{clean[0:2]}-{clean[2:4]}-{clean[4:6]}"
    return clean  # fallback: devolver sem formatação se comprimento inesperado


def _preprocess_image_variants(image_path: str):
    """
    Cria variantes da imagem para aumentar a robustez do OCR em matrículas
    pequenas, com baixo contraste ou iluminação irregular.
    """
    if not _PIL_AVAILABLE:
        return [image_path]

    try:
        image = Image.open(image_path).convert('L')
    except Exception:
        return [image_path]

    # Variante 1: ampliação + equalização para melhorar legibilidade.
    enlarged = image.resize((image.width * 2, image.height * 2))
    equalized = ImageOps.equalize(enlarged)

    # Variante 2: reforço de contraste para destacar caracteres.
    contrasted = ImageEnhance.Contrast(equalized).enhance(2.2)

    return [
        image_path,
        np.array(equalized),
        np.array(contrasted),
    ]


def _plate_candidates_from_token(token: str) -> list[str]:
    """
    Gera candidatos de matrícula corrigindo confusões comuns do OCR
    (ex.: O/0, I/1, S/5), respeitando os formatos portugueses suportados.
    """
    cleaned = re.sub(r'[^A-Z0-9]', '', token.upper())
    if len(cleaned) != 6:
        return []

    templates = (
        'LLDDLL',  # AA00AA
        'DDLLDD',  # 00AA00
        'DDDDLL',  # 0000AA
    )

    candidates = set()
    for template in templates:
        chars = []
        valid = True
        for char, expected in zip(cleaned, template):
            if expected == 'L':
                if char.isalpha():
                    chars.append(char)
                elif char in _DIGIT_TO_LETTER:
                    chars.append(_DIGIT_TO_LETTER[char])
                else:
                    valid = False
                    break
            else:
                if char.isdigit():
                    chars.append(char)
                elif char in _LETTER_TO_DIGIT:
                    chars.append(_LETTER_TO_DIGIT[char])
                else:
                    valid = False
                    break
        if valid:
            candidates.add(''.join(chars))

    return sorted(candidates)


def _extract_plate_candidate(text: str) -> str | None:
    """
    Procura uma matrícula num texto OCR, incluindo correções de ambiguidades.
    """
    for pattern in _PLATE_PATTERNS:
        match = pattern.search(text)
        if match:
            return _normalise_plate(match.group())

    for token in re.findall(r'[A-Z0-9\-\s]{4,12}', text.upper()):
        for candidate in _plate_candidates_from_token(token):
            if any(pattern.match(candidate) for pattern in _PLATE_PATTERNS_CLEAN):
                return _normalise_plate(candidate)

    return None


def read_plate_from_image(image_path: str) -> str | None:
    """
    Lê uma imagem e tenta extrair uma matrícula Portuguesa.

    Processo:
        1. Executar OCR sobre a imagem (EasyOCR devolve regiões de texto
           com posição, texto reconhecido e nível de confiança).
        2. Para cada região, tentar detetar um padrão de matrícula válido,
           guardando candidatos ordenados por confiança.
        3. Se não encontrar nenhum candidato individualmente, concatenar
           todo o texto e tentar novamente (fallback).

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
    results = []
    for image_input in _preprocess_image_variants(image_path):
        # Allowlist limita caracteres ao domínio esperado de matrículas.
        results.extend(
            reader.readtext(
                image_input,
                allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789- ',
            )
        )

    # Ordenar resultados por confiança descendente: o OCR está mais seguro
    # das regiões com confiança mais alta — processamos essas primeiro.
    results.sort(key=lambda r: r[2], reverse=True)

    candidates = []
    for _, text, confidence in results:
        if confidence < 0.15:  # pequena tolerância para imagens mais difíceis
            continue
        candidate = _extract_plate_candidate(text)
        if candidate:
            candidates.append((confidence, candidate))

    if candidates:
        # Devolver a matrícula com maior confiança de reconhecimento
        candidates.sort(key=lambda c: c[0], reverse=True)
        return candidates[0][1]

    # Fallback: o padrão pode estar dividido por várias regiões detetadas
    # pelo OCR. Concatenar todo o texto e tentar encontrar o padrão no total.
    full_text = ' '.join(t for _, t, _ in results)
    candidate = _extract_plate_candidate(full_text)
    if candidate:
        return candidate

    # Nenhum padrão encontrado na imagem
    return None
