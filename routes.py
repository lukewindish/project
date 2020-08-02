import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from comm import app, db, bcrypt
from comm.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from comm.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/home") #Route for home page
def home():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    #displays every post in Post data base by date and paginates it for 5
    return render_template('home.html', posts=posts)

@app.route("/register", methods=['GET', 'POST'])#route for register page
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()#initiate form
    if form.validate_on_submit():#on submition, encrypts passowrd and adds data to database
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)#add user to database, then commit changes
        db.session.commit()
        #flash message confirms to user it was successful
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))#route for login page
    form = LoginForm()#Initializes form
    if form.validate_on_submit():#checks to see if form is valid
        user = User.query.filter_by(email=form.email.data).first() #checks if user and password match
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout") #route for logout for user
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture): #function to save pictures for profile pictures
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125) #Makes pictre size smaller
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

def save_picture2(form_picture): #function to save pictures for posts
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/post_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

#Route for account link
@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm() #shows form to update account
    if form.validate_on_submit():
        if form.picture.data: #if submit new pic, saves and changes
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route("/post/new",methods=['GET', 'POST'])
@login_required
def new_post(): #route for creating new posts
    form = PostForm()
    if form.validate_on_submit():
        if form.pic.data:
            picture_file = save_picture2(form.pic.data)
        #line 117 is where post is added to data base with all of data submitted
        post = Post(title = form.title.data, content = form.content.data, price = form.price.data, contact = form.contact.data, post_image= picture_file, author = current_user)
        db.session.add(post)
        db.session.commit() #adds then commit data to database
        flash("Your post was successful!", 'success')
        return redirect(url_for("home"))
    return render_template('create_post.html', title='New Post',form=form, legend="New Post")


@app.route("/post/<post_id>")#route for looking at specific post
def post(post_id):
    post = Post.query.get_or_404(post_id) #throws 404 if not found
    return render_template("post.html",title=post.title,post=post)

@app.route("/post/<post_id>/update",methods=['GET', 'POST'])
@login_required
def update_post(post_id): #route for updating or deleting post if current user made that post
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit(): #updates all form content for that post
        post.title = form.title.data
        post.content = form.content.data
        post.price = form.price.data
        post.contact = form.contact.data
        post.post_image = save_picture2(form.pic.data)
        db.session.commit()
        #resubmits form if updating
        flash("Your post has been updated!","success")
        return redirect(url_for('post',post_id = post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
        form.price.data = post.price
        form.contact.data = post.contact
    return render_template('create_post.html', title='Update Post',form=form,legend="Update Post")

@app.route("/post/<post_id>/delete",methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403) #submits 403 error if post author isnt logged in
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been deleted!","success")
    return redirect(url_for('home'))

@app.route("/user/<string:username>")
def user_posts(username): #shows all posts by certain username
    page = request.args.get("page", 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts,user=user)
