from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    # Use localhost for local development.
    # For external access set host='0.0.0.0' and configure firewall/NGINX accordingly.
    socketio.run(app, debug=True, host='127.0.0.1', port=5000)

