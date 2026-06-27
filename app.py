from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lab-secret-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lab_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    phone = db.Column(db.String(20))
    test_name = db.Column(db.String(100))
    result = db.Column(db.String(200))
    status = db.Column(db.String(20), default='Pending')
    date_recorded = db.Column(db.DateTime, default=datetime.utcnow)

class LabSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_name = db.Column(db.String(100), default="Medical Laboratory")
    logo_filename = db.Column(db.String(100))
    watermark_text = db.Column(db.String(50), default="OFFICIAL COPY")

with app.app_context():
    db.create_all()
    # Create default settings if none exist
    if not LabSettings.query.first():
        db.session.add(LabSettings())
        db.session.commit()

@app.route('/')
def index():
    patients = Patient.query.order_by(Patient.date_recorded.desc()).all()
    settings = LabSettings.query.first()
    return render_template('index.html', patients=patients, settings=settings)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    setting = LabSettings.query.first()
    if request.method == 'POST':
        setting.hospital_name = request.form.get('hospital_name')
        setting.watermark_text = request.form.get('watermark_text')
        
        file = request.files.get('logo')
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            setting.logo_filename = filename
            
        db.session.commit()
        flash('Settings updated successfully!')
        return redirect(url_for('index'))
    return render_template('settings.html', settings=setting)

@app.route('/add', methods=['POST'])
def add_patient():
    new_patient = Patient(
        full_name=request.form.get('full_name'), 
        age=request.form.get('age'), 
        gender=request.form.get('gender'), 
        phone=request.form.get('phone'), 
        test_name=request.form.get('test_name'), 
        status='Pending'
    )
    db.session.add(new_patient)
    db.session.commit()
    flash('Patient added successfully!')
    return redirect(url_for('index'))

@app.route('/update/<int:id>', methods=['POST'])
def update_patient(id):
    patient = Patient.query.get(id)
    patient.result = request.form.get('result')
    patient.status = 'Completed'
    db.session.commit()
    flash('Result updated successfully!')
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_patient(id):
    patient = Patient.query.get(id)
    db.session.delete(patient)
    db.session.commit()
    flash('Patient record deleted!')
    return redirect(url_for('index'))

@app.route('/print/<int:id>')
def print_result(id):
    patient = Patient.query.get(id)
    settings = LabSettings.query.first()
    return render_template('print_result.html', p=patient, settings=settings)

if __name__ == '__main__':
    app.run(port=8085, debug=True)
