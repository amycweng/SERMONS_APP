from flask import render_template
from flask import redirect, request, url_for, session
from collections import defaultdict

from .models.sermon import Sermon

from flask import Blueprint
bp = Blueprint('index', __name__)

@bp.route('/')
def index():
    sermons = Sermon.get_all() 
    return render_template('index.html',
                        sermons = sermons)
    
