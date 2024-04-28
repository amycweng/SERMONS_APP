from flask import render_template
from flask_login import current_user
from flask import request, redirect, url_for
import datetime
from .models.seller import Seller
from .models.category import Category 
from humanize import naturaltime
import os 
from .models.feedback import ProductFeedback, SellerFeedback

from flask import Blueprint
bp = Blueprint('feedback', __name__)

# note that for each page we render, we need is_seller and sorted_categories to get the right menu on the top. 

def humanize_time(dt):
    return naturaltime(datetime.datetime.now() - dt)

@bp.route('/feedback_history/<int:uid>', methods=['POST','GET'])
def my_feedback(uid):
    # render the feedback history page for a given user 
    name = SellerFeedback.get_name(uid) # name of the user 
    pfeedback = ProductFeedback.get_by_uid(uid) # get the user's feedback for products 
    pupvotes = {}
    my_pupvotes = {}
    for item in pfeedback: 
        # get the user's upvotes for product reviews 
        pupvotes[(item.uid,item.pid)] = ProductFeedback.upvote_count(item.uid,item.pid)[0][0]
    
    # get the user's feedback for sellers 
    sfeedback = SellerFeedback.get_by_uid(uid)
    supvotes = {}
    my_supvotes = {}
    for item in sfeedback:
        supvotes[(item.uid,item.sid)] = SellerFeedback.upvote_count(item.uid,item.sid)[0][0]
    is_seller=False
    # if the current user is logged in, then they can upvote reviews 
    if current_user.is_authenticated: 
        if Seller.get(current_user.id): 
            is_seller = True 
        # get the current user's upvotes for product reviews 
        for reviewer, reviewed in pupvotes:
            my_pupvotes[(reviewer,reviewed)] = ProductFeedback.my_upvote(current_user.id,reviewer,reviewed)[0][0]
        # get the current user's upvotes for seller reviews 
        for reviewer, reviewed in supvotes:
            my_supvotes[(reviewer,reviewed)] = SellerFeedback.my_upvote(current_user.id,reviewer,reviewed)[0][0]
    sorted_categories = sorted(Category.get_all(), key=lambda x: x.name)
    return render_template('myfeedback.html',
                        uid = uid,
                        name = name,
                        pfeedback=pfeedback,
                        pupvotes = pupvotes,
                        my_pupvotes = my_pupvotes,
                        my_supvotes = my_supvotes,
                        sfeedback=sfeedback,
                        supvotes=supvotes,
                        is_seller=is_seller,
                        categories=sorted_categories,
                        humanize_time=humanize_time)
    
@bp.route('/myfeedback/add/<int:product_id>/<name>', methods=['POST','GET'])
def product_submission_form(product_id,name):
    if current_user.is_authenticated:
        # this link is only accessible on the detailed order and detailed product pages 
        # if the user has purchased this product before 
        if Seller.get(current_user.id): 
            is_seller = True 
        else: 
            is_seller = False
        sorted_categories = sorted(Category.get_all(), key=lambda x: x.name)
        return render_template('myfeedback_add.html',
                                product_id=product_id,
                                is_seller=is_seller,
                                name=name,
                                type="product",
                                categories=sorted_categories,
                                humanize_time=humanize_time)
    # if the user is anonymous, go to the detailed products page 
    return redirect(url_for('products.product_detail',product_id=product_id))

@bp.route('/myfeedback/add/product', methods=['POST','GET'])
def product_add_feedback(): 
    if request.method == 'POST': 
        # this link is only accessible on the detailed order and product pages 
        # if the user has purchased this product at least once before 
        if Seller.get(current_user.id): 
            is_seller = True
        else:
            is_seller = False 
        pid = int(request.form['pid'])
        rating = int(request.form['rating'])
        review = request.form['review']
        current_dateTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # get image file and format properly 
        file = request.files['image']
        filename = file.filename
        if not filename: 
            ProductFeedback.add_feedback(current_user.id,pid,rating,review,current_dateTime, None)
        else: 
            filepath = os.path.join('/home/ubuntu/quokkazon/app/static/product_images', filename)
            file.save(filepath)
            ProductFeedback.add_feedback(current_user.id,pid,rating,review,current_dateTime, "product_images/" + filename)
        
        pfeedback = ProductFeedback.get_by_uid_pid(current_user.id, pid)
        sorted_categories = sorted(Category.get_all(), key=lambda x: x.name)
        return render_template('myfeedback_edit.html',
                            pfeedback=pfeedback,
                            is_seller=is_seller,
                            categories=sorted_categories,
                            humanize_time=humanize_time)
    
    # if the user did not click a button to get to this page, redirect them to the home page 
    return redirect(url_for('index.index'))  
   
