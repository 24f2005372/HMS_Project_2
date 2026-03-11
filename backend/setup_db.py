from app import app, db
from models import User, Doctor, Patient, Department

with app.app_context():
    db.drop_all()
    db.create_all()

    # Create departments
    depts = [
        Department(name='Cardiology', description='Heart and cardiovascular system'),
        Department(name='Oncology', description='Cancer diagnosis and treatment'),
        Department(name='General Medicine', description='General health consultations'),
        Department(name='Orthopedics', description='Bone, joint and muscle care'),
        Department(name='Neurology', description='Brain and nervous system'),
    ]
    for d in depts:
        db.session.add(d)
    db.session.flush()

    # Create admin
    admin = User(username='admin', email='admin@hms.com', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)

    db.session.commit()
    print("✅ Database created with admin user (username: admin, password: admin123) and 5 departments.")
