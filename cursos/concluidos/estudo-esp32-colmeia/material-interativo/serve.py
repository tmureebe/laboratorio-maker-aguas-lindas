#!/usr/bin/env python3
"""Serve only the deliverable directory on loopback. No dependencies."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Inicia o curso Colmeia localmente.')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--directory', type=Path, default=Path(__file__).resolve().parents[1] / 'dist')
    args = parser.parse_args()
    directory = args.directory.resolve()
    if not (directory / 'index.html').is_file():
        parser.error('A pasta indicada não contém index.html.')
    class Handler(SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header('Cache-Control', 'no-cache')
            super().end_headers()
        def log_message(self, fmt, *values):
            if values and str(values[1] if len(values) > 1 else '') not in ('200', '304'):
                super().log_message(fmt, *values)
    try:
        server = ThreadingHTTPServer(('127.0.0.1', args.port), partial(Handler, directory=str(directory)))
    except OSError as error:
        parser.exit(1, f'Não foi possível usar a porta {args.port}: {error.strerror}. Tente ./start.sh --port 8001\n')
    print(f'Curso pronto: http://127.0.0.1:{server.server_port}\nAbra esse endereço no navegador. Ctrl+C encerra o servidor.\nUse sempre o mesmo endereço e porta para recuperar o progresso.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nCurso encerrado. O progresso continua no navegador.')
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