@bp.route('/myfeedback/edit/product/<int:product_id>', methods=['POST','GET'])
def product_feedback_edit(product_id):
    if current_user.is_authenticated: 
        # go to the feedback editing page for this product 
        if Seller.get(current_user.id): 
            is_seller = True
        else:
            is_seller=False
        pfeedback = ProductFeedback.get_by_uid_pid(current_user.id, product_id)
        sorted_categories = sorted(Category.get_all(), key=lambda x: x.name)
        return render_template('myfeedback_edit.html',
                            pfeedback=pfeedback,
                            is_seller=is_seller,
                            categories=sorted_categories,
                            humanize_time=humanize_time)
    # redirect to the detailed product page if the user is anonymous 
    return redirect(url_for('products.product_detail',product_id=product_id))      
 
@bp.route('/myfeedback/edit/product_rating', methods=['POST','GET'])
def product_rating_edit():
    if request.method == "POST":
        # this link is only accessible on the Product Feedback Editing Form 
        current_dateTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        rating = int(request.form['rating'])
        pid = int(request.form['pid'])
        ProductFeedback.edit_rating(current_user.id, pid, rating, current_dateTime)
        return redirect(url_for('feedback.product_feedback_edit',product_id=pid))     
    # redirect to home page if the user did not access this page through the right buttons (i.e., just used url)
    return redirect(url_for("index.index")) 

@bp.route('/myfeedback/edit/product_review', methods=['POST','GET'])
def product_review_edit():
    if request.method == "POST":
        # this link is only accessible on the Product Feedback Editing Form 
        current_dateTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        review = request.form['review']
        pid = int(request.form['pid'])
        ProductFeedback.edit_review(current_user.id, pid, review, current_dateTime)
        return redirect(url_for('feedback.product_feedback_edit',product_id=pid))
    # redirect to home page if the user did not access this page through the right buttons (i.e., just used url)
    return redirect(url_for("index.index"))
    
@bp.route('/myfeedback/edit/product_image', methods=['POST','GET'])
def product_image_edit():
    if request.method == 'POST': 
        # this link is only accessible on the Product Feedback Editing Form 
        current_dateTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # get image file and format properly 
        file = request.files['image']
        filename = file.filename
        filepath = os.path.join('/home/ubuntu/quokkazon/app/static/product_images', filename)
        file.save(filepath)

        pid = int(request.form['pid'])
        ProductFeedback.edit_image(current_user.id, pid, "product_images/" + filename, current_dateTime)
        return redirect(url_for('feedback.product_feedback_edit',product_id=pid))
    # redirect to home page if the user did not access this page through the right buttons (i.e., just used url)
    return redirect(url_for("index.index"))
    

@bp.route('/myfeedback/delete/<int:product_id>', methods=['POST','GET'])
def product_remove_feedback(product_id):
    if current_user.is_authenticated: 
        # this link is only accessible on the Product Feedback Editing Form 
        # when a user removes their product feedback, also remove any associated upvotes 
        ProductFeedback.remove_upvotes(current_user.id,product_id)
        ProductFeedback.remove_feedback(current_user.id,product_id)
    # redirect to detailed products page if the user is anonymous and tried to access this form by url 
    return redirect(url_for('products.product_detail',product_id=product_id))
    
@bp.route('/myfeedback/delete/product_review', methods=['POST','GET'])
def product_remove_review():
    if request.method == 'POST':
        # this link is only accessible on the Product Feedback Editing Form 
        # remove upvotes as well when a user deletes their review because their feedback is no longer helpful  
        pid = int(request.form['pid'])
        current_dateTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ProductFeedback.remove_upvotes(current_user.id,pid)
        ProductFeedback.edit_review(current_user.id, pid,'',current_dateTime)
        return redirect(url_for('feedback.product_feedback_edit',product_id=pid))
    # redirect to home page if the user did not access this page through the right buttons (i.e., just used url)
    return redirect(url_for("index.index"))
    
    
