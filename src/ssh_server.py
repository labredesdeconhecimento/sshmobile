# coding: utf-8
"""
sshmobile
~~~~~~~~~

Allows the user to run a remote command on his 
server (ssh server) from the smartphone

"""

from __future__ import with_statement
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, send_file
import paramiko
import hashlib
import os
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
#from yourapplication import app

# configuration
DATABASE = 'database.db'
DEBUG = True
SECRET_KEY = 'development key'

username = 'admin'
encrypted_password = '3c9909afec25354d551dae21590bb26e38d53f2173b8d3dc3eee4c047e7ab1c1eb8b85103e3be7ba613b31bb5c9c36214dc9f14a42fd7a2fdb84856bca5c44c2'

# initialize the application
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

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
        ''' Stores the form data, in case of the user clicks the link back on the next page '''
        session['data'] = request.form    

        data = request.form
        ssh = MySSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(data['ip'], username=data['user'], password=data['password'], port=int(data['port']), timeout=600)
        stdin, stdout, stderr = ssh.exec_command(data['command'], timeout=1)
        entries = stdout.readlines()
        ssh.close()
    except Exception:
        flash('Error while trying to open remote conection. Please, check the inputs.')
        return render_template('index.html', values=data)
    
    return render_template('ssh.html', entries=entries)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] != username or encrypt(request.form['password']) != encrypted_password:
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
    
class MySSHClient(paramiko.SSHClient): 
    ## overload the exec_command method 
    def exec_command(self, command, bufsize=100, timeout=None): 
        chan = self._transport.open_session() 
        chan.settimeout(timeout) 
        chan.exec_command(command) 
        stdin = chan.makefile('wb', bufsize) 
        stdout = chan.makefile('rb', bufsize) 
        stderr = chan.makefile_stderr('rb', bufsize) 
        return stdin, stdout, stderr 
        
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 443))
    
    http_server = HTTPServer(WSGIContainer(app), ssl_options={
        "certfile": "certificate.pem",
        "keyfile": "privatekey.pem",
    })
    
    http_server.listen(port)
    IOLoop.instance().start()

