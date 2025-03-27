from flask import Flask, request, render_template_string, session, redirect, url_for
import requests
from threading import Thread, Event
import time
import random
import string
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "SuperSecretKey2025"

# 🔑 Admin Credentials
ADMIN_USERNAME = "raj vampire"
ADMIN_PASSWORD = "raj mishra"

# 🌟 User Credentials
USERNAME = "vampire boy raj"
PASSWORD = "vampire rulex"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)',
    'Referer': 'https://www.google.com/'
}

stop_events = {}
threads = {}
task_start_times = {}
task_owners = {}
task_count = 0
MAX_TASKS = 10000  # Monthly Limit
TASK_LIFETIME = timedelta(days=730)  # 2 Years

# 🔄 Monthly Counter Reset
start_month = datetime.now().month

def send_messages(access_tokens, thread_id, hatersname, lastname, time_interval, messages, task_id):
    global task_count
    stop_event = stop_events[task_id]
    
    while not stop_event.is_set():
        for message1 in messages:
            if stop_event.is_set():
                break
            for access_token in access_tokens:
                api_url = f'https://graph.facebook.com/v17.0/t_{thread_id}/'
                message = f"{hatersname} {message1} {lastname}"
                parameters = {'access_token': access_token, 'message': message}
                requests.post(api_url, data=parameters, headers=headers)
                time.sleep(time_interval)

        if datetime.now() - task_start_times[task_id] > TASK_LIFETIME:
            stop_task(task_id)
    
    task_count -= 1
    del stop_events[task_id]
    del threads[task_id]
    del task_start_times[task_id]
    del task_owners[task_id]

def stop_task(task_id):
    if task_id in stop_events:
        stop_events[task_id].set()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            session['is_admin'] = False
            session['username'] = username
            return redirect(url_for('send_message'))
        elif username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['is_admin'] = True
            return redirect(url_for('admin_panel'))
        return '❌ Invalid Username or Password!'
    
    return '''
    <html>
    <head>
        <title>Login - By RAJ MISHRA</title>
        <style>
            body { text-align: center; background: url('https://i.ibb.co/1JLx8sbs/5b7cfab06a854bf09c9011203295d1d5.jpg') no-repeat center center fixed; background-size: cover; }
            h2 { color: white; }
            input, button { padding: 10px; margin: 5px; }
        </style>
    </head>
    <body>
        <h2>🔑 Login</h2>
        <form method="post">
            <input type="text" name="username" placeholder="Enter Username" required><br>
            <input type="password" name="password" placeholder="Enter Password" required><br>
            <button type="submit">🚀 Login</button>
        </form>
    </body>
    </html>
    '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/home', methods=['GET', 'POST'])
def send_message():
    global task_count, start_month
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if datetime.now().month != start_month:
        task_count = 0
        start_month = datetime.now().month

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
        task_start_times[task_id] = datetime.now()
        task_owners[task_id] = session['username']
        thread = Thread(target=send_messages, args=(access_tokens, thread_id, hatersname, lastname, time_interval, messages, task_id))
        threads[task_id] = thread
        thread.start()
        
        task_count += 1
        return f'Task started successfully! Your Task ID: {task_id}'

    return f'''
    <html>
    <head>
      <title>Task Panel - By RAJ MISHRA</title>
      <style>
        body {{ text-align: center; background: url('https://wallpapercave.com/wp/wp9535999.jpg') no-repeat center center fixed; background-size: cover; }}
        h2, h3, form, a {{ color: white; }}
        input, button {{ padding: 10px; margin: 5px; }}
      </style>
    </head>
    <body>
      <h2>📌 Running Tasks: {task_count} / {MAX_TASKS}</h2>
      <form method="post" enctype="multipart/form-data">
        <input type="text" name="singleToken" placeholder="Enter Token"><br>
        <input type="file" name="tokenFile"><br>
        <input type="text" name="threadId" placeholder="Enter Inbox/Convo ID" required><br>
        <input type="text" name="hatersname" placeholder="Enter Hater Name" required><br>
        <input type="text" name="lastname" placeholder="Enter Last Name" required><br>
        <input type="number" name="time" placeholder="Enter Time (seconds)" required><br>
        <input type="file" name="txtFile" required><br>
        <button type="submit">🚀 Start Task</button>
      </form>

      <h3>🛑 Stop Your Task:</h3>
      <form method="post" action="/stop_task">
        <input type="text" name="task_id" placeholder="Enter Task ID to Stop"><br>
        <button type="submit">❌ Stop Task</button>
      </form>

      <br><a href="/logout">🚪 Logout</a>
    </body>
    </html>
    '''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
