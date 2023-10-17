import functools
import json
import os
import random
from flask import (
    Blueprint,
    render_template,
    session,
    url_for
)

bp = Blueprint('game', __name__, url_prefix='/game')

@bp.route("/board")
@bp.route("/board/<playerName>")
def board(playerName = None):
    return render_template('game/board.html', playerName=playerName)
@bp.route("/getBoardData")
def getBoardData():
    json_data = open(os.path.join(os.path.realpath(os.path.dirname(__file__)), "static", "business.json"))
    data = json.load(json_data)
    return json.dumps(data)

@bp.route("/roll")
def roll():
    return str(random.randrange(1,13))