@bp.route('/myfeedback/delete/image', methods=['POST','GET'])
def product_remove_image():
    if request.method == 'POST': 
        # this link is only accessible on the Product Feedback Editing Form 
        # remove the user's image for a product review 
        pid = int(request.form['pid'])
        current_dateTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ProductFeedback.edit_image(current_user.id, pid,'',current_dateTime)
        return redirect(url_for('feedback.product_feedback_edit',product_id=pid))
    # redirect to home page if the user did not access this page through the right buttons (i.e., just used url)
    return redirect(url_for("index.index"))
    
@bp.route('/productfeedback/remove_upvote', methods=['POST','GET'])
def remove_upvote_product_review():
    if request.method == "POST":
        # this link is only accessible on the Product Feedback Editing Form 
        # remove the user's upvote for a product review 
        reviewer =  int(request.form['reviewer'])
        product = int(request.form['reviewed'])
        page = request.form['page']
        ProductFeedback.remove_my_upvote(current_user.id,reviewer,product)
        if page == "myfeedback":
            # accessed this function via the private feedback history page 
            return redirect(url_for('feedback.my_feedback',uid=current_user.id))
        elif page == "publicfeedback":
            # accessed this function via a public feedback history page 
            uid = int(request.form['uid'])
            return redirect(url_for('feedback.my_feedback',uid=uid))
        # accessed this function via a detailed product page 
        return redirect(url_for('products.product_detail',product_id=product))
    # redirect to home page if the user did not access this page through the right buttons (i.e., just used url)
    return redirect(url_for("index.index"))
    
@bp.route('/productfeedback/upvote', methods=['POST','GET'])
def upvote_product_review():
    if request.method == "POST":
        # this link is only accessible on the Product Feedback Editing Form 
        # upvote a product review 
        reviewer =  int(request.form['reviewer'])
        product = int(request.form['reviewed'])
        page = request.form['page']
        ProductFeedback.add_my_upvote(current_user.id,reviewer,product)
        if page == "myfeedback":
            # accessed this function via the private feedback history page 
            return redirect(url_for('feedback.my_feedback',uid=current_user.id))
        elif page == "publicfeedback":
            # accessed this function via a public feedback history page 
            uid = int(request.form['uid'])
            return redirect(url_for('feedback.my_feedback',uid=uid))
        # accessed this function via a detailed product page 
        return redirect(url_for('products.product_detail',product_id=product))
    # redirect to home page if the user did not access this page through the right buttons (i.e., just used url)
    return redirect(url_for("index.index"))
    

@bp.route('/myfeedback/edit/seller/<int:seller_id>', methods=['POST','GET'])
def seller_feedback_edit(seller_id):
    # edit feedback for a seller 
    if current_user.is_authenticated:
        if Seller.get(current_user.id): 
            is_seller = True 
        else:
            is_seller = False
        sfeedback = SellerFeedback.get_by_uid_sid( # sorted by rating 
                        current_user.id, seller_id)
        sorted_categories = sorted(Category.get_all(), key=lambda x: x.name)
        return render_template('myfeedback_edit.html',
                            sfeedback=sfeedback,
                            is_seller=is_seller,
                            categories=sorted_categories,
                            humanize_time=humanize_time)
    # redirect to the seller's public profile if the user is anonymous 
    return redirect(url_for('feedback.public_profile',user_id=seller_id))

@bp.route('/myfeedback/edit/seller_rating', methods=['POST','GET'])
def seller_rating_edit():
    # edit the rating for a seller 
    if request.method == 'POST': 
        # this button will only appear on the Seller Feedback Editing Form 
        current_dateTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        rating = int(request.form['rating'])
        sid = int(request.form['sid'])
        SellerFeedback.edit_rating(current_user.id, sid, rating, current_dateTime)
        return redirect(url_for('feedback.seller_feedback_edit',seller_id=sid))
    # redirect to home page if the user did not access this page through the right buttons (i.e., just used url)
    return redirect(url_for("index.index"))
    
@bp.route('/myfeedback/edit/seller_review', methods=['POST','GET'])
def seller_review_edit():
    # edit the review for a seller 
    if request.method == 'POST': 
        # this button will only appear the Seller Feedback Editing Form 
        current_dateTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        review = request.form['review']
        sid = int(request.form['sid'])
        SellerFeedback.edit_review(current_user.id, sid, review, current_dateTime)
        return redirect(url_for('feedback.seller_feedback_edit',seller_id=sid))
    # redirect to home page if the user did not access this page through the right buttons (i.e., just used url)
    return redirect(url_for("index.index"))
    
