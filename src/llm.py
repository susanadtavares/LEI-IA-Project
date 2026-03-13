# llm.py
# Integração com LLM local via Ollama
# Instalar Ollama: https://ollama.com/
# Modelo sugerido: ollama pull llama3.2

import json
import urllib.request
import urllib.error

OLLAMA_URL  = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2"


def _post(payload: dict, timeout: int = 120) -> dict:
    """Envia um pedido POST ao servidor Ollama e retorna a resposta JSON."""
    data = json.dumps(payload).encode("utf-8")
    req  = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
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
        "model":  model,
        "prompt": prompt,
        "stream": False,
    }

    try:
        result = _post(payload)
        return result.get("response", "Resposta vazia do LLM.").strip()

    except urllib.error.URLError:
        return (
            "⚠  Não foi possível ligar ao Ollama.\n"
            "   Certifica-te de que o Ollama está em execução: ollama serve\n"
            f"  E que o modelo está disponível: ollama pull {model}"
        )
    except Exception as exc:
        return f"⚠  Erro ao consultar o LLM: {exc}"


def list_available_models() -> list[str]:
    """Devolve a lista de modelos disponíveis no Ollama local."""
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []
