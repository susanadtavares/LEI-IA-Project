# =============================================================================
# llm.py
# =============================================================================
# Módulo de integração com um LLM (Large Language Model) local através do
# Ollama — uma ferramenta que permite correr modelos de linguagem localmente,
# sem enviar dados para a internet.
#
# Pré-requisitos:
#   1. Instalar Ollama:  https://ollama.com/download
#   2. Descarregar um modelo (sugestão):  ollama pull llama3.2
#   3. Garantir que o servidor está a correr:  ollama serve
#      (em Windows, o Ollama inicia automaticamente como serviço de sistema)
#
# O Ollama expõe uma API REST local em http://localhost:11434.
# Este módulo comunica com ela usando apenas a biblioteca padrão do Python
# (urllib), sem dependências externas adicionais.
#
# Função pública principal:
#   get_city_attractions(city, model) -> str
# =============================================================================

import json
import urllib.request
import urllib.error

# Endpoint da API do Ollama para geração de texto.
# Por defeito o Ollama fica na porta 11434 do localhost.
OLLAMA_URL    = "http://localhost:11434/api/generate"

# Modelo a usar por defeito. Pode ser alterado na chamada de cada função.
# llama3.2 é um modelo leve (3B parâmetros) e rápido, adequado a hardware
# doméstico. Alternativas: mistral, phi3, tinyllama, etc.
DEFAULT_MODEL = "llama3.2"


def _post(payload: dict, timeout: int = 120) -> dict:
    """
    Função auxiliar privada: envia um pedido POST ao servidor Ollama.

    Parâmetros:
        payload : dicionário Python que será serializado para JSON e enviado
        timeout : segundos máximos de espera pela resposta (modelos grandes
                  podem demorar mais tempo a gerar texto)

    Retorna:
        Dicionário Python com a resposta JSON do Ollama.

    Lança:
        urllib.error.URLError se o servidor não estiver acessível.
    """
    data = json.dumps(payload).encode("utf-8")
    req  = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},  # obrigatório para a API REST
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_city_attractions(city: str, model: str = DEFAULT_MODEL) -> str:
    """
    Consulta o LLM local (Ollama) para obter as 3 principais atrações de uma cidade.

    Parâmetros:
        city : nome da cidade Portuguesa
        model: modelo Ollama a utilizar (default: llama3.2)

    Retorna:
        String com as 3 atrações ou mensagem de erro.
    """
    # Prompt cuidadosamente estruturado para obter uma resposta consistente:
    # - Instrução clara do que queremos (3 atrações)
    # - Pedido de resposta em português
    # - Formato explícito com numeração e limite de texto por atração
    # - Proibição de conteúdo adicional (evita longas introduções/conclusões)
    prompt = (
        f"Indica as 3 principais atrações turísticas de {city}, Portugal. "
        "Responde em português de forma concisa, numerando cada atração. "
        "Formato obrigatório:\n"
        "1. [Nome]: [Breve descrição num máximo de 2 frases]\n"
        "2. [Nome]: [Breve descrição num máximo de 2 frases]\n"
        "3. [Nome]: [Breve descrição num máximo de 2 frases]\n"
        "Não incluas mais nada além das 3 atrações."
    )

    payload = {
        "model":  model,   # modelo a usar no Ollama
        "prompt": prompt,  # texto de entrada para o modelo
        "stream": False,   # False = esperar pela resposta completa de uma vez
                           # (True enviaria tokens à medida que são gerados)
    }

    try:
        result = _post(payload)
        # A API do Ollama devolve a resposta gerada no campo "response"
        return result.get("response", "Resposta vazia do LLM.").strip()

    except urllib.error.URLError:
        # Erro de rede/ligação: Ollama não está a correr ou porta incorreta
        return (
            "⚠  Não foi possível ligar ao Ollama.\n"
            "   Certifica-te de que o Ollama está em execução: ollama serve\n"
            f"  E que o modelo está disponível: ollama pull {model}"
        )
    except Exception as exc:
        # Qualquer outro erro inesperado (JSON inválido, timeout, etc.)
        return f"⚠  Erro ao consultar o LLM: {exc}"


def list_available_models() -> list[str]:
    """
    Consulta o Ollama para listar os modelos instalados localmente.
    Útil para mostrar ao utilizador quais os modelos disponíveis antes
    de escolher qual usar.

    Retorna:
        Lista de strings com os nomes dos modelos (ex: ['llama3.2', 'mistral']).
        Devolve lista vazia se o Ollama não estiver acessível.
    """
    try:
        # Endpoint /api/tags lista todos os modelos instalados no Ollama
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return [m["name"] for m in data.get("models", [])]
    except Exception:  # silenciar erro: se o Ollama não estiver disponível, devolver []
        return []