@bp.route('/myfeedback/delete', methods=['POST','GET'])
def seller_remove_feedback():
    # remove my feedback entirely for a seller 
    if request.method == 'POST':
        # this button will only appear on the seller's public profile page 
        # and the detailed order page if the user has purchased from this seller before 
        sid = int(request.form['sid'])
        SellerFeedback.remove_upvotes(current_user.id, sid)
        SellerFeedback.remove_feedback(current_user.id,sid)
        return redirect(url_for('feedback.public_profile',user_id=sid))
    # redirect to home page if the user did not access this page through the right buttons (i.e., just used url)
    return redirect(url_for("index.index"))
    
@bp.route('/myfeedback/delete/seller_review', methods=['POST','GET'])
def seller_remove_review():
    # only remove my review for the seller 
    if request.method == 'POST': 
        # this button will only appear on the seller's public profile page 
        # and the detailed order page if the user has purchased from this seller before 
        seller_id = int(request.form['sid'])
        current_dateTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        SellerFeedback.remove_upvotes(current_user.id, seller_id)
        SellerFeedback.edit_review(current_user.id, seller_id,'',current_dateTime)
        return redirect(url_for('feedback.seller_feedback_edit',seller_id=seller_id))
    # redirect to home page if the user did not access this page through the right buttons (i.e., just used url)
    return redirect(url_for("index.index"))
    
@bp.route('/myfeedback/add/seller', methods=['POST','GET'])
def seller_add_feedback():
    # add new feedback for this seller 
    if request.method == 'POST': 
        # this button will only appear on the seller's public profile page 
        # and the detailed order page if the user has purchased from this seller before 
        # and the user currently does not have any feedback for this seller already 
        if Seller.get(current_user.id):
            is_seller = True
        else: 
            is_seller = False
        sid = int(request.form['sid'])
        rating = int(request.form['rating'])
        review = request.form['review']
        current_dateTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        SellerFeedback.add_feedback(current_user.id,sid,rating,review,current_dateTime)
        sfeedback = SellerFeedback.get_by_uid_sid(current_user.id, sid)
        sorted_categories = sorted(Category.get_all(), key=lambda x: x.name)
        return render_template('myfeedback_edit.html',
                            sfeedback=sfeedback,
                            is_seller=is_seller,
                            categories=sorted_categories,
                            humanize_time=humanize_time)
    # redirect to home page if the user did not access this page through the right buttons (i.e., just used url)
    return redirect(url_for("index.index"))
    

@bp.route('/myfeedback/add/<int:seller_id>', methods=['POST','GET'])
def seller_submission_form(seller_id):
    if current_user.is_authenticated: 
        if Seller.get(current_user.id):
            is_seller = True
        else: 
            is_seller = False
        name = SellerFeedback.get_name(seller_id)
        sorted_categories = sorted(Category.get_all(), key=lambda x: x.name)
        # render the seller feedback submission form 
        return render_template('myfeedback_add.html',
                                seller_id=seller_id,
                                is_seller = is_seller,
                                name=name,
                                type="seller",
                                categories=sorted_categories,
                                humanize_time=humanize_time)
    # redirect to home page if the user did not access this page through the right buttons (i.e., just used url)
    return redirect(url_for("index.index"))
    

@bp.route('/sellerfeedback/remove_upvote', methods=['POST','GET'])
def remove_upvote_seller_review():
    if request.method == "POST":
        reviewer =  int(request.form['reviewer'])
        seller = int(request.form['seller'])
        SellerFeedback.remove_my_upvote(current_user.id,reviewer,seller)
        page = request.form['page']
        if page == "myfeedback":
            # accessed this function via the private feedback history page 
            return redirect(url_for('feedback.my_feedback',uid=current_user.id))
        elif page == "publicfeedback":
            # accessed this function via a public feedback history page 
            uid = int(request.form['uid'])
            return redirect(url_for('feedback.my_feedback',uid=uid))
        elif page=="myprofile":
            # accessed this function via the private profile page 
            return redirect(url_for('profile.my_profile'))
        # accessed this function through a public profile page 
        return redirect(url_for('feedback.public_profile',user_id=seller))
    # redirect to home page if the user did not access this page through the right buttons (i.e., just used url)
    return redirect(url_for("index.index"))
    
