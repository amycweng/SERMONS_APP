
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required

from flask import Blueprint
bp = Blueprint('profile', __name__)

from .models.seller import Seller
from .models.feedback import SellerFeedback, ProductFeedback
from .models.purchase import Purchase
from .models.product import Product
from .models.category import Category
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp
from humanize import naturaltime
import datetime
import pandas as pd
import plotly
import plotly.express as px
import json
from .models.user import User

# List of month abbreviations for analytics graph
MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

def humanize_time(dt):
    return naturaltime(datetime.datetime.now() - dt)

# User personal page
@bp.route('/myprofile')
@login_required
def my_profile():
    a = Seller.get(current_user.id)
    sfeedback = None
    order_count_graph, order_freq_graph, ratings_graph = None, None, None
    supvotes = {}
    myupvotes = {}
    summary = None
    if a is None: 
        is_seller = False
    else:
        is_seller = True

        # Create a graph for top selling products by count for a particular seller
        order_counts = Purchase.get_order_counts_by_sid(current_user.id)
        if order_counts:
            oc_df = pd.DataFrame(order_counts[:min(len(order_counts), 10)], columns=['ID','Product','Count sold'])
            oc_fig = px.bar(oc_df, x='Product', y='Count sold', title='Top Selling Products', text_auto=True, color_discrete_sequence=['#8E7618'])
            order_count_graph = json.dumps(oc_fig, cls=plotly.utils.PlotlyJSONEncoder)

        # Create a graph for the total number orders over time for a particular seller across all products
        orders_freq = [[f'{MONTHS[row[0]-1]} {row[1]}',row[2]] for row in Purchase.get_num_orders_per_month(current_user.id)]
        plot_graph = False
        for row in orders_freq:
            if row[1] != 0:
                plot_graph = True
                break
        if plot_graph:
            of_df = pd.DataFrame(orders_freq, columns=['Month','Count'])
            of_fig = px.line(of_df, x='Month',y='Count',title='Total Number of Orders Per Month')
            order_freq_graph = json.dumps(of_fig, cls=plotly.utils.PlotlyJSONEncoder)

        # Create a graph for the average seller rating over time by month
        num_ratings, sum, avg_ratings = 0, 0, []
        ratings_freq = SellerFeedback.get_seller_ratings(current_user.id)
        if ratings_freq:
            m = ratings_freq[0][0]
            y = ratings_freq[0][1]
            current_year = datetime.datetime.now().year
            current_month = datetime.datetime.now().month
            i = 0
            while m <= 12 and y < current_year or m <= current_month and y == current_year:
                while len(ratings_freq) > 0 and ratings_freq[0][0] == m and ratings_freq[0][1] == y:
                    sum += ratings_freq[0][2]
                    num_ratings += 1
                    ratings_freq.pop(0)
                avg_ratings.append([f'{MONTHS[int(m)-1]} {y}', float(sum/num_ratings)])
                m += 1
                if m > 12:
                    m = 1
                    y += 1
            rt_df = pd.DataFrame(avg_ratings, columns=['Month','Rating'])
            rt_fig = px.line(rt_df, x='Month',y='Rating',title='Average Rating Over Time')
            rt_fig.update_traces(line=dict(color='red'))
            ratings_graph = json.dumps(rt_fig, cls=plotly.utils.PlotlyJSONEncoder)

    sfeedback = SellerFeedback.get_by_sid(current_user.id)
    supvotes = {}
    myupvotes = {}
    sorted_by_upvotes = SellerFeedback.sorted_by_upvotes(current_user.id)
    for item in sfeedback:
        supvotes[(item.uid,item.sid)] = SellerFeedback.upvote_count(item.uid,item.sid)[0][0]
    summary = SellerFeedback.summary_ratings(current_user.id)
    if summary[0] is None: 
        summary = None 
    for reviewer,seller in supvotes: 
        myupvotes[(reviewer,seller)] = SellerFeedback.my_upvote(current_user.id,reviewer,seller)[0][0]
    count = 0
    top3 = []
    for item in sorted_by_upvotes: 
        top3.append(item)
        count += 1 
        if count == 3: break

    feedback_for_other_sellers = SellerFeedback.user_summary_ratings(current_user.id)
    feedback_for_products = ProductFeedback.user_summary_ratings(current_user.id)
    sorted_categories = sorted(Category.get_all(), key=lambda x: x.name)
    # The user information will be loaded from the current_user proxy
    return render_template('myprofile.html',
                            is_seller = is_seller,
                           title='My Profile',
                           order_count_graph=order_count_graph,
                           order_freq_graph=order_freq_graph,
                           ratings_graph=ratings_graph,
                           sfeedback = sfeedback,
                           supvotes=supvotes,
                           my_supvotes=myupvotes,
                           top3=top3,
                           summary = summary,
                           current_user=current_user,
                           feedback_for_other_sellers=feedback_for_other_sellers,
                           feedback_for_products=feedback_for_products,
                           humanize_time=humanize_time,
                           categories=sorted_categories)

# Registers a user as a seller
@bp.route('/register_seller')
@login_required
def reg_seller():
    Seller.add_seller(current_user.id)
    # The user information will be loaded from the current_user proxy
    return redirect(url_for('profile.my_profile'))

class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Regexp('^[0-9]*$', message='Phone number must contain only numbers')])
    submit = SubmitField('Register')
        
    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')

# Allows for personal info to be changed
@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    sorted_categories = sorted(Category.get_all(), key=lambda x: x.name)
    form = RegistrationForm()
    if request.method == 'POST':
        # Retrieve form data
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        phone_number = request.form.get('phone_number').replace('(','').replace(')','').replace('-','').replace(' ','').replace('+','')
        address = request.form.get('address')
        if len(firstname.strip()) == 0 or len(email.strip()) == 0 or len(phone_number.strip()) != 10 or len(address.strip()) == 0:
            return render_template('edit_profile.html', categories=sorted_categories, error=True)
        User.update_user_info(current_user.id, email, firstname, lastname, address, phone_number, password)
        #flash('Profile updated successfully!')
        return redirect(url_for('profile.my_profile'))
    return render_template('edit_profile.html', categories=sorted_categories, error=False)


# Allows for balance to be topped-up
@bp.route('/top_up', methods=['GET', 'POST'])
@login_required
def top_up():
    sorted_categories = sorted(Category.get_all(), key=lambda x: x.name)
    if request.method == 'POST':
        # Retrieve form data
        added_money = request.form.get("added_money")
        if User.top_up(current_user.id, current_user.balance, added_money):
            return redirect(url_for('profile.my_profile'))
        else:
            return render_template('top_up.html',error=True)
    return render_template('top_up.html',error=False, categories=sorted_categories)
