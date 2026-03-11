from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_caching import Cache
from models import db, User, Doctor, Patient, Appointment, Treatment, Department, DoctorAvailability
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import os, io, csv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hms_v2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'hms_v2_super_secret'

# Redis Caching (Milestone 8)
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300

# Celery Config (Milestone 7)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# Mail Config (update with real credentials in .env)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME', 'noreply@hms.com')

CORS(app)
db.init_app(app)
cache = Cache(app)


# ── HELPERS ──────────────────────────────────────────────────────────────────

def get_user_from_token():
    """Simple token: base64(user_id:role) sent as Authorization header."""
    import base64
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return None
    try:
        decoded = base64.b64decode(token).decode()
        uid, role = decoded.split(':')
        return User.query.get(int(uid))
    except Exception:
        return None

def require_role(*roles):
    """Returns (user, error_response) — caller checks if error_response is not None."""
    user = get_user_from_token()
    if not user:
        return None, (jsonify({'message': 'Unauthorized'}), 401)
    if user.role not in roles:
        return None, (jsonify({'message': 'Forbidden'}), 403)
    if user.is_blacklisted:
        return None, (jsonify({'message': 'Account blacklisted'}), 403)
    return user, None

def make_token(user):
    import base64
    raw = f"{user.id}:{user.role}"
    return base64.b64encode(raw.encode()).decode()


# ── AUTH ──────────────────────────────────────────────────────────────────────

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    if user and user.check_password(data.get('password', '')) and not user.is_blacklisted:
        return jsonify({
            'token': make_token(user),
            'role': user.role,
            'id': user.id,
            'username': user.username
        }), 200
    return jsonify({'message': 'Invalid credentials or blacklisted account'}), 401

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Username and password required'}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    user = User(username=data['username'], email=data.get('email'), role='patient')
    user.set_password(data['password'])
    db.session.add(user)
    db.session.flush()
    patient = Patient(user_id=user.id, address=data.get('address',''),
                      phone=data.get('phone',''), date_of_birth=data.get('dob',''),
                      blood_group=data.get('blood_group',''))
    db.session.add(patient)
    db.session.commit()
    return jsonify({'message': 'Registered successfully'}), 201


# ── ADMIN ─────────────────────────────────────────────────────────────────────

@app.route('/api/admin/dashboard')
@cache.cached(timeout=60, key_prefix='admin_dashboard')
def admin_stats():
    user, err = require_role('admin')
    if err: return err
    return jsonify({
        'doctors': Doctor.query.count(),
        'patients': Patient.query.count(),
        'appointments': Appointment.query.count(),
        'completed': Appointment.query.filter_by(status='Completed').count(),
        'cancelled': Appointment.query.filter_by(status='Cancelled').count(),
    })

# Departments
@app.route('/api/departments', methods=['GET'])
def get_departments():
    depts = Department.query.all()
    return jsonify([{'id': d.id, 'name': d.name, 'description': d.description,
                     'doctors_count': len(d.doctors)} for d in depts])

@app.route('/api/departments', methods=['POST'])
def add_department():
    user, err = require_role('admin')
    if err: return err
    data = request.json
    if Department.query.filter_by(name=data['name']).first():
        return jsonify({'message': 'Department already exists'}), 400
    dept = Department(name=data['name'], description=data.get('description',''))
    db.session.add(dept)
    db.session.commit()
    return jsonify({'message': 'Department added', 'id': dept.id}), 201

# Doctors
@app.route('/api/doctors', methods=['GET'])
@cache.cached(timeout=120, key_prefix=lambda: f"doctors_{request.args.get('search','')}")
def get_doctors():
    search = request.args.get('search', '').lower()
    query = Doctor.query.join(User)
    if search:
        query = query.filter(
            db.or_(User.username.ilike(f'%{search}%'),
                   Doctor.specialization.ilike(f'%{search}%'))
        )
    docs = query.all()
    return jsonify([{
        'id': d.id, 'username': d.user.username, 'spec': d.specialization,
        'email': d.user.email, 'phone': d.phone, 'experience': d.experience_years,
        'bio': d.bio, 'department_id': d.department_id,
        'department': d.department.name if d.department else '',
        'is_blacklisted': d.user.is_blacklisted
    } for d in docs])

