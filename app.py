from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "lab_secret_key"

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(based_dir if 'based_dir' in locals() else basedir, 'lab_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Facility(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, default="General Health Lab")
    address = db.Column(db.String(200))
    contact = db.Column(db.String(50))

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    phone = db.Column(db.String(20))
    test_name = db.Column(db.String(100))
    result = db.Column(db.Text)
    date_recorded = db.Column(db.DateTime, default=datetime.utcnow)

def prepare_patient_list(patients):
    formatted = []
    for p in patients:
        formatted.append({
            'name': p.full_name.title(),
            'test_display': f"{p.test_name}: {p.result}",
            'date': p.date_recorded.strftime("%d %b %Y") if p.date_recorded else "N/A",
            'id': p.id
        })
    return formatted

with app.app_context():
    db.create_all()
    if not Facility.query.first():
        db.session.add(Facility(name="My Health Lab", address="123 Main St", contact="0123456789"))
        db.session.commit()

@app.route('/')
def index():
    facility = Facility.query.first()
    patients_raw = Patient.query.all()
    patients_prepared = prepare_patient_list(patients_raw)
    return render_template('index.html', facility=facility, patients=patients_prepared)

@app.route('/add_patient', methods=['POST'])
def add_patient():
    new_p = Patient(
        full_name=request.form['name'],
        age=request.form['age'],
        gender=request.form['gender'],
        phone=request.form['phone'],
        test_name=request.form['test_name'],
        result=request.form['result']
    )
    db.session.add(new_p)
    db.session.commit()
    flash("Patient record saved successfully!", "success")
    return redirect(url_for('index'))

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    facility = Facility.query.first()
    if request.method == 'POST':
        facility.name = request.form['name']
        facility.address = request.form['address']
        facility.contact = request.form['contact']
        db.session.commit()
        flash("Facility settings updated!", "info")
        return redirect(url_for('index'))
    return render_template('settings.html', facility=facility)

@app.route('/print/<int:id>')
def print_result(id):
    patient = Patient.query.get_or_404(id)
    facility = Facility.query.first()
    return render_template('print_result.html', patient=patient, facility=facility)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8085)
