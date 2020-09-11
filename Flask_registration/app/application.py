from flask import Flask, render_template, request, redirect, url_for, make_response, session, logging, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from passlib.hash import sha256_crypt # for encrypting user
import re # regular expression for email validation

# connecting existing database
engine = create_engine("postgresql+psycopg2://postgres:1234@localhost/zendb")
db = scoped_session(sessionmaker(bind=engine))

application = app = Flask(__name__)
app.secret_key = "12OWhiSmnikin9);"

# first page
@app.route("/")
def index():
    if 'mail' in session:
            flash("You're already loggedin, please logout first to access","danger")
            return redirect(url_for('home'))
    else:
        return render_template("index.html")

# signup or registration page
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        # taking user input in variables
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        password = request.form.get('password')
        confirm = request.form.get('confirm') 
        address = request.form.get('address')
        # encrypting password
        secure_password = sha256_crypt.encrypt(str(password))

        # checks if email is valid
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash("Invalid email address!","danger")
            return render_template("register.html")
        # checks if email is already taken 
        # which also prevents integrity error for adding same email
        try:
            email_data = db.execute("SELECT email FROM member WHERE email=:email",{"email":email}).fetchone()
            if(email == email_data[0]):
                flash("Email is already taken","danger")
                return render_template("register.html")
            else:
                pass
        except TypeError:
            pass
        # checks password length, should be atleast 8 
        if(len(password)) < 7:
            flash("Password Too short","danger")
            return render_template("register.html")
        # checks if both passwords are same
        elif(password == confirm):
            # user registration
            db.execute("INSERT INTO member(fullname,email,password,address) VALUES (:fullname,:email,:password,:address)",{"fullname":fullname,"email":email,"password":secure_password,"address":address})
            db.commit()
            fullname = request.form.get("fullname")
            address = request.form.get("address")
            flash("Signup complete","success")
            return render_template("home.html", fullname = fullname, address = address)
        else:
            # two passwords arent same
            flash("Passwords dont match","danger")
            return render_template("register.html") 
    else: 
        # if request method is GET
        if 'mail' in session:
            flash("You're already loggedin, please logout first to access","danger")
            return redirect(url_for('home'))
        return render_template("register.html")


# login page
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        # taking user input in variables
        email = request.form.get("email")
        password = request.form.get('password')
        # checks if email is valid
        # prevents database transaction if email isnt valid
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash("Invalid email address!","danger")
            return render_template("login.html")
        # querying and retriving from db
        data = db.execute("SELECT email, password FROM member WHERE email=:email",{"email":email}).fetchone()
        passworddata = data[1]
        # no email available 
        if data is None:
            flash("Invalid email","danger")
            return render_template("login.html")
        else:
            if sha256_crypt.verify(password, passworddata):
                # setting up session variable
                session['mail'] = request.form['email']
                flash("login succesfull","success")                    
                return redirect(url_for('home'))
            else:
                # passwords dont match
                flash("invalid credentials","danger")
                return render_template("login.html")
    else:
        # when request method is GET 
        if 'mail' in session:
            flash("You're already loggedin, please logout first","danger")
            return redirect(url_for('home'))
        else:
            return render_template("login.html")

# home page can only be accessed through login or signup
@app.route('/home', methods=['POST', 'GET'])
def home():
    # if user is loggedin 
    if 'mail' in session:
        # if user has been already on home page and has fullname and address already in session
        # prevents a repetative database transaction
        if 'fullname' in session:
            data0 = session['fullname'] 
            data1 = session['address']
            return render_template("home.html", fullname = data0, address = data1)
        # when user logsin for first time
        else:
            # session from login
            email = session['mail']
            data = db.execute("SELECT fullname, address FROM member WHERE email=:email",{"email":email}).fetchone()
            # setting session for further use
            session['fullname'] = data[0]
            session['address'] = data[1]
            return render_template("home.html", fullname = data[0], address = data[1])
    # if user tries accessing home page without login or signup        
    else:
        flash("login required","danger")
        return render_template("login.html")


# logout can only be accesed if user is logged in
@app.route('/logout', methods=['POST', 'GET'])
def logout():
    # if user is logged in
    if 'mail' in session:
        session.clear()
        flash("Logged out successfully","success")
    # if unlogged user tries accessing
    else:
        flash("Login required","danger")
    # everyone is redirected to login page eventually
    return redirect(url_for("login"))

if __name__ =="__main__":
    app.secret_key = "12OWhiSmnikin9);"
    # debug = False in production environment
    app.run(debug=True, port=8090) 