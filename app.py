from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'lab_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    phone = db.Column(db.String(20))
    test_name = db.Column(db.String(100))
    result = db.Column(db.Text)
    date = db.Column(db.String(20))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    patients = Patient.query.all()
    return render_template('index.html', patients=patients)

@app.route('/add', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        new_patient = Patient(
            name=request.form['name'],
            age=request.form['age'],
            gender=request.form['gender'],
            phone=request.form['phone'],
            test_name=request.form['test_name'],
            result=request.form['result'],
            date=request.form['date']
        )
        db.session.add(new_patient)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_patient.html')

@app.route('/patient/<int:id>')
def view_patient(id):
    patient = Patient.query.get_or_404(id)
    return render_template('view_result.html', patient=patient)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
