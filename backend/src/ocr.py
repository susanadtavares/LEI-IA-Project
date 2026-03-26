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
    # readtext devolve lista de (bounding_box, texto, confiança)
    results = reader.readtext(image_path)

    # Ordenar resultados por confiança descendente: o OCR está mais seguro
    # das regiões com confiança mais alta — processamos essas primeiro.
    results.sort(key=lambda r: r[2], reverse=True)

    candidates = []
    for _, text, confidence in results:
        if confidence < 0.2:  # descartar reconhecimentos com confiança muito baixa
            continue
        for pattern in _PLATE_PATTERNS:
            match = pattern.search(text)
            if match:
                # Guardar par (confiança, matrícula normalizada)
                candidates.append((confidence, _normalise_plate(match.group())))

    if candidates:
        # Devolver a matrícula com maior confiança de reconhecimento
        candidates.sort(key=lambda c: c[0], reverse=True)
        return candidates[0][1]

    # Fallback: o padrão pode estar dividido por várias regiões detetadas
    # pelo OCR. Concatenar todo o texto e tentar encontrar o padrão no total.
    full_text = ' '.join(t for _, t, _ in results)
    for pattern in _PLATE_PATTERNS:
        match = pattern.search(full_text)
        if match:
            return _normalise_plate(match.group())

    # Nenhum padrão encontrado na imagem
    return None
