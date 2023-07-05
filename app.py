from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'
app.config['SECRET_KEY'] = 'secret_key'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

# Define the users table model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route for the user registration
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if not request.form['username'] or not request.form['password']:
            flash('Please enter all the fields', 'error')
        else:
            # Check if the username already exists in the database
            existing_user = User.query.filter_by(username=request.form['username']).first()
            if existing_user:
                flash('User already exists. Please login.')
                return redirect(url_for('login'))
            else:
                # Create a new user object
                user = User(username=request.form['username'], password=request.form['password'])

                with app.app_context():
                    # Add the user to the database
                    db.session.add(user)
                    db.session.commit()

                flash('Record was successfully added')
                return redirect(url_for('login'))

    # Render the registration form
    return render_template('signup.html')


# Route for the user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if not request.form['username'] or not request.form['password']:
            flash('Please enter all the fields', 'error')
        else:
            # Get the user from the database
            user = User.query.filter_by(username=request.form['username']).first()
            if user and user.password == request.form['password']:
                login_user(user)
                flash('Login successful')
                return redirect(url_for('show_all'), code=307)
            else:
                flash('Invalid username or password')
                return redirect(url_for('login'))

    # Render the login form
    return render_template('login.html')

# Route for the user logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout successful')
    return redirect(url_for('login'))


# Define the tasks table model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, name, description, status, user_id):
        self.name = name
        self.description = description
        self.status = status
        self.user_id = user_id

# Route for displaying home page
@app.route('/home')
def home():
    return render_template('home.html')


# Route for displaying all tasks
@app.route('/api/todo', methods=['GET', 'POST'])
def show_all():
    if not current_user.is_authenticated:
        flash('Invalid request')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Retrieve all tasks for the current user
        tasks = Task.query.filter_by(user_id=current_user.id).all()
        return render_template('show_all.html', tasks=tasks)
    else:
        #redirect to login page with an error message
        flash('Invalid request')
        return redirect(url_for('login'))

# Route for adding a new task
@app.route('/api/todo/create', methods=['GET', 'POST'])
@login_required
def new():
    # Handle form submission
    if request.method == 'POST':
        # Validate form input
        if not request.form['name'] or not request.form['description'] or not request.form['status']:
            flash('Please enter all the fields', 'error')
        else:
            # Create a new task object for the current user
            task = Task(request.form['name'], request.form['description'], request.form['status'], current_user.id)

            with app.app_context():
                # Add the task to the database
                db.session.add(task)
                db.session.commit()

            flash('Record was successfully added')
            return redirect(url_for('show_all'), code=307)

    # Render the new task form
    return render_template('new.html')


# Route for editing a task
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    # Get the task from the database
    task = Task.query.filter_by(id=id, user_id=current_user.id).first()

    if not task:
        # If the task is not found, redirect to the show_all() function with an error message
        flash('Invalid task ID')
        return redirect(url_for('show_all'))

    # Handle form submission
    if request.method == 'POST':
        # Validate form input
        if not request.form['name'] or not request.form['description'] or not request.form['status']:
            flash('Please enter all the fields', 'error')
        else:
            name = request.form['name']
            description = request.form['description']
            status = request.form['status']

            # Update the task object
            task.name = name
            task.description = description
            task.status = status

            with app.app_context():
                # Update the task in the database
                db.session.merge(task)
                db.session.commit()

            flash('Record was successfully updated')
            return redirect(url_for('show_all'), code=307)

    # Render the edit task form
    return render_template('edit.html', task=task)

# Route for deleting a task
@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    # Get the task from the database
    task = Task.query.filter_by(id=id, user_id=current_user.id).first()

    if not task:
        # If the task is not found, redirect to the show_all() function with an error message
        flash('Invalid task ID')
        return redirect(url_for('show_all'), code=307)

    # Delete the task from the database
    db.session.delete(task)
    db.session.commit()

    flash('Record was successfully deleted')
    return redirect(url_for('show_all'), code=307)

if __name__ == '__main__':
    with app.app_context():
        # Create the database tables if they don't exist
        db.create_all()

    # Start the Flask application
    app.run(debug=True)
