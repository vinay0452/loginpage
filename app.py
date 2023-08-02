from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Vinaymay@05'
app.config['MYSQL_DB'] = 'pythonlogin'

mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Retrieve username and password from the submitted form
        username = request.form['username']
        password = request.form['password']
        
        # Create a cursor to interact with the database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Execute the SQL query to select the account with the given username
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        
        # Check if the account exists and if the password matches the one in the database
        if account and password == account['password']:
            # If login is successful, store session data
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password!'
            
    # Render the login page with the appropriate message
    return render_template('index.html', msg=msg)

@app.route('/logout', methods=['GET'])
def logout():
    # Remove session data to log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        # Retrieve the form data for registration
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Create a cursor to interact with the database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Check if the account with the given username already exists
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # If all checks pass, insert the new account into the accounts table
            cursor.execute('INSERT INTO accounts (username, password, email) VALUES (%s, %s, %s)', (username, password, email))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    return render_template('register.html', msg=msg)

@app.route('/home', methods=['GET'])
def home():
    # Check if the user is logged in by verifying session data
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET'])
def profile():
    # Check if the user is logged in by verifying session data
    if 'loggedin' in session:
        # Retrieve the account information from the database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000)
