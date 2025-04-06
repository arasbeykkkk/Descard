# server.py
from flask import Flask
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('message')
def handle_message(msg):
    print('Mesaj:', msg)
    send(msg, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, port=10000, host='0.0.0.0')
