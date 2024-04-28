from flask import render_template
from flask import request, redirect, url_for
import os 
from .models.sermon import Sermon

from flask import Blueprint
bp = Blueprint('sermon', __name__)

@bp.route('/paraphrases')
def semantic_search():
    sermons = Sermon.get_all() 
    return render_template('index.html',
                        sermons = sermons)