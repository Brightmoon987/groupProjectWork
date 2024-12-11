from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User

app = Flask(__name__)
app.secret_key = 'key_sessione_user'  # Secret key for session
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# Initialize db and flask-login
db.init_app(app)
login_manager = LoginManager()  # Initialize Flask-Login
login_manager.init_app(app)  # Link Flask-Login with Flask
login_manager.login_view = 'login'  # View to redirect users who are not logged in

# User loader function (this is crucial for Flask-Login to work)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Fetch the user by ID

with app.app_context():
    db.create_all()

# Implement routes and methods

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if user already exists in the DB
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="Questo username è già in uso.")
        
        # Create a new user and save to the DB
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', error=None)

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if both username and password are provided
        if not username or not password:
            error = "Entrambi i campi sono obbligatori."
            return render_template('login.html', error=error)
        
        # Try to find the user in the database
        user = User.query.filter_by(username=username, password=password).first()
        if user:  # If user exists
            login_user(user)
            return redirect(url_for('home'))
        else:
            error = "Username o password non corretti."
    
    return render_template('login.html', error=error)

@app.route('/home')
@login_required  # Only accessible if user is logged in
def home():
    return render_template('home.html', username=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()  # Logout the user
    return redirect(url_for('login'))  # Redirect to the login page

if __name__ == '__main__':
    app.run(debug=True)
