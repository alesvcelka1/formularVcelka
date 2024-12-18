from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Regexp
from models import db, Person
import hashlib
from itsdangerous import URLSafeSerializer

# Initialize the Flask app and configure the database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Path to database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking to save resources
app.config['SECRET_KEY'] = 'mysecretkey'  # Secret key for CSRF protection

# Initialize the database
db.init_app(app)

# Initialize the serializer
serializer = URLSafeSerializer(app.config['SECRET_KEY'])

# WTForm for adding a new person
class PersonForm(FlaskForm):
    id = IntegerField('ID')
    first_name = StringField('First Name', validators=[DataRequired(), Regexp(r'^[a-zA-Z]+$', message="First name must contain only letters.")])
    last_name = StringField('Last Name', validators=[DataRequired(), Regexp(r'^[a-zA-Z]+$', message="Last name must contain only letters.")])
    age = IntegerField('Age', validators=[DataRequired()])
    submit = SubmitField('Add Person')

# Create the tables and populate initial data if not already present
with app.app_context():
    db.create_all()
    if not Person.query.first():
        db.session.add_all([
            Person(first_name='Alice', last_name='Smith', age=30),
            Person(first_name='Bob', last_name='Johnson', age=25),
            Person(first_name='Charlie', last_name='Brown', age=35)
        ])
        db.session.commit()

@app.route('/')
def index():
    persons = Person.query.all()
    return render_template('index.html', persons=persons, serializer=serializer)

@app.route('/add', methods=['GET', 'POST'])
def add():
    form = PersonForm()
    if form.validate_on_submit():
        # Improved validation for name, last name, and age
        first_name = form.first_name.data.strip()
        last_name = form.last_name.data.strip()
        age = form.age.data

        if not first_name.isalpha():
            form.first_name.errors.append('First name must contain only letters.')
        elif not last_name.isalpha():
            form.last_name.errors.append('Last name must contain only letters.')
        elif age < 0 or age > 120:
            form.age.errors.append('Age must be between 0 and 120.')
        else:
            new_person = Person(first_name=first_name, last_name=last_name, age=age, id=form.id.data)
            db.session.add(new_person)
            db.session.commit()
            return redirect(url_for('index'))
    return render_template('add.html', form=form)

@app.route('/detail/<int:person_id>')
def detail(person_id):
    person = Person.query.get_or_404(person_id)
    return render_template('detail.html', person=person)

@app.route('/delete/<token>', methods=['POST'])
def delete(token):
    try:
        person_id = serializer.loads(token)
        person = Person.query.get(person_id)
        if person:
            db.session.delete(person)
            db.session.commit()
    except Exception as e:
        print(f"Error: {e}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)