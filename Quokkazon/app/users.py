from flask import render_template, redirect, url_for, flash, request, session
from werkzeug.urls import url_parse
from flask_session import Session
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp

from .models.user import User
from .models.category import Category
from .models.seller import Seller


from flask import Blueprint
bp = Blueprint('users', __name__)


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')

        return redirect(next_page)
    sorted_categories = sorted(Category.get_all(), key=lambda x: x.name)
    return render_template('login.html', title='Sign In', form=form, categories=sorted_categories)


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


@bp.route('/register', methods=['GET', 'POST'])
def register():
    sorted_categories = sorted(Category.get_all(), key=lambda x: x.name)
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.register(form.email.data,
                        form.firstname.data,
                         form.lastname.data,
                         form.address.data,
                         form.password.data,
                         form.phone_number.data
                         ):
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form, categories=sorted_categories)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))



@bp.before_request
def activate_session():
    if request.path in ['/users/search_results']:
        session.modified = True

@bp.after_request
def deactivate_session(response):
    if request.path in ['', '/users']:
        session['search_term'] = ''
    return response

ROWS = 24
@bp.route('/users/search_results', methods=['GET','POST'])
def search_results():
    sorted_categories = sorted(Category.get_all(), key=lambda x: x.name)
    page = request.args.get("page", 1, type=int)
    start = (page-1) * ROWS
    end = start + ROWS
    
    search_term = request.args.get('search_term', '')

    all_users = User.get_all()
    if request.method == 'POST':
        search_term = request.form['search_term']
        session['search_term'] = search_term
        if not search_term:
            return redirect(url_for('users.search_results'))
    
    if request.method == 'GET':
        search_term = session.get('search_term')  
    all_users = search_users(search_term)
    paginated = all_users[start:end]
    total_pages = len(all_users)//24 + 1
    return render_template('usersearchResults.html',
                            all_users = paginated,
                            search_term2 = search_term,
                            len_users = len(all_users),
                            page=page,
                            total_pages=total_pages,
                            categories=sorted_categories,
                            is_seller= Seller.is_seller(current_user))

def search_users(search_term):
    users = User.get_all()
    search_results = [user for user in users if (search_term.lower() in user.firstname.lower()) or (search_term.lower() in user.lastname.lower()) or (search_term.lower() in (user.firstname.lower() + " " + user.lastname.lower()))]
    return search_results
