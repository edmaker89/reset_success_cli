import os

import requests
from dotenv import load_dotenv

load_dotenv()

AUTH_TOKEN = os.getenv("AUTH_TOKEN")
API_URL = os.getenv("API_URL", "https://seu-endpoint")

cpfs = [
    "05540983181"
]

headers = {
    "Authorization": f"Basic {AUTH_TOKEN}",
}

for cpf in cpfs:
    resp = requests.post(
        API_URL,
        headers=headers,
        json={
            "cpf": cpf,
            "Tipo_usuario": "CPF"
        }
    )

    dados = resp.json()
    usuario = dados.get("usuario", "")
    nova_senha = dados.get("nova_senha", "")

    print(f"{usuario} / {nova_senha}")
