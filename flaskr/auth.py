from flask import Blueprint, session, redirect, url_for, render_template, request

from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField
from wtforms.validators import DataRequired


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
    if form.validate_on_submit():
        session['name'] = form.name.data
        session['room'] = form.room.data
        session['maxPlayers'] = form.maxPlayers.data
        return redirect(url_for('game.board',playerName = session['name']),)
    elif request.method == 'GET':
        form.name.data = session.get('name', '')
        form.room.data = session.get('room', '')
        form.maxPlayers.data = session.get('maxPlayers', '')
    return render_template('login.html', form=form)