#!/usr/bin/env python3

from flask import Flask, session, request, render_template, jsonify, redirect, url_for
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import eventlet
#from flask_pymongo import PyMongo
from pymongo import MongoClient
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user
import bcrypt

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret_key'
con = MongoClient('ds155862.mlab.com', 55862)
db = con['scavenger_hunt']
db.authenticate('stephanie-phuong-khanh', 'Leo10Messi')

socketio = SocketIO(app)

#Login
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/play")
def play():
    if 'username' in session:
        return render_template('play.html', name=session['username'])
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    users = db.users
    login_user = users.find_one({'name' : request.form['username']})
    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == login_user['password']:
            session['username'] = request.form['username']
            return redirect(url_for('play'))
    return 'Invalid username/password combination'
    # user_id = db.users.insert_one({'name': 'John', 'age': 18}).inserted_id
    # print ('Added new user ID: ' + str(user_id))

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = db.users
        existing_user = users.find_one({'name': request.form['username']})
        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name': request.form['username'], 'password': hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('play'))
        return ('That username already exists!')
    return render_template('register.html')


@socketio.on('connect')  #authentication?
def connect_handler():
    if current_user.is_authenticated:
        print('Connected. SessionID:' + request.sid)
        emit('my response',
             {'message': '{0} has joined'.format(current_user.name)},
             broadcast=True)
    else:
        return render_template('index.html')

@socketio.on('disconnect') 
def disconnect_handler():
    print('Disconnected.')

if __name__ == '__main__':
    #app.run(debug='True')
    socketio.run(app, debug='True')