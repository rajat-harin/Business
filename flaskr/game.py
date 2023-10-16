import functools
import random
from flask import (
    Blueprint,
    render_template,
    session
)

bp = Blueprint('game', __name__, url_prefix='/game')

@bp.route("/board")
@bp.route("/board/<playerName>")
def board(playerName = None):
    return render_template('game/board.html', playerName=playerName)

@bp.route("/roll")
def roll():
    return str(random.randrange(1,13))
