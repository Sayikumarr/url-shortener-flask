from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.debug = True

# adding configuration for using a sqlite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Students_Auth.db'

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    password = db.Column(db.String(20), unique = False, nullable = False)
    fullName = db.Column(db.String(30), nullable = False)
    email = db.Column(db.String(50), unique = True)
    # urls = db.relationship("Url", backref="user")

    def __repr__(self):
        return f"ID : {self.id}, Username: {self.username}"


class Url(db.Model):
    __tablename__ = 'url'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    or_url = db.Column(db.String(2048), nullable = False)
    short_url = db.Column(db.String(8), unique = True, nullable = False)
    
    def __repr__(self):
        return f"User ID : {self.user_id}, Shortened URL: {self.short_url}"


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/signin",methods=['GET','POST'])
def signin():
    if request.method=="POST":
        username=request.form.get("username")
        pwd=request.form.get("pwd")
        user = User.query.filter(User.username==username).one()
        valid = False
        if user is not None:
            if check_password_hash(user.password,pwd):
                valid = True
                return redirect("/")
        if not valid:
                return render_template('signin.html',msg='Invalid User or Password!')
    return render_template("signin.html")

@app.route("/signup",methods=['GET','POST'])
def signup():
    if request.method=="POST":
        name=request.form.get("fname")
        email=request.form.get("email")
        username=request.form.get("username")
        pwd=request.form.get("pwd")
        if ((User.query.filter(User.username==username).one() is None) and (User.query.filter(User.email==email).one() is None)):
            user = User(username=username,password=generate_password_hash(pwd),fullName=name,email=email)
            db.session.add(user)
            db.session.commit()
            return redirect("/")
        else:
            return render_template("signup.html",msg='User already exists')
    return render_template("signup.html")

@app.route("/signout")
def signout():
    return render_template("signout.html")


def main():
    with app.app_context():
        db.create_all()
    app.run()

if "__main__"==__name__:
    main()