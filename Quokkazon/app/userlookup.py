from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required

from .models.seller import Seller
from .models.category import Category

from flask import Blueprint
bp = Blueprint('userlookup', __name__)

#Page to lookup users
@bp.route('/lookup')
def lookup():
    is_seller = False
    #retrieving categories from category table
    sorted_categories = sorted(Category.get_all(), key=lambda x: x.name)
    if current_user.is_authenticated: 
        if Seller.find(current_user.id):
            is_seller = True
    return render_template('userlookup.html', 
    is_seller=Seller.is_seller(current_user),
    title='Lookup', categories=sorted_categories)