@bp.route('/sellerfeedback/upvote', methods=['POST','GET'])
def upvote_seller_review():
    if request.method == "POST":
        reviewer =  int(request.form['reviewer'])
        seller = int(request.form['seller'])
        SellerFeedback.add_my_upvote(current_user.id,reviewer,seller)
        page = request.form['page']
        if page == "myfeedback":
            # accessed this function via the private feedback history page 
            return redirect(url_for('feedback.my_feedback',uid=current_user.id))
        elif page == "publicfeedback":
            # accessed this function via a public feedback history page 
            uid = int(request.form['uid'])
            return redirect(url_for('feedback.my_feedback',uid=uid))
        elif page=="myprofile":
            # accessed this function via the private profile page 
            return redirect(url_for('profile.my_profile'))
        # accessed this function through a public profile page
        return redirect(url_for('feedback.public_profile',user_id=seller))
    # redirect to home page if the user did not access this page through the right buttons (i.e., just used url)
    return redirect(url_for("index.index"))
        
@bp.route('/public_profile/<int:user_id>', methods=['POST','GET'])
def public_profile(user_id):
    # variable that holds a summary of ratings if it exists 
    summary = None
    # if the current logged-in user viewing this page is a seller or not 
    is_seller = False 
    # get all feedback for the given user (empty if the user is not a seller)
    sfeedback = SellerFeedback.get_by_sid(user_id)
    # get all feedback for the given user sorted by upvotes (empty if the user is not a seller)
    sorted_by_upvotes = SellerFeedback.sorted_by_upvotes(user_id)
    # upvotes for reviews about this seller 
    supvotes = {}
    for item in sfeedback:
        supvotes[(item.uid,item.sid)] = SellerFeedback.upvote_count(item.uid,item.sid)[0][0]
    # get top three most popular reviews 
    top3 = []
    count = 0
    for item in sorted_by_upvotes: 
        top3.append(item)
        count += 1 
        if count == 3: break
    
    # if the current user is logged in, get their upvotes (if any) for the reviews about this user (if the user is a seller)
    myupvotes = {}
    if current_user.is_authenticated: 
        # if the current user is a seller 
        if Seller.get(current_user.id):
            is_seller = True
        # whether the current logged-in user has purchased from this seller before 
        has_purchased  = SellerFeedback.has_purchased(current_user.id,user_id)
        if has_purchased is not None: 
            my_seller_feedback = SellerFeedback.get_by_uid_sid(current_user.id, user_id)
        else: 
            # the user has not purchased from this seller before 
            has_purchased = False
            my_seller_feedback = False
        # which reviews the current user has upvoted 
        for reviewer,seller in supvotes: 
            myupvotes[(reviewer,seller)] = SellerFeedback.my_upvote(current_user.id,reviewer,seller)[0][0]
    else: 
        has_purchased, my_seller_feedback = False, False

    # check if user is a seller 
    user_is_seller = Seller.get(user_id)
    if user_is_seller is not None: 
        if Seller.has_products(user_id):
            summary = SellerFeedback.summary_ratings(user_id)    
        user_is_seller = True
    else: 
        user_is_seller = False 
    
    # user's information 
    info = Seller.find(user_id)
    # summary of the feedback that the user has left for products and sellers
    feedback_for_other_sellers = SellerFeedback.user_summary_ratings(user_id)
    feedback_for_products = ProductFeedback.user_summary_ratings(user_id)
    sorted_categories = sorted(Category.get_all(), key=lambda x: x.name)
    return render_template('publicProfile.html',
                            sfeedback=sfeedback,
                            supvotes=supvotes,
                            myupvotes=myupvotes,
                            summary=summary,
                            user_is_seller=user_is_seller,
                            categories=sorted_categories,
                            is_seller=is_seller,
                            user_id=user_id,
                            top3=top3,
                            first_name = info[2],
                            last_name = info[3],
                            email = info[1],
                            humanize_time=humanize_time,
                            has_purchased = has_purchased,
                            my_seller_feedback=my_seller_feedback,
                            feedback_for_other_sellers=feedback_for_other_sellers,
                            feedback_for_products=feedback_for_products)