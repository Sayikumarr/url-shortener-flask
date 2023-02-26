import random
import string
from flask import Flask,render_template,request,redirect,make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

# To evaluate the name of the current module
app = Flask(__name__)
app.debug = True

# adding configuration for using a sqlite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Students_Auth.db'

app.config['SECRET_KEY'] = 'sai@123'

db = SQLAlchemy(app)

#Class containing the details of user table
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    password = db.Column(db.String(20), unique = False, nullable = False)
    fullName = db.Column(db.String(30), nullable = False)
    email = db.Column(db.String(50), unique = True)
    # urls = db.relationship("Url", backref="user")

    # Special method to represent class objects as a string
    def __repr__(self):
        return f"ID : {self.id}, Username: {self.username}"

# Class containing child table 'url' 
class Url(db.Model):
    __tablename__ = 'url'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    or_url = db.Column(db.String(2048), nullable = False)
    short_url = db.Column(db.String(8), unique = True, nullable = False)
    
    # Special method to represent class objects as string
    def __repr__(self):
        return f"User ID : {self.user_id}, Shortened URL: {self.short_url}"

# To generate the token
def generate_auth_token(user):
    return jwt.encode({ 'id': user.id },app.config['SECRET_KEY'], algorithm='HS256')

# To verify the token
def verify_auth_token(token):
    try:
        #HS256 is a symmetric algorithm that shares one secret key between the identity provider and your application
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    except:
        return
    return User.query.filter(User.id==data['id']).first()

#Decorator for login part
def login_check(func):
    def inner():
        token = request.cookies.get("token")
        if verify_auth_token(token):
            return func()
        else:
            return signin()
    return inner

@app.route("/")
def home():
    user = verify_auth_token(request.cookies.get("token"))
    return render_template("home.html",user=user)

@app.route("/signin",methods=['GET','POST'])
def signin():
    user = verify_auth_token(request.cookies.get("token"))
    if not user:
        if request.method=="POST":
            username=request.form.get("username")
            pwd=request.form.get("pwd")
            user = User.query.filter(User.username==username).one()
            valid = False
            if user is not None:
                if check_password_hash(user.password,pwd):
                    valid = True
                    response = make_response(redirect('/'))
                    response.set_cookie('token',generate_auth_token(user))
                    return response
            if not valid:
                    return render_template('signin.html',msg='Invalid User or Password!')
        return render_template("signin.html")
    else:
        return redirect('/')

@app.route("/signup",methods=['GET','POST'])
def signup():
    user = verify_auth_token(request.cookies.get("token"))
    if not user:
        if request.method=="POST":
            name=request.form.get("fname")
            email=request.form.get("email")
            username=request.form.get("username")
            pwd=request.form.get("pwd")
            if ((User.query.filter(User.username==username).first() is None) and (User.query.filter(User.email==email).first() is None)):
                user = User(username=username,password=generate_password_hash(pwd),fullName=name,email=email)
                db.session.add(user)
                db.session.commit()
                response = make_response(redirect('/'))
                response.set_cookie('token',generate_auth_token(user))
                return response
            else:
                return render_template("signup.html",msg='User already exists')
        return render_template("signup.html")
    else:
        return redirect('/')

@app.route("/signout")
def signout():
    domain = request.host
    resp = make_response(redirect('/'))
    resp.delete_cookie('token',path='/', domain=domain)
    return resp


# To view or add the URLs
@app.route('/dashboard',methods=['GET','POST'])
@login_check
def dashboard():
    user = verify_auth_token(request.cookies.get("token"))
    user_urls = Url.query.filter(Url.user_id==user.id)
    if request.method=='POST':
        url = request.form.get('url')
        # Check if the URL is already in the database
        existing_url = user_urls.filter_by(or_url=url).first()
        if existing_url:
            return '<h1>URL already EXISTS</h1>'
        else:
            # Generate a random string of characters to use as the shortened URL
            short_url = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            while Url.query.filter_by(short_url=short_url).first():
                short_url = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            new_url = Url(short_url=short_url,or_url=url,user_id=user.id)
            db.session.add(new_url)
            db.session.commit()
            return redirect('/dashboard')
    url_set = user_urls.all()
    return render_template('data.html',data=url_set,user=user)

@app.route('/<short_url>', methods=['GET'])
def redirect_url(short_url):
    url = Url.query.filter_by(short_url=short_url).first()
    if url:
        return redirect(url.or_url)
    else:
        return "Invalid URL"

def main():
    with app.app_context():
        db.create_all()
    app.run()

if "__main__"==__name__:
    main()