from flask import jsonify
from flask import render_template, flash
from flask_login import current_user
from flask import redirect, url_for, request
import datetime
import decimal
from humanize import naturaltime

from .models.cart import CartItem
from .models.inventory import Inventory
from .models.purchase import Purchase
from .models.user import User
from .models.feedback import ProductFeedback, SellerFeedback
from .models.category import Category
from .models.seller import Seller

from flask import Blueprint
bp = Blueprint('cart', __name__)


@bp.route('/cart')
def cart():
    if (current_user.is_authenticated):
        #check if holiday code has been applied
        discount = request.args.get('discount', default=False, type=bool)
        multiplier = 1
        if discount:
            multiplier = 0.75
        seller_names = {}
        product_names = {}
        # find the items the current user has added to their cart
        if current_user.is_authenticated:
            items = CartItem.get_all_by_uid(
                            current_user.id)
            for item in items:
                # get the name of the seller 
                seller_names[item.sid] = SellerFeedback.get_name(item.sid)
                # get the name of the product 
                product_names[item.pid] = ProductFeedback.get_product_name(item.pid)[0][0]
                item.price = round(decimal.Decimal(multiplier) * item.price,2)
            totalprice = round(CartItem.get_total_price(current_user.id) * multiplier,2)

        else:
            return jsonify({}), 404
        sorted_categories = sorted(Category.get_all(), key=lambda x: x.name)
        # render the page by adding information to the cart.html file
        return render_template('cart.html',
                        items=items, totalprice=totalprice, seller_names = seller_names, 
                        product_names=product_names, categories = sorted_categories,
                        is_seller= Seller.is_seller(current_user))
    else:
        return redirect(url_for('index.index'))


@bp.route('/cart/add', methods=['POST'])
def cart_add():
    product_id = request.form["product_id"]
    seller_id = request.form["seller_id"]
    quantity = request.form.get("quantity", "")
    if not quantity or not quantity.isdigit():
        quantity = 1
    saved_for_later = request.form["saved_for_later"]
    #check in stock
    if int(quantity) > Inventory.get(seller_id, product_id).num_for_sale:
        flash("Not enough in stock.")
        return redirect(url_for('cart.cart'))
    #check quantity is positive
    if int(quantity) >= 1:
    #add item to cart with specifications if already not in cart
        if CartItem.get(current_user.id, seller_id, product_id) == None:
            CartItem.add_item(current_user.id, seller_id, product_id, quantity, saved_for_later)
        else: #otherwise, tell the user they have already ordered it.
            flash("Item is already in the cart.")
    else:
        flash("You can't order less than 1 of this item.")
    return redirect(url_for('cart.cart'))

@bp.route('/cart/select/<int:product_id>', methods=['POST'])
def cart_select(product_id):
    sorted_categories = sorted(Category.get_all(), key=lambda x: x.name)
    # find the sellers for this product
    names = {}
    summary_feedback = {}
    if current_user.is_authenticated:
        sellers = Inventory.get_all_by_pid(product_id)
        for seller in sellers: 
            names[seller.sid] = SellerFeedback.get_seller_name(seller.sid)
            summary_feedback[seller.sid] = SellerFeedback.summary_ratings(seller.sid)
    else:
        return jsonify({}), 404
    # render a seller selection page with seller IDs and prices
    return render_template('sellerselection.html',
                      sellers=sellers,
                      names=names,
                      summary_feedback=summary_feedback, categories=sorted_categories,
                      is_seller= Seller.is_seller(current_user))

@bp.route('/cart/remove/<int:product_id>/<int:seller_id>', methods=['POST'])
def cart_remove(seller_id, product_id):
    CartItem.remove_item(current_user.id, seller_id, product_id)
    return redirect(url_for('cart.cart'))

@bp.route('/cart/update_quantity', methods=['POST'])
def cart_update_quantity():
    quantity = request.form.get("quantity", "")
    if not quantity or not quantity.isdigit():
        quantity = 1
    seller_id = request.form['seller_id']
    product_id = request.form['product_id']
    #check quantity not over stock
    if int(quantity) > Inventory.get(seller_id, product_id).num_for_sale:
        flash("Not enough in stock.")
        return redirect(url_for('cart.cart'))
    #check quantity is positive
    if int(quantity) >= 1:
        CartItem.update_quantity(current_user.id, seller_id, product_id, quantity)
    else:
        flash("You can't order less than 1 of this item.")
    return redirect(url_for('cart.cart'))