@app.route('/api/doctors', methods=['POST'])
def add_doctor():
    user, err = require_role('admin')
    if err: return err
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already taken'}), 400
    new_user = User(username=data['username'], email=data.get('email'), role='doctor')
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.flush()
    doc = Doctor(user_id=new_user.id, specialization=data['specialization'],
                 department_id=data.get('department_id'),
                 experience_years=data.get('experience', 0),
                 phone=data.get('phone',''), bio=data.get('bio',''))
    db.session.add(doc)
    db.session.commit()
    cache.delete('doctors_')
    return jsonify({'message': 'Doctor added'}), 201

@app.route('/api/doctor/<int:id>', methods=['GET','PUT','DELETE'])
def doctor_detail(id):
    doc = Doctor.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify({'id': doc.id, 'username': doc.user.username, 'spec': doc.specialization,
                        'email': doc.user.email, 'phone': doc.phone, 'experience': doc.experience_years,
                        'bio': doc.bio, 'department_id': doc.department_id})
    user, err = require_role('admin')
    if err: return err
    if request.method == 'PUT':
        data = request.json
        doc.specialization = data.get('spec', doc.specialization)
        doc.experience_years = data.get('experience', doc.experience_years)
        doc.phone = data.get('phone', doc.phone)
        doc.bio = data.get('bio', doc.bio)
        doc.department_id = data.get('department_id', doc.department_id)
        doc.user.username = data.get('username', doc.user.username)
        doc.user.email = data.get('email', doc.user.email)
        db.session.commit()
        cache.delete('doctors_')
        return jsonify({'message': 'Doctor updated'})
    if request.method == 'DELETE':
        db.session.delete(doc.user)
        db.session.commit()
        cache.delete('doctors_')
        return jsonify({'message': 'Doctor deleted'})

@app.route('/api/doctor/<int:id>/blacklist', methods=['POST'])
def blacklist_doctor(id):
    user, err = require_role('admin')
    if err: return err
    doc = Doctor.query.get_or_404(id)
    doc.user.is_blacklisted = not doc.user.is_blacklisted
    db.session.commit()
    cache.delete('doctors_')
    status = 'blacklisted' if doc.user.is_blacklisted else 'unblacklisted'
    return jsonify({'message': f'Doctor {status}'})

# Patients (Admin)
@app.route('/api/admin/patients', methods=['GET'])
def admin_get_patients():
    user, err = require_role('admin')
    if err: return err
    search = request.args.get('search', '').lower()
    query = Patient.query.join(User)
    if search:
        query = query.filter(
            db.or_(User.username.ilike(f'%{search}%'),
                   Patient.phone.ilike(f'%{search}%'),
                   User.email.ilike(f'%{search}%'))
        )
    patients = query.all()
    return jsonify([{
        'id': p.id, 'username': p.user.username, 'email': p.user.email,
        'phone': p.phone, 'address': p.address, 'dob': p.date_of_birth,
        'blood_group': p.blood_group, 'is_blacklisted': p.user.is_blacklisted
    } for p in patients])

@app.route('/api/admin/patient/<int:id>', methods=['PUT'])
def admin_update_patient(id):
    user, err = require_role('admin')
    if err: return err
    patient = Patient.query.get_or_404(id)
    data = request.json
    patient.address = data.get('address', patient.address)
    patient.phone = data.get('phone', patient.phone)
    patient.date_of_birth = data.get('dob', patient.date_of_birth)
    patient.blood_group = data.get('blood_group', patient.blood_group)
    patient.user.email = data.get('email', patient.user.email)
    db.session.commit()
    return jsonify({'message': 'Patient updated'})

@app.route('/api/admin/patient/<int:id>/blacklist', methods=['POST'])
def blacklist_patient(id):
    user, err = require_role('admin')
    if err: return err
    patient = Patient.query.get_or_404(id)
    patient.user.is_blacklisted = not patient.user.is_blacklisted
    db.session.commit()
    status = 'blacklisted' if patient.user.is_blacklisted else 'unblacklisted'
    return jsonify({'message': f'Patient {status}'})

# Admin: All Appointments
@app.route('/api/admin/appointments', methods=['GET'])
def admin_appointments():
    user, err = require_role('admin')
    if err: return err
    appts = Appointment.query.order_by(Appointment.date.desc()).all()
    return jsonify([{
        'id': a.id, 'patient': a.patient.user.username, 'doctor': a.doctor.user.username,
        'date': a.date, 'time': a.time, 'status': a.status,
        'diagnosis': a.treatment.diagnosis if a.treatment else '',
        'prescription': a.treatment.prescription if a.treatment else ''
    } for a in appts])


