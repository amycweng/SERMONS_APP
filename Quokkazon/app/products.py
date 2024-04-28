from flask import redirect, request, url_for, session, render_template, flash
from flask_session import Session
from flask_login import current_user
from humanize import naturaltime
import datetime
from collections import defaultdict
import os, random
import pandas as pd
import plotly
import plotly.express as px
import json

from .models.product import Product, ProductRating
from .models.feedback import ProductFeedback, SellerFeedback
from .models.purchase import Purchase
from .models.inventory import Inventory
from .models.stock import Stock
from .models.category import Category
from .models.seller import Seller

from flask import Blueprint

bp = Blueprint('products', __name__)

# List of month abbreviations for analytics graph
MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

#converting time into a readable format
def humanize_time(dt):
    return naturaltime(datetime.datetime.now() - dt)

#activating a search session
@bp.before_request
def activate_session():
    if request.path in ['/products/search_results']:
        session.modified = True

#deactivating a search session
@bp.after_request
def deactivate_session(response):
    if request.path in ['', '/products']:
        session['search_term'] = ''
    return response

#function to create the product detail and pass in values
@bp.route('/products/<int:product_id>',methods = ['GET','POST'])
def product_detail(product_id):
    #To create a recently viewed list without retrieving from database, save to session
    if 'recent' not in session:
        session['recent'] = []  # 
    recent_list = session['recent']
    #Don't want duplicate items, and I only want a maximum of 4 recently viewed items to display
    if product_id not in recent_list:
        if len(recent_list) < 4:
            recent_list.insert(0, product_id)
        else:
            recent_list.pop()   
    session['recent'] = recent_list
    
    product = Product.get(product_id)
    inventory = Inventory.get_all_by_pid(product_id)
    inv_len = len(inventory)
    seller_names = {}
    seller_summary = {}
    order_freq_graph = None
    sid = None
    
    #retrieve seller information
    for seller in inventory: 
        # get the name of the seller 
        seller_names[seller.sid] = SellerFeedback.get_name(seller.sid)
        # get summary feedback statistics for the seller 
        seller_summary[seller.sid] = SellerFeedback.summary_ratings(seller.sid)
    pfeedback = ProductFeedback.get_by_pid(product_id)
    sorted_by_upvotes = ProductFeedback.sorted_by_upvotes(product_id)
    pupvotes = {}
    
    #retrieve feedback information and upvote information
    for item in pfeedback:
        pupvotes[(item.uid,item.pid)] = ProductFeedback.upvote_count(item.uid,item.pid)[0][0]
    count = 0
    top3 = []
    for item in sorted_by_upvotes: 
        top3.append(item)
        count += 1 
        if count == 3: break
    # get summary statistics for ratings 
    summary = ProductFeedback.summary_ratings(product_id)
   
    #current user's feedback and upvotes
    myupvotes = {}
    if current_user.is_authenticated: 
        has_purchased = ProductFeedback.has_purchased(current_user.id,product_id)
        if len(has_purchased) > 0: 
            my_product_feedback = ProductFeedback.get_by_uid_pid(current_user.id, product_id)
        else: 
            my_product_feedback = False
            has_purchased = False
        # which reviews the current user has upvoted 
        for reviewer,reviewed in pupvotes: 
            myupvotes[(reviewer,reviewed)] = ProductFeedback.my_upvote(current_user.id,reviewer,reviewed)[0][0]
        
        sid = Seller.get(current_user.id)
        if sid and Inventory.in_inventory(current_user.id, product_id):
            # Create a graph for the number of orders per month for the given product and seller
            orders_freq = [[f'{MONTHS[row[0]-1]} {row[1]}',row[2]] for row in Purchase.get_num_orders_per_month(current_user.id, product_id)]
            of_df = pd.DataFrame(orders_freq, columns=['Month','Count'])
            of_fig = px.line(of_df, x='Month',y='Count',title='My Orders Per Month')
            order_freq_graph = json.dumps(of_fig, cls=plotly.utils.PlotlyJSONEncoder)            
    else: 
        my_product_feedback, has_purchased = False, False
        
    sorted_categories = sorted(Category.get_all(), key=lambda x: x.name)
    return render_template('productDetail.html',
                           product=product,
                           pfeedback=pfeedback,
                           pupvotes=pupvotes,
                           myupvotes=myupvotes,
                           summary=summary,
                           top3=top3,
                           seller_names=seller_names,
                           seller_summary=seller_summary,
                           my_product_feedback = my_product_feedback,
                           has_purchased=has_purchased,
                           humanize_time=humanize_time,
                           inventory=inventory,
                           inv_len = inv_len,
                           order_freq_graph=order_freq_graph,
                           is_seller=sid,
                           categories=sorted_categories)

ROWS = 24 #number of items on each page
#product page endpoint that shows all of the products
@bp.route('/products', methods=['GET','POST'])
def products():
    #pagination code
    page = request.args.get("page", 1, type=int)
    start = (page-1) * ROWS
    end = start + ROWS
    
    inventory = Inventory.get_all()
    product_prices = defaultdict(list)
    summary = defaultdict(list)
    items = []
    
    #make lists of product prices and summaries for items 
    for item in inventory:
        product_prices[item.pid].append(item.price)
        summary[item.pid] = ProductFeedback.summary_ratings(item.pid)

    #sorting and filtering the products
    if request.method == 'GET':
        filter_by = request.args.get('filter_by') if request.args.get('filter_by') is not None else 'all'
        sort_by = request.args.get('sort_by') if request.args.get('sort_by') is not None else 'a-z'
        if sort_by == "top_reviews":
            items = ProductRating.all_ratings()
        elif sort_by == "low_price":
            items = Stock.get_stock_asc()
        elif sort_by == "high_price":
            items = Stock.get_stock_desc()
        else:
            if filter_by == "available":
                if sort_by == "a-z":
                    items = Stock.get_az()             
                if sort_by == "z-a":
                    items = Stock.get_za()
            else:
                if sort_by == "a-z":
                    print("IM HERE A_Z")
                    items = Product.get_az()
                    
                else:
                    items = Product.get_za()
        

    paginated = items[start:end]
    total_pages = len(items)//24 + 1
    
    sorted_categories = sorted(Category.get_all(), key=lambda x: x.name)
    
    return render_template('products.html',
                      items=paginated,
                      inventory=inventory, 
                      summary=summary,
                      product_prices = product_prices,
                      page=page,
                      total_pages=total_pages,
                      categories=sorted_categories,
                      is_seller=Seller.is_seller(current_user),
                      category="All Products")

