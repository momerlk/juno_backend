from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import requests

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes with the policy set to "*"
socketio = SocketIO(app, cors_allowed_origins="*")

TARGET_URL = 'ws://172.24.6.108:8080/feed'

@app.route('/')
def index():
    return "WebSocket proxy server is running"

@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

@socketio.on('message')
def handle_message(message):
    print(f"Received message: {message}")
    try:
        resp = requests.post(TARGET_URL, json=message)
        emit('response', resp.json())
    except requests.exceptions.RequestException as e:
        emit('response', {'error': str(e)})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=3002)
