from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit
from collections import deque
from datetime import datetime

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'Hypertext'
socket = SocketIO(app, cors_allowed_origins="*")

# Store the last 10 buzzer clicks with their positions
buzzer_clicks = deque(maxlen=10)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/buzzer', methods=['GET', 'POST'])
def buzzer():
    if request.method == 'POST':
        username = request.form.get('username')
        if not username:
            return render_template('login.html', error="Please enter a username")
        
        # Check if admin
        if username == 'admin@123':
            return render_template('admin.html')
            
        return render_template('Buzzer.html', username=username)
    return render_template('login.html')

@socket.on('buzz')
def handle_buzz(data):
    # Add the new buzz to the list
    buzz_data = {
        'username': data['username'],
        'timestamp': data['timestamp'],
        'senderId': data['senderId']
    }
    buzzer_clicks.append(buzz_data)
    
    # Sort by timestamp and assign positions
    sorted_clicks = sorted(list(buzzer_clicks), key=lambda x: x['timestamp'])
    for i, buzz in enumerate(sorted_clicks, 1):
        buzz['position'] = i
    
    # Emit the sorted list to all clients
    emit('buzz', sorted_clicks, broadcast=True)

@socket.on('reset')
def handle_reset():
    buzzer_clicks.clear()
    # Emit both reset event and empty buzz list
    emit('reset', broadcast=True)
    emit('buzz', list(buzzer_clicks), broadcast=True)

if __name__ == "__main__":
    socket.run(app, debug=True, host='0.0.0.0')