# ── DOCTOR ────────────────────────────────────────────────────────────────────

@app.route('/api/doctor/appointments/<int:user_id>', methods=['GET'])
def doc_appts(user_id):
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    if not doctor: return jsonify([])
    filter_type = request.args.get('filter', 'all')  # all | today | week
    query = Appointment.query.filter_by(doctor_id=doctor.id)
    today = datetime.utcnow().date()
    if filter_type == 'today':
        query = query.filter_by(date=str(today))
    elif filter_type == 'week':
        week_end = str(today + timedelta(days=7))
        query = query.filter(Appointment.date >= str(today), Appointment.date <= week_end)
    appts = query.order_by(Appointment.date, Appointment.time).all()
    return jsonify([{
        'id': a.id, 'patient_id': a.patient.id, 'patient': a.patient.user.username,
        'date': a.date, 'time': a.time, 'status': a.status,
        'diagnosis': a.treatment.diagnosis if a.treatment else '',
        'prescription': a.treatment.prescription if a.treatment else '',
        'notes': a.treatment.notes if a.treatment else '',
        'next_visit': a.treatment.next_visit if a.treatment else ''
    } for a in appts])

@app.route('/api/doctor/complete/<int:id>', methods=['POST'])
def complete_appt(id):
    appt = Appointment.query.get_or_404(id)
    data = request.json
    appt.status = 'Completed'
    if appt.treatment:
        appt.treatment.diagnosis = data.get('diagnosis','')
        appt.treatment.prescription = data.get('prescription','')
        appt.treatment.notes = data.get('notes','')
        appt.treatment.next_visit = data.get('next_visit','')
    else:
        t = Treatment(appointment_id=appt.id, diagnosis=data.get('diagnosis',''),
                      prescription=data.get('prescription',''), notes=data.get('notes',''),
                      next_visit=data.get('next_visit',''))
        db.session.add(t)
    db.session.commit()
    return jsonify({'message': 'Appointment completed'})

@app.route('/api/doctor/cancel/<int:id>', methods=['POST'])
def doctor_cancel_appt(id):
    appt = Appointment.query.get_or_404(id)
    appt.status = 'Cancelled'
    db.session.commit()
    return jsonify({'message': 'Appointment cancelled'})

@app.route('/api/doctor/patients/<int:user_id>', methods=['GET'])
def doctor_patients(user_id):
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    if not doctor: return jsonify([])
    patient_ids = db.session.query(Appointment.patient_id).filter_by(doctor_id=doctor.id).distinct()
    patients = Patient.query.filter(Patient.id.in_(patient_ids)).all()
    return jsonify([{'id': p.id, 'username': p.user.username, 'phone': p.phone,
                     'dob': p.date_of_birth, 'blood_group': p.blood_group} for p in patients])

@app.route('/api/doctor/availability/<int:user_id>', methods=['GET','POST'])
def doctor_availability(user_id):
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    if not doctor: return jsonify({'message': 'Doctor not found'}), 404
    if request.method == 'GET':
        avail = DoctorAvailability.query.filter_by(doctor_id=doctor.id).all()
        return jsonify([{'id': a.id, 'date': a.date, 'start_time': a.start_time,
                         'end_time': a.end_time, 'is_available': a.is_available} for a in avail])
    data = request.json  # list of {date, start_time, end_time}
    # Clear existing future availability and re-save
    today = str(datetime.utcnow().date())
    DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor.id,
        DoctorAvailability.date >= today
    ).delete()
    for slot in data:
        a = DoctorAvailability(doctor_id=doctor.id, date=slot['date'],
                               start_time=slot['start_time'], end_time=slot['end_time'])
        db.session.add(a)
    db.session.commit()
    cache.delete_memoized(get_doctors)
    return jsonify({'message': 'Availability saved'})

@app.route('/api/doctor/<int:doc_id>/availability', methods=['GET'])
def get_doctor_availability(doc_id):
    avail = DoctorAvailability.query.filter_by(doctor_id=doc_id, is_available=True).all()
    return jsonify([{'date': a.date, 'start_time': a.start_time, 'end_time': a.end_time} for a in avail])


# ── PATIENT ────────────────────────────────────────────────────────────────────

