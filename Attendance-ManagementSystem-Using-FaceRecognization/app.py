import subprocess
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "your_secret_key"

#user data for demonstration purposes
user_data = {
    '837480': {'password': 'employee123', 'role': 'employee'},
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in user_data and password == user_data[username]['password']:
            # Redirect to a different page after successful login
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        user_type = get_user_type(session['user'])
        if user_type == 'employee':
            #subprocess.run(['python3', 'main.py'])
            return render_template('employee_dashboard.html', username=session['user'])
        else:
            return "Unknown user type"
    return redirect(url_for('index'))

@app.route('/mark_attendance')
def mark_attendance():
    subprocess.run(['python3', 'main.py'])
    return redirect(url_for('dashboard'))

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/submit_contact_form', methods=['POST'])
def submit_contact_form():
    return redirect(url_for('index'))

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

def get_user_type(username):
    # Get user role from user_data dictionary
    if username in user_data:
        return user_data[username]['role']
    return 'unknown'

if __name__ == '__main__':
    app.run(debug=True)
