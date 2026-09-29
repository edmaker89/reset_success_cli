import os
import re

import requests
from dotenv import load_dotenv

load_dotenv()

AUTH_TOKEN = os.getenv("AUTH_TOKEN")
API_URL = os.getenv("API_URL", "https://seu-endpoint")

# Campos onde a integração pode mandar a mensagem de retorno (o primeiro preenchido vence).
CAMPOS_MENSAGEM = ("mensagem", "message", "msg", "retorno", "erro", "error")


def limpar_cpf(cpf: str) -> str:
    return re.sub(r"\D", "", cpf or "")


def reset_senha(cpf: str) -> dict:
    """Chama a API de reset e devolve um resultado normalizado para o painel."""
    cpf = limpar_cpf(cpf)
    resultado = {"cpf": cpf, "ok": False, "http": None, "usuario": "", "nova_senha": "", "mensagem": "", "erro": ""}

    if len(cpf) != 11:
        resultado["erro"] = "CPF inválido (precisa ter 11 dígitos)"
        return resultado

    try:
        resp = requests.post(
            API_URL,
            headers={"Authorization": f"Basic {AUTH_TOKEN}"},
            json={"cpf": cpf, "Tipo_usuario": "CPF"},
            timeout=30,
        )
    except requests.RequestException as exc:
        resultado["erro"] = f"Falha de conexão: {exc.__class__.__name__}"
        return resultado

    resultado["http"] = resp.status_code
    try:
        dados = resp.json()
    except ValueError:
        dados = {}

    if not isinstance(dados, dict):
        dados = {}

    resultado["usuario"] = dados.get("usuario", "") or ""
    resultado["nova_senha"] = dados.get("nova_senha", "") or ""
    resultado["mensagem"] = str(next((dados[k] for k in CAMPOS_MENSAGEM if dados.get(k)), ""))

    if resp.ok and resultado["nova_senha"]:
        resultado["ok"] = True
    else:
        resultado["erro"] = resultado["mensagem"] or resp.text[:200] or f"HTTP {resp.status_code}"

    return resultado
