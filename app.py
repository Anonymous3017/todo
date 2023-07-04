'''
 ToDo app with authentication in Flask framework. I have to use Flask and SQLAlchemy extensions to handle user sessions and database operations. I have to also add some basic validations and error handling. The app should has the following endpoints:

/api/todo/register: To register a new user with username and password
/api/todo/login: To log in an existing user with username and password
/api/todo/logout: To log out the current user
/api/todo: To get all the todo items for the current user
/api/todo/<int:id>: To get, update or delete a specific todo item for the current user
The app uses a SQLite database to store the user and todo data. You can change it to any other database by modifying the SQLALCHEMY_DATABASE_URI configuration.'''

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'
app.config['SECRET_KEY'] = 'secret_key'
db = SQLAlchemy(app)

#Define the users table model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

#Route for the user registration
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if not request.form['username'] or not request.form['password']:
            flash('Please enter all the fields', 'error')
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


#Route for the user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if not request.form['username'] or not request.form['password']:
            flash('Please enter all the fields', 'error')
        else:
            # Get the user from the database
            user = User.query.filter_by(username=request.form['username']).first()
            if user and user.password == request.form['password']:
                flash('Login successful')
                return redirect(url_for('show_all'))
            else:
                flash('Login failed', 'error')

    # Render the login form
    return render_template('login.html')

#Route for the user logout
@app.route('/logout')
def logout():
    flash('Logout successful')
    return redirect(url_for('login'))


# Define the tasks table model
class Tasks(db.Model):
    id = db.Column('task_id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(200))
    status = db.Column(db.String(10))

    def __init__(self, name, description, status):
        self.name = name
        self.description = description
        self.status = status


# Route for the home page, displays all tasks
@app.route('/')
def show_all():
    with app.app_context():
        tasks = Tasks.query.all()
        print(tasks)
        return render_template('show_all.html', tasks=tasks)


# Route for adding a new task
@app.route('/new', methods=['GET', 'POST'])
def new():
    # Handle form submission
    if request.method == 'POST':
        # Validate form input
        if not request.form['name'] or not request.form['description'] or not request.form['status']:
            flash('Please enter all the fields', 'error')
        else:
            # Create a new task object
            task = Tasks(request.form['name'], request.form['description'], request.form['status'])

            with app.app_context():
                # Add the task to the database
                db.session.add(task)
                db.session.commit()

            flash('Record was successfully added')
            return redirect(url_for('show_all'))

    # Render the new task form
    return render_template('new.html')


# Route for editing a task
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    # Get the task from the database
    task = Tasks.query.get(id)

    # Handle form submission
    if request.method == 'POST':
        # Validate form input
        if not request.form['name'] or not request.form['description'] or not request.form['status']:
            flash('Please enter all the fields', 'error')
        else:
            form_id = request.form['id']
            name = request.form['name']
            description = request.form['description']
            status = request.form['status']
            print(f"Received form data: id={form_id}, name={name}, description={description}, status={status}")
            # Update the task object
            task.name = name
            task.description = description
            task.status = status

            with app.app_context():
                # Update the task in the database
                db.session.merge(task)
                db.session.commit()
                print(f"Updated task record: id={form_id}, name={name}, description={description}, status={status}")
                # Check if the transaction was committed
                if not db.session.is_active:
                    print("\n Transaction was not committed")


            flash('Record was successfully updated')
            return redirect(url_for('show_all'))

    # Render the edit task form
    return render_template('edit.html', task=task)


# route for delete a task
@app.route('/delete', methods=['POST'])
def delete():
    task_id = request.form['id']
    task = Tasks.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        flash('Record was successfully deleted')
    else:
        flash('Task record not found', 'error')
    return redirect(url_for('show_all'))

if __name__ == '__main__':
    with app.app_context():
        # Create the database tables if they don't exist
        db.create_all()
        

    # Start the Flask application
    app.run(debug=True)

