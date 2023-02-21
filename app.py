from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy

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

    def __repr__(self):
        return f"ID : {self.id}, Username: {self.username}"


class Url(db.Model):
    __tablename__ = 'url'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    or_url = db.Column(db.String(2048), nullable = False)
    short_url = db.Column(db.String(8), unique = True, nullable = False)
    
    def __repr__(self):
        return f"User ID : {self.user_id}, Shortened URL: {self.short_url}"


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/signin")
def signin():
    return render_template("signin.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/signout")
def signout():
    return render_template("signout.html")


app.run()