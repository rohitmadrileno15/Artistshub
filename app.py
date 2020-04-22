
# A very simple Flask Hello World app for you to get started with...

from flask import Flask
import random
import random,string
from flask import Flask,redirect, url_for,render_template, request,session,flash
import os
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime

from flask_wtf import FlaskForm
from flask_wtf.file import FileField , FileAllowed
from wtforms import StringField , PasswordField,SubmitField
from wtforms.validators import DataRequired,Length, Email , EqualTo, ValidationError
from flask_login import LoginManager, UserMixin, login_user,current_user,logout_user,login_required

from wtforms.widgets import TextArea






app = Flask(__name__)

app.config['SECRET_KEY'] = '450933c08c5ab75e79619102eddf47dee813a9d6'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)



login_manager = LoginManager(app)



class User(db.Model , UserMixin):
    id = db.Column(db.Integer,primary_key= True)
    username = db.Column(db.String(15), unique= True, nullable = False)
    email = db.Column(db.String(120), unique= True, nullable = False)

    password = db.Column(db.String(60), nullable = False)
    #posts = db.relationship("Post", backref = 'author' , lazy = True)


    def __repr__(self):
        a = User('{self.username}','{self.email}')
        return (a)


class Post(db.Model):
    id = db.Column(db.Integer,primary_key= True)
    title = db.Column(db.String(300), nullable = True)
    caption = db.Column(db.String(3400), nullable = False)
    picture = db.Column(db.String(300))
    author = db.Column(db.String(50), nullable = False)
    date_posted = db.Column(db.DateTime, default = datetime.utcnow )
    user_personal_id = db.Column(db.Integer)



    def __repr__(self):
        return Post('{self.caption}','{self.picture}','{self.date_posted}')


@login_manager.user_loader

def load_user(user_id):
    return (User.query.get(int(user_id)))

class RegistrationForm(FlaskForm):

    username = StringField('UserName' , validators = [DataRequired() , Length(min = 3, max = 14)])
    email = StringField('Email' , validators = [DataRequired() , Email()])
    password = PasswordField('Password' , validators = [DataRequired()])
    Confirm_password = PasswordField('Confirm Password' , validators = [DataRequired() , EqualTo('password')])
    submit = SubmitField('Sign Up!')


class LoginForm(FlaskForm):
    email = StringField('Email' , validators = [DataRequired() , Email()])
    password = PasswordField('Password' , validators = [DataRequired()])

    submit = SubmitField('Log in.')

@app.route("/" )
@app.route("/main" )

def home():
    return render_template('index.html' )


@app.route("/aboutsection_know_more" )

def aboutknowmore():
    return render_template('aboutknowmore.html' )


@app.route("/notes_from_dev" )

def notes():
    return render_template('notes_.html' )



@app.route("/posts" )
def index():

    posts = Post.query.all()
    out = []
    post_picture = Post.query.with_entities(Post.picture).all()

    posts.reverse()
    for t in post_picture:
        for x in t:
            out.append(x)

    out.reverse()



    return render_template('home.html', posts = posts , post_picture=out)




@app.route("/register", methods = ['GET' , "POST"] )

def register():

    form = RegistrationForm()

    if (form.validate_on_submit()):
        ##hashing passwords
        hashed_pwd = form.password.data
        user = User(username = form.username.data ,email = form.email.data, password = hashed_pwd)
        u = form.username.data
        e = form.email.data
        user1 = User.query.filter_by(username =  u ).first()
        user2 = User.query.filter_by(email = e).first()

        if (user1 or user2):
            return ("<h1> Credentials already taken!  </h1>")
        else:
            db.session.add(user)
            db.session.commit()

            flash('Your account has been created, Login!' , 'success')
            return redirect(url_for('login'))




    else:
        return render_template('register.html' ,type ='Register', title = 'Register' , form = form )



@app.route("/login" , methods = ['GET' , "POST"])

def login():
    if (current_user.is_authenticated):
        return redirect(url_for('index'))

    form = LoginForm()
    if (form.validate_on_submit() ):
        user = User.query.filter_by(email = form.email.data).first()
        if(user and (user.password == form.password.data)):
            login_user(user , remember = False)
            next_page = request.args.get('next')
            return redirect(next_page) if (next_page) else (redirect(url_for('index')))
        else:
            return ("<br> <h1>You have entered wrong credentials for Logging in.</h1><br> <p>Go back and    Log in Again! </p>")

    else:
        return render_template('login.html' , type = 'Log in', title = 'Log in',form = form )


#putting this here because login is just above it

login_manager.login_view  = 'login'
login_manager.login_message_category = 'info'


@app.route("/loggedout" )

def logout():
    logout_user()
    return redirect(url_for('home'))




class UpdateAccountForm(FlaskForm):

    username = StringField('UserName' , validators = [DataRequired() , Length(min = 3, max = 14)])

    submit = SubmitField('Update')

    def validate_username(self,username):

        if (username.data != current_user.username):
            user = User.query.filter_by(username = username.data).first()
            if (user):
                raise ValidationError('Username already Taken!')

@app.route("/account_user", methods = ['GET' , "POST"] )
@login_required
def account_of_users():
    id_of_user = current_user.id
    posts__ = Post.query.filter_by(user_personal_id = id_of_user).all()
    no_of_images = len(posts__)
    formnew = UpdateAccountForm()
    if (formnew.validate_on_submit()):

        current_user.username = formnew.username.data
        db.session.commit()
        return redirect(url_for('account_of_users'))

    elif (request.method == 'GET'):
        formnew.username.data = current_user.username


    return render_template('profile.html', no_of_posts = no_of_images , form = formnew  )


class UploadForm(FlaskForm):
    title = StringField('Title',validators = [DataRequired() , Length(min = 1, max = 300)])
    caption = StringField('Write-Up' , widget = TextArea())
    image_url = FileField('Image File')
    submit = SubmitField ("Upload")




def save_picture(form_picture):
    hashed_caption = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])

    f_name,f_ext = os.path.splitext(form_picture.filename)
    fn = hashed_caption+f_name
    picture_fn = fn + f_ext
    picture_path = os.path.join(app.root_path , 'static' , picture_fn)
    form_picture.save(picture_path)
    return picture_fn


@app.route("/account_user_upload", methods = ["GET" ,  "POST"] )
@login_required
def upload_new():
    form = UploadForm()
    pic_list = ["blog_pic.png","blog_pic2.jpg","blog_pic3.png","blog_pic4.png","blog_pic5.jpg"]

    if (form.validate_on_submit()):
        c = form.caption.data
        t = form.title.data
        img = form.image_url.data
        if ( img == ""):
            picture_file = random.choice(pic_list)
        else:
            picture_file = save_picture(form.image_url.data)



        print("done")
        newFile = Post(title = t , caption = c , picture = picture_file  ,author = current_user.username, user_personal_id = current_user.id )
        db.session.add(newFile)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('upload.html', form = form )



@app.route("/image_gallery_user_upload" )
@login_required
def image_gallery():
    id_of_user = current_user.id
    posts_ = Post.query.filter_by(user_personal_id = id_of_user).all()



    posts_.reverse()


    print()



    return render_template('image_gallery.html', posts = posts_ )











if __name__ == '__main__':
    app.run(debug= True)


