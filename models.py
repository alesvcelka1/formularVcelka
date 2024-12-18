
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///people.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Person.query.first():
            db.session.add_all([
                Person(first_name='Alice', last_name='Smith', age=30),
                Person(first_name='Bob', last_name='Johnson', age=25),
                Person(first_name='Charlie', last_name='Brown', age=35)
            ])
            db.session.commit()
    app.run(debug=True)