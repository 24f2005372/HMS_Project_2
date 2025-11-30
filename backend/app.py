from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, User, Doctor, Patient, Appointment

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hms_v2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'v2secret'

CORS(app) # Allow Vue to talk to Flask
db.init_app(app)

# --- AUTH ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username'], password=data['password']).first()
    if user:
        return jsonify({'message': 'Login Success', 'role': user.role, 'id': user.id, 'username': user.username})
    return jsonify({'message': 'Invalid Credentials'}), 401

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'User exists'}), 400
    
    new_user = User(username=data['username'], password=data['password'], role='patient')
    db.session.add(new_user)
    db.session.commit()
    
    new_pat = Patient(user_id=new_user.id, address=data.get('address', ''))
    db.session.add(new_pat)
    db.session.commit()
    return jsonify({'message': 'Registered'}), 201

# --- ADMIN ---
@app.route('/api/admin/dashboard')
def admin_stats():
    return jsonify({
        'doctors': Doctor.query.count(),
        'patients': Patient.query.count(),
        'appointments': Appointment.query.count()
    })

@app.route('/api/doctors', methods=['GET', 'POST'])
def manage_doctors():
    if request.method == 'POST':
        data = request.json
        # Check if user exists first to prevent duplicate username error
        if User.query.filter_by(username=data['username']).first():
             return jsonify({'message': 'Username taken'}), 400
             
        user = User(username=data['username'], password=data['password'], role='doctor')
        db.session.add(user)
        db.session.commit()
        doc = Doctor(user_id=user.id, specialization=data['specialization'])
        db.session.add(doc)
        db.session.commit()
        return jsonify({'message': 'Doctor Added'})
    
    # GET
    docs = Doctor.query.all()
    return jsonify([{'id': d.id, 'username': d.user.username, 'spec': d.specialization} for d in docs])

@app.route('/api/doctor/<int:id>', methods=['DELETE'])
def delete_doctor(id):
    doc = Doctor.query.get(id)
    user = User.query.get(doc.user_id)
    db.session.delete(doc)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Deleted'})

# --- PATIENT ---
@app.route('/api/patient/book', methods=['POST'])
def book_appt():
    data = request.json
    # Logic to prevent double booking
    exists = Appointment.query.filter_by(doctor_id=data['doctor_id'], date=data['date'], time=data['time']).first()
    if exists: return jsonify({'message': 'Slot Taken'}), 400
    
    # Get Patient ID from User ID
    patient = Patient.query.filter_by(user_id=data['user_id']).first()
    
    new_appt = Appointment(patient_id=patient.id, doctor_id=data['doctor_id'], 
                           date=data['date'], time=data['time'], status='Booked')
    db.session.add(new_appt)
    db.session.commit()
    return jsonify({'message': 'Booked'})

@app.route('/api/patient/appointments/<int:user_id>')
def my_appts(user_id):
    patient = Patient.query.filter_by(user_id=user_id).first()
    if not patient: return jsonify([])
    appts = Appointment.query.filter_by(patient_id=patient.id).all()
    return jsonify([
        {'id': a.id, 'doctor': a.doctor.user.username, 'date': a.date, 
         'time': a.time, 'status': a.status, 'diagnosis': a.diagnosis, 'prescription': a.prescription} 
        for a in appts])

# --- DOCTOR ---
@app.route('/api/doctor/appointments/<int:user_id>')
def doc_appts(user_id):
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    if not doctor: return jsonify([])
    appts = Appointment.query.filter_by(doctor_id=doctor.id).all()
    return jsonify([
        {'id': a.id, 'patient': a.patient.user.username, 'date': a.date, 
         'time': a.time, 'status': a.status, 'diagnosis': a.diagnosis, 'prescription': a.prescription} 
        for a in appts])

@app.route('/api/doctor/complete/<int:id>', methods=['POST'])
def complete_appt(id):
    data = request.json
    appt = Appointment.query.get(id)
    appt.diagnosis = data['diagnosis']
    appt.prescription = data['prescription']
    appt.status = 'Completed'
    db.session.commit()
    return jsonify({'message': 'Completed'})

if __name__ == '__main__':
    app.run(debug=True)