#endpoint for searches and search results
@bp.route('/products/search_results', methods=['GET','POST'])
def search_results():
    #pagination code
    page = request.args.get("page", 1, type=int)
    start = (page-1) * ROWS
    end = start + ROWS
    
    #the search term input by user
    search_term = request.args.get('search_term', '')

    inventory = Inventory.get_all()
    product_prices = defaultdict(list)
    summary = defaultdict(list)
    
    #defining product prices and summary for products
    for item in inventory:
        product_prices[item.pid].append(item.price)
        summary[item.pid] = ProductFeedback.summary_ratings(item.pid)
    
    #if nothing is searched, redirect to main products page, otherwise set the search term
    if request.method == 'POST':
        search_term = request.form['search_term']
        session['search_term'] = search_term
        if not search_term:
            return redirect(url_for('products.products'))
    
    #get search term from sessions
    if request.method == 'GET':
        search_term = session.get('search_term')
    
    #filtering and sorting on the search results page
    filter_by = request.args.get('filter_by') if request.args.get('filter_by') is not None else 'all'
    sort_by = request.args.get('sort_by') if request.args.get('sort_by') is not None else 'a-z'
    if sort_by == "top_reviews":
        items = search_products(search_term, ProductRating.all_ratings())
    elif sort_by == "low_price":
        items = search_products(search_term, Stock.get_stock_asc())
    elif sort_by == "high_price":
        items = search_products(search_term, Stock.get_stock_desc())
    else:
        if filter_by == "available":
            items = apply_sort(search_products(search_term, Stock.get_all_in_stock()), sort_by)
        else:
            items = apply_sort(search_products(search_term, Product.get_all()), sort_by)
    
    sorted_categories = sorted(Category.get_all(), key=lambda x: x.name)

    paginated = items[start:end]
    total_pages = len(items)//24 + 1
    return render_template('searchResults.html',
                            items = paginated,
                            inventory = inventory,
                            product_prices = product_prices,
                            search_term = search_term,
                            summary=summary,
                            len_products = len(items),
                            page=page,
                            total_pages=total_pages,
                            categories=sorted_categories,
                            is_seller=Seller.is_seller(current_user))
    
#search results are products that have search term in their name and description
def search_products(search_term, products):
    search_results = [product for product in products if (search_term.lower() in product.name.lower()) or (search_term.lower() in product.description.lower())]
    return search_results

#apply letter sorting function for any page
def apply_sort(items, sort_by):
    if sort_by == "a-z":
        sort_items = sorted(items, key=lambda x: x.name)
    if sort_by == "z-a":
        sort_items = sorted(items, key=lambda x: x.name, reverse=True)
    return sort_items

#endpoint for the add products form which inserts the form elements to the products table
@bp.route('/products/add_products', methods=['GET','POST'])
def add_products():
    sorted_categories = sorted(Category.get_all(), key=lambda x: x.name)
    if request.method == 'POST':
        name = request.form["name"]
        description = request.form["description"]
        altTxt = request.form["altTxt"]
        category = request.form["category"]
        pid = int(Product.newPID()[0][0]) + 1
        createdAt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updatedAt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        file = request.files['image']
        filename = file.filename
        filepath = os.path.join('/home/ubuntu/quokkazon/app/static/product_images', filename)
        file.save(filepath)
        
        
        if Product.get_by_name(name):
            flash(name + 'is already an available product')
            return redirect(url_for('inventory.inventory'))
        else:
            Product.add_product(pid, name, description, "product_images/" + filename, altTxt, createdAt, updatedAt, category, current_user.id)
        
        if Inventory.add(pid, current_user.id, 0, 0, 0):
            return redirect(url_for('inventory.edit', product_id=pid, oq=0, on=0, op=0))
        flash(Product.get_name(pid) + ' already present in inventory!')
        
        return redirect(url_for('inventory.inventory'))
                
    return render_template('add_products.html', categories=sorted_categories)

#endpoint for the edit products form. Updates the form values in the Products table according to pid and sid
@bp.route('/products/edit_product/<int:product_id>', methods=['GET','POST'])
def edit_product(product_id):
    sorted_categories = sorted(Category.get_all(), key=lambda x: x.name)
    product = Product.get(product_id)
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        altTxt = request.form["altTxt"]
        category = request.form["category"]
        updatedAt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        #users may choose not to change their image
        if request.files['image']:
            file = request.files['image']
            filename = file.filename
            filepath = os.path.join('/home/ubuntu/quokkazon/app/static/product_images', filename)
            file.save(filepath)
        else:
            filename = product.image[15:]
        
        Product.edit(product_id, name, description, "product_images/" + filename, altTxt, updatedAt, category, current_user.id)
        return redirect(url_for('inventory.inventory'))
    return render_template('editProduct.html',  categories=sorted_categories, product=product, product_id=product_id)

