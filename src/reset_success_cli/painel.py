import json
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from reset_success_cli.api import API_URL, AUTH_TOKEN, reset_senha

HOST = "127.0.0.1"
PORT = 8765
PAGINA = (Path(__file__).parent / "painel.html").read_bytes()


class Handler(BaseHTTPRequestHandler):
    def _json(self, status: int, corpo: dict) -> None:
        dados = json.dumps(corpo, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(PAGINA)))
            self.end_headers()
            self.wfile.write(PAGINA)
        elif self.path == "/api/config":
            self._json(200, {"configurado": bool(AUTH_TOKEN) and "seu-endpoint" not in API_URL})
        else:
            self._json(404, {"erro": "não encontrado"})

    def do_POST(self) -> None:
        if self.path != "/api/reset":
            self._json(404, {"erro": "não encontrado"})
            return
        try:
            tamanho = int(self.headers.get("Content-Length", 0))
            cpf = json.loads(self.rfile.read(tamanho) or b"{}").get("cpf", "")
        except (ValueError, AttributeError):
            self._json(400, {"erro": "corpo inválido"})
            return
        self._json(200, reset_senha(cpf))

    def log_message(self, fmt, *args) -> None:
        # Não loga o corpo; só método/rota/status, sem CPF nem senha.
        print(f"[painel] {self.command} {self.path} -> {args[1] if len(args) > 1 else ''}")


def main() -> None:
    servidor = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}"
    print(f"Painel rodando em {url} (Ctrl+C para sair)")
    webbrowser.open(url)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()
