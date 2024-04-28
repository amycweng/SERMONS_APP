from flask import render_template
from flask import redirect, request, url_for, session
from flask_session import Session
from flask_login import current_user
from humanize import naturaltime
import datetime
from collections import defaultdict
import os, random
from .products import apply_sort

from .models.product import Product, ProductRating
from .models.feedback import ProductFeedback
from .models.inventory import Inventory
from .models.stock import Stock
from .models.category import Category
from .models.seller import Seller

from flask import Blueprint
bp = Blueprint('categories', __name__)

#human readable time
def humanize_time(dt):
    return naturaltime(datetime.datetime.now() - dt)

# number of items on each page is 24
ROWS = 24

# function used to display the products filtered by category using the same products template
@bp.route('/<category_id>', methods=['GET','POST'])
def category_products(category_id):
    # defining the page and items on page
    page = request.args.get("page", 1, type=int)
    start = (page-1) * ROWS
    end = start + ROWS
    
    cat_items = Product.get_all_by_cat(category_id)
    category = Category.get_name(category_id)
    inventory = Inventory.get_all()
    product_prices = defaultdict(list)
    summary = defaultdict(list)
    
    # filtering and sorting based on the page request
    if request.method == 'GET':
        filter_by = request.args.get('filter_by') if request.args.get('filter_by') is not None else 'all'
        sort_by = request.args.get('sort_by') if request.args.get('sort_by') is not None else 'a-z'
        if sort_by == "top_reviews": 
            items = ProductRating.all_ratings_cid(category_id) #reviews are available for available products
        elif sort_by == "low_price":
            items = Stock.get_stock_by_cat_asc(category_id) #price is available for in-stock
        elif sort_by == "high_price":
            items = Stock.get_stock_by_cat_desc(category_id) #price is available for in-stock
        else: # sorting by alphabet is ok both in and not in stock
            if filter_by == "available":
                items = apply_sort(Stock.get_stock_by_cat(category_id), sort_by) 
            else:
                items = apply_sort(cat_items, sort_by)
    
    #retrieving prices and ratings for each product from inventory and feedback tables
    for item in inventory:
        product_prices[item.pid].append(item.price)
        summary[item.pid] = ProductFeedback.summary_ratings(item.pid)

    paginated = items[start:end]
    total_pages = len(items)//24 + 1
    
    #retrieving categories from category table
    sorted_categories = sorted(Category.get_all(), key=lambda x: x.name)
    
    return render_template('products.html', items=paginated,
                      inventory=inventory, 
                      summary=summary,
                      product_prices = product_prices,
                      page=page,
                      total_pages=total_pages,
                      categories=sorted_categories,
                      category=category,
                      is_seller=Seller.is_seller(current_user))
    
    