@bp.route('/cart/submit', methods=['POST'])
def cart_submit():
    #get cart price
    totalPrice = float(request.form["total"].strip("/"))
    multiplier = 1
    #check if these are discounted prices, or listed prices
    discounted = CartItem.compare(current_user.id, totalPrice)
    if discounted:
        multiplier = 0.75
    if totalPrice == 0: #block empty orders
        flash("You can't submit an empty order!")
        return redirect(url_for('cart.cart'))
    #compare price with users balance
    if totalPrice < User.get_balance(current_user.id):
        neworder = CartItem.newOrderId(current_user.id)
        inStock = CartItem.check_stocks(current_user.id)
        if inStock: #stock may have changed since user last logged in
            CartItem.increase_balances(CartItem.get_all_sids(current_user.id), current_user.id, multiplier) #increase for sellers
            CartItem.decrease_balance(current_user.id, totalPrice) #subtract from buyer
            items = CartItem.get_all_by_uid(
                                current_user.id)
            for item in items: #enter new items into purchases table
                if item.saved_for_later == '0': #other functions check in the model, get_all_by_uid doesn't
                    #because it is what is used to render the whole cart page
                    CartItem.decrease_stock(item.sid, current_user.id, item.pid)
                    CartItem.newPurchase(item.uid, item.sid, item.pid, neworder, item.quantity, item.price * decimal.Decimal(multiplier), None)
            CartItem.submit(current_user.id)
            return redirect(url_for('cart.cart_order', order_id = neworder)) #show order details
        else:
            flash("One or more items are out of stock for your order.")
            return redirect(url_for('cart.cart'))
    else:
        flash("The total price exceeds your current balance!")
        return redirect(url_for('cart.cart'))

@bp.route('/cart/<int:order_id>')
def cart_order(order_id):
    items = Purchase.get_order(current_user.id, order_id)
    all_fulfilled = True
    for item in items: #iterate through to see if order is completely fulfilled
        if item.date_fulfilled == None:
            all_fulfilled = False
    totalprice = Purchase.get_total_price_order(current_user.id, order_id)
    sorted_categories = sorted(Category.get_all(), key=lambda x: x.name)
    seller_names = {}
    product_names = {}
    product_feedback_exists = {}
    seller_feedback_exists = {}
    for purchase in items: 
        # get the name of the seller 
        seller_names[purchase.sid] = SellerFeedback.get_name(purchase.sid)
        # get the name of the product 
        product_names[purchase.pid] = ProductFeedback.get_product_name(purchase.pid)[0][0]
        # check whether we place the link to feedback editing or submission form 
        if len(ProductFeedback.feedback_exists(current_user.id,purchase.pid)) > 0: 
            product_feedback_exists[purchase.pid] = True
        else: 
            product_feedback_exists[purchase.pid] = False
        # check whether we place the link to feedback editing or submission form 
        if len(SellerFeedback.feedback_exists(current_user.id,purchase.sid)) > 0: 
            seller_feedback_exists[purchase.sid] = True
        else: 
            seller_feedback_exists[purchase.sid] = False
    
    return render_template('buyerOrder.html', 
                           items = items, 
                           totalprice = totalprice,
                           seller_names = seller_names,
                           product_names = product_names,
                           product_feedback_exists = product_feedback_exists,
                           seller_feedback_exists = seller_feedback_exists,
                           all_fulfilled = all_fulfilled,
                           categories= sorted_categories,
                           is_seller= Seller.is_seller(current_user))

@bp.route('/cart/viewOrders')
def cart_viewOrders(): #show list of past orders for user
    items = Purchase.get_unique_orders_by_uid(current_user.id)
    sorted_categories = sorted(Category.get_all(), key=lambda x: x.name)
    return render_template('viewOrders.html', items = items, categories = sorted_categories, is_seller= Seller.is_seller(current_user))

@bp.route('/cart/update_saved', methods=['POST'])
def cart_update_saved():
    product_id = request.form['product_id']
    seller_id = request.form['seller_id']
    saved_for_later = request.form['saved_for_later']
    if saved_for_later == '0':
        CartItem.move_to_saved(current_user.id, seller_id, product_id)
    else:
        CartItem.move_to_cart(current_user.id, seller_id, product_id)
    return redirect(url_for('cart.cart'))

@bp.route('/cart/discount', methods=['POST'])
def cart_discount():
    code = request.form['code']
    if code == "QUOLIDAY25":
        #CartItem.discount(current_user.id)
        flash("Code applied!")
        return redirect(url_for('cart.cart', discount = True))
    else:
        flash("Code not recognized.")
        return redirect(url_for('cart.cart'))