from flask import render_template
from flask_login import current_user
from flask import request, redirect, url_for
import datetime
from .models.feedback import SellerFeedback
from .models.seller import Seller
from humanize import naturaltime

from .models.messages import Messages
from .models.category import Category
from flask import Blueprint
bp = Blueprint('messages', __name__)

def humanize_time(dt):
    return naturaltime(datetime.datetime.now() - dt)

# we need is_seller and sorted_categories in each function that renders a template because we need the header to be consistent 

@bp.route('/my_message_history', methods=['POST','GET'])
def my_messages():
    # inbox of message threads (with links to each thread in a table)
    if current_user.is_authenticated: 
        if Seller.get(current_user.id):
            is_seller=True
        else: 
            is_seller = False
        interacted = Messages.has_message(current_user.id)
        sorted_categories = sorted(Category.get_all(), key=lambda x: x.name)
        return render_template('mymessages.html',
                        interacted=interacted,
                        categories=sorted_categories,
                        is_seller=is_seller,
                        humanize_time=humanize_time)
    # user is anonymous 
    return redirect(url_for('index.index'))

@bp.route('/my_message_history/<int:other_user>', methods=['POST','GET'])
def message_thread(other_user):
    # user's message history with another user 
    if current_user.is_authenticated: 
        if Seller.get(current_user.id):
            is_seller = True
        else:
            is_seller = False
        sorted_categories = sorted(Category.get_all(), key=lambda x: x.name)
        messages = Messages.message_thread(current_user.id,other_user)
        other_user_name = SellerFeedback.get_name(other_user)
        return render_template('messages.html',
                            messages=messages,
                            is_seller = is_seller,
                            other_user=other_user,
                            categories=sorted_categories,
                            other_user_name=other_user_name,
                            humanize_time=humanize_time)
    # user is anonymous 
    return redirect(url_for('index.index'))

@bp.route('/new_message', methods=['POST','GET'])
def new_message():
    if request.method == "POST":
        # this function must be accessed via the button in a private message thread 
        other_user = int(request.form['other_user'])
        msg = request.form['message']
        current_dateTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        Messages.new_message(current_user.id,other_user,current_dateTime,msg)
        return redirect(url_for('messages.message_thread',other_user=other_user))
    # if a user enters this url, redirect them to the home page 
    return redirect(url_for('index.index'))