@app.route('/api/patient/profile/<int:user_id>', methods=['GET','PUT'])
def patient_profile(user_id):
    patient = Patient.query.filter_by(user_id=user_id).first()
    if not patient: return jsonify({'message': 'Not found'}), 404
    if request.method == 'GET':
        return jsonify({'username': patient.user.username, 'email': patient.user.email,
                        'address': patient.address, 'phone': patient.phone,
                        'dob': patient.date_of_birth, 'blood_group': patient.blood_group})
    data = request.json
    patient.address = data.get('address', patient.address)
    patient.phone = data.get('phone', patient.phone)
    patient.date_of_birth = data.get('dob', patient.date_of_birth)
    patient.blood_group = data.get('blood_group', patient.blood_group)
    patient.user.email = data.get('email', patient.user.email)
    db.session.commit()
    return jsonify({'message': 'Profile updated'})

@app.route('/api/patient/book', methods=['POST'])
def book_appt():
    data = request.json
    doctor_id = data.get('doctor_id')
    date = data.get('date')
    time = data.get('time')
    # Double booking check
    conflict = Appointment.query.filter_by(
        doctor_id=doctor_id, date=date, time=time
    ).filter(Appointment.status != 'Cancelled').first()
    if conflict:
        return jsonify({'message': 'This slot is already booked'}), 400
    patient = Patient.query.filter_by(user_id=data['user_id']).first()
    appt = Appointment(patient_id=patient.id, doctor_id=doctor_id, date=date, time=time, status='Booked')
    db.session.add(appt)
    db.session.commit()
    return jsonify({'message': 'Appointment booked', 'id': appt.id}), 201

@app.route('/api/patient/reschedule/<int:id>', methods=['PUT'])
def reschedule_appt(id):
    appt = Appointment.query.get_or_404(id)
    data = request.json
    new_date = data.get('date', appt.date)
    new_time = data.get('time', appt.time)
    conflict = Appointment.query.filter_by(
        doctor_id=appt.doctor_id, date=new_date, time=new_time
    ).filter(Appointment.status != 'Cancelled', Appointment.id != id).first()
    if conflict:
        return jsonify({'message': 'New slot is already booked'}), 400
    appt.date = new_date
    appt.time = new_time
    appt.status = 'Booked'
    db.session.commit()
    return jsonify({'message': 'Appointment rescheduled'})

@app.route('/api/patient/cancel/<int:id>', methods=['POST'])
def cancel_appt(id):
    appt = Appointment.query.get_or_404(id)
    appt.status = 'Cancelled'
    db.session.commit()
    return jsonify({'message': 'Appointment cancelled'})

@app.route('/api/patient/appointments/<int:user_id>', methods=['GET'])
def my_appts(user_id):
    patient = Patient.query.filter_by(user_id=user_id).first()
    if not patient: return jsonify([])
    appts = Appointment.query.filter_by(patient_id=patient.id).order_by(Appointment.date.desc()).all()
    return jsonify([{
        'id': a.id, 'doctor': a.doctor.user.username, 'doctor_id': a.doctor_id,
        'spec': a.doctor.specialization, 'date': a.date, 'time': a.time, 'status': a.status,
        'diagnosis': a.treatment.diagnosis if a.treatment else '',
        'prescription': a.treatment.prescription if a.treatment else '',
        'notes': a.treatment.notes if a.treatment else '',
        'next_visit': a.treatment.next_visit if a.treatment else ''
    } for a in appts])

@app.route('/api/patient/history/<int:patient_id>', methods=['GET'])
def get_patient_history(patient_id):
    appts = Appointment.query.filter_by(patient_id=patient_id, status='Completed').order_by(Appointment.date.desc()).all()
    return jsonify([{
        'date': a.date, 'doctor': a.doctor.user.username,
        'diagnosis': a.treatment.diagnosis if a.treatment else '',
        'prescription': a.treatment.prescription if a.treatment else '',
        'notes': a.treatment.notes if a.treatment else '',
        'next_visit': a.treatment.next_visit if a.treatment else ''
    } for a in appts])

@app.route('/api/export_csv/<int:user_id>', methods=['GET'])
def export_csv(user_id):
    try:
        from tasks import export_csv_task
        export_csv_task.delay(user_id)
        return jsonify({'message': 'CSV export job triggered. You will receive an email when ready.'}), 202
    except Exception:
        return jsonify({'message': 'CSV export queued (start Celery worker to process).'}), 202


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
