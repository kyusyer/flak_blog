import werkzeug.security
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['UPLOAD_FOLDER'] = "static/files"


# login authentication
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


##CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
#Line below only required once, when creating DB. 
# db.create_all()



@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        new_user = User(
            email=request.form.get('email'),
            name=request.form.get("name"),
            # password=request.form.get("password")
            password=generate_password_hash(request.form.get('password'), method='pbkdf2:sha256', salt_length=8)

        )

        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)

        return redirect(url_for("secrets"))
    return render_template("register.html")


@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user_to_check = User.query.filter_by(email=email).first()
        pwhash = user_to_check.password

        if check_password_hash(pwhash, password):
            login_user(user_to_check)
            return redirect(url_for('secrets'))
    return render_template("login.html")




@app.route('/secrets')
@login_required
def secrets():
    print(current_user.name)
    return render_template("secrets.html", name=current_user.name)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download')
@login_required
def download():
    filename = "cheat_sheet.pdf"
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
