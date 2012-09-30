# coding: utf-8
"""
sshmobile
~~~~~~~~~

Allows the user to run a remote command on his 
server (ssh server) from the smartphone

"""
from __future__ import with_statement
from sqlite3 import dbapi2 as sqlite3
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, send_file
import paramiko
import hashlib

# configuration
DATABASE = 'database.db'
DEBUG = True
SECRET_KEY = 'development key'

# initialize the application
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    """Returns a new connection to the database."""
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    """Creates the database tables."""
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    """Make sure we are connected to the database each request."""
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'db'):
        g.db.close()

#@app.route('/')
#def show_entries():
#    cur = g.db.execute('select title, text from entries order by id desc')
#    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
#    return render_template('show_entries.html', entries=entries)

@app.route('/index')
def index():
    if not session.get('logged_in'):
        abort(401)
    return render_template('index.html', values=session.get('data'))

@app.route('/ssh', methods=['POST', 'GET'])
def ssh_session():
    if not session.get('logged_in'):
        abort(401)

    try:
        ''' Stores de form data, in case of the user clicks the link back on the next page '''
        session['data'] = request.form    

        data = request.form
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(data['ip'], username=data['user'], password=data['password'], port=int(data['port']))
        stdin, stdout, stderr = ssh.exec_command(data['command'])
    except Exception:
        flash('Error while trying to open remote conection. Please, check the inputs.')
        return render_template('index.html', values=data)
    
    return render_template('ssh.html', entries=stdout.readlines())

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cur = g.db.execute('select username, encrypted_password from users')
        user = cur.fetchall()[0]
  
        if request.form['username'] != user[0] or encrypt(request.form['password']) != user[1]:
            flash('Invalid username or password!')
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return render_template('login.html')

def encrypt(password):
    return hashlib.sha512(password).hexdigest()
    
@app.route('/favicon.ico')
def get_favicon():
    return send_file('static/favicon.ico', mimetype='image/png')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0')
