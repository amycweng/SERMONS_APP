
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import current_user
from .models.seller import Seller
from .models.user import User
from .models.product import Product
from .models.purchase import Purchase
from .models.category import Category
import datetime

bp = Blueprint('allpurchases', __name__)

@bp.route('/orders', methods=['GET', 'POST'])
def orders():
    # find the products current user has bought:
    if current_user.is_authenticated:
        orders = Purchase.get_all_by_sid(
            current_user.id)
    else:
        orders = None
        
    categories = Category.get_all()
    sorted_categories = sorted(categories, key=lambda x: x.name)
    # render the page by adding information to the index.html file
    return render_template('orders.html',
                           orders=orders,
                           is_seller=Seller.is_seller(current_user),
                           product_class=Product,
                           user_class=User,
                           categories=sorted_categories)

# Let a seller mark a purchase as fulfilled at the current time within their own orders table
@bp.route('/orders/fulfill/<int:uid>-<int:sid>-<int:pid>-<int:oid>', methods=['POST'])
def fulfill(uid, sid, pid, oid):
    current_dateTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if Purchase.fulfill(uid, sid, pid, oid, current_dateTime):
        return redirect(url_for('allpurchases.orders'))
    else:
        print("ERROR with fulfillment entry")
    return redirect(url_for('allpurchases.orders'))
        