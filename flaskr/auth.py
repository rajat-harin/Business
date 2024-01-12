from flask import Blueprint, flash, g, session, redirect, url_for, render_template, request

from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.security import check_password_hash, generate_password_hash


from flaskr.db import get_db

class LoginForm(FlaskForm):
    """Accepts a nickname and a room."""
    name = StringField('Name', validators=[DataRequired()])
    room = StringField('Room', validators=[DataRequired()])
    maxPlayers = StringField('Max Players', validators=[DataRequired()])
    submit = SubmitField('Enter Gameroom')

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login form to enter a room."""
    form = LoginForm()
    db = get_db()

    if form.validate_on_submit():
        session['name'] = form.name.data
        session['room'] = form.room.data
        session['maxPlayers'] = form.maxPlayers.data

        # try:
        #     print('try')
        #     try:
        #         db.execute(
        #         "INSERT INTO ROOMS (title, maxPlayers, currentPlayers) VALUES (?, ?,?)",
        #         (session['room'], session['maxPlayers'], 1),
        #         )
        #         db.commit()
        #     except db.IntegrityError:
        #         pass
        #     except db.DatabaseError:
        #         print('Error while creating room!')
        #         print(db.Error.sqlite_errorname)
        #     db.execute(
        #         "INSERT INTO USERS (username, password, room) VALUES (?, ?,?)",
        #         (session['name'], generate_password_hash('123'),session['room']),
        #     )
        #     db.commit()
        # except db.IntegrityError:
        #     print('except integrity')
        #     user = db.execute(
        #     'SELECT * FROM USERS WHERE username = ?', (session['name'],)
        #     ).fetchone()
        #     print(str(db.IntegrityError))
        # except db.DatabaseError:
        #     print('except Error')
        #     print(db.Error.sqlite_errorname)

        # else:
        #     return redirect(url_for("auth.login"))

        return redirect(url_for('game.board',playerName = session['name']),)
    elif request.method == 'GET':
        form.name.data = session.get('name', '')
        form.room.data = session.get('room', '')
        form.maxPlayers.data = session.get('maxPlayers', '')
    return render_template('login.html', form=form)


"""Unused routes below needs code extension and integration"""
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

# @bp.before_app_request
# def load_logged_in_user():
#     user_id = session.get('user_id')

#     if user_id is None:
#         g.user = None
#     else:
#         g.user = get_db().execute(
#             'SELECT * FROM user WHERE id = ?', (user_id,)
#         ).fetchone()