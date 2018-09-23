#!/usr/bin/env python3

from flask import Flask, session, request, render_template, jsonify, redirect, url_for
from flask_restful import Api, Resource, reqparse
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import eventlet
from pymongo import MongoClient
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user
import bcrypt
import requests
from flask_cors import CORS
from bson.objectid import ObjectId
import socketio

app = Flask(__name__)
CORS(app)
api = Api(app)
socketio = SocketIO(app)

app.config['SECRET_KEY'] = 'secret_key'
con = MongoClient('ds155862.mlab.com', 55862)
db = con['scavenger_hunt']
db.authenticate('stephanie-phuong-khanh', 'Leo10Messi')

games = db["games"]
ID = 0

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/login', methods=['POST'])
def login():
    request_json = request.get_json()
    username = request_json.get('username')
    users = db.users
    login_user = users.find_one({'username' : username})
    if login_user:
        if bcrypt.hashpw(request_json.get('password').encode('utf-8'), login_user.get('password')) == login_user.get('password'):
            #session['username'] = username
            new_user_ID = users.find_one({'username' : username}).get('_id')
            return (str(new_user_ID))
    print('bad login broooo0oo')
    return ('Fail')

@app.route('/register', methods=['POST'])
def register():
    request_json = request.get_json()
    username = request_json.get('username')
    # print('USERNAME:' + type(username))
    users = db.users
    user_taken = users.find_one({'username': username })
    if user_taken:
        return ('Fail')
    else:
        hashpass = bcrypt.hashpw(request_json.get('password').encode('utf-8'), bcrypt.gensalt())
        users.insert_one({
            'username' : username,
            'password' : hashpass
        })
        #session['username'] = username
        new_user_ID = users.find_one({'username' : username}).get('_id')
        return (str(new_user_ID))


@app.route('/savegame', methods=['POST'])
def saveGame():
    if request.method == 'POST':
        games = db.games
        _id = games.insert_one({
            'ownerID': request.json.get('ownerID', None),
            'title': request.json.get('gameTitle', None),
            'location': request.json.get('gameLocation', None),
            'description': request.json.get('gameDescription', None),
            'tasks': [],
        })
        ID = str(_id.inserted_id)
        return jsonify({
            "status": 'OK',
            "message": 'Game Added!',
            "id": ID,
        })
        
@app.route('/savetask', methods=['POST'])
def saveTask():
    if request.method == 'POST':
        _id = request.json.get('_id', None)
        # print(_id)
        game = db.games.find_one({'_id': ObjectId(_id)})
        games = db.games
        games.update_one(
            {'_id': ObjectId(_id)},
            {
                '$push': {'tasks': 
                    {
                        'order': request.json.get('order', None),
                        'title': request.json.get('title', None),
                        'image_desc': request.json.get('desc', None),
                        'image_url': request.json.get('url', None), 
                    }
                }
            }
        )
        # print(game)
        return jsonify({
            'status': 'OK',
            'message': 'Task Added!',
        })


@socketio.on('connect')  #authentication?
def connect_handler():
    print('SOCKETIO Connected. SessionID:' + request.sid)

@socketio.on('disconnect') 
def disconnect_handler():
    print('SOCKETIO Disconnected.')

if __name__ == '__main__':
    # app.run(debug='True', host='0.0.0.0')
    socketio.run(app, debug='True', host='0.0.0.0')