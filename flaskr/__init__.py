import os

from flask import Flask, redirect, url_for
from flask_socketio import SocketIO

socketio = SocketIO()

def create_app(test_config = None):
    app = Flask(__name__,instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    socketio.init_app(app)
    #socketio.run(app)
    from . import game, events, auth, db
    db.init_app(app)
    app.register_blueprint(game.bp)
    app.register_blueprint(events.bp)
    app.register_blueprint(auth.bp)

    if test_config is None :
        app.config.from_pyfile('config.py',silent=True)
    else:
        app.config.from_mapping(test_config)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/")
    def hello():
        return redirect(url_for('auth.login'))
    
    @socketio.on('message')
    def handle_message(data):
        print('received message: ' + data)
    
    return app