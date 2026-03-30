import socket
from app import create_app, socketio

app = create_app()


def pick_free_port(primary=5000, max_port=5100):
    for port in range(primary, max_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    raise RuntimeError(f'No free port found between {primary} and {max_port}')


if __name__ == '__main__':
    chosen_port = pick_free_port(5000, 5100)
    print(f'Running on 127.0.0.1:{chosen_port} (auto-select)')
    socketio.run(app, debug=True, host='127.0.0.1', port=chosen_port)
