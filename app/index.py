from flask import render_template
from flask import redirect, request, url_for, session
from collections import defaultdict

from .models.metadata import Metadata

from flask import Blueprint
bp = Blueprint('index', __name__)

@bp.route('/')
def index():
    sermons = Metadata.get_all()
    return render_template('index.html',
                        sermons = sermons)
    
