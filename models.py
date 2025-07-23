from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin' or 'intern'
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    post = db.Column(db.String(50))  # Human Resources, Business Development, etc.
    doj = db.Column(db.String(20))  # Date of joining
    reference_number = db.Column(db.String(20))
    is_poc = db.Column(db.Boolean, default=False)
    poc_name = db.Column(db.String(100))  # Name of the POC for this user
    
    # TND Targets
    target = db.Column(db.Integer, default=0)  # Total enrollments target
    tnd_total_target = db.Column(db.Integer, default=50)  # TND total target (default 50)
    ms_azure_900_target = db.Column(db.Integer, default=0)
    seo_starter_target = db.Column(db.Integer, default=0)
    seo_smm_target = db.Column(db.Integer, default=0)
    dm_crash_target = db.Column(db.Integer, default=0)
    job_ready_target = db.Column(db.Integer, default=0)
    azure_combo_target = db.Column(db.Integer, default=0)
    
    # Category Targets
    recruitment_target = db.Column(db.Integer, default=0)
    college_db_target = db.Column(db.Integer, default=0)
    client_db_target = db.Column(db.Integer, default=0)
    school_lead_db_target = db.Column(db.Integer, default=0)
    pms_entries = db.relationship('PMSEntry', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class PMSEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    
    # Excel format fields
    poc = db.Column(db.String(100))
    intern_name = db.Column(db.String(100))
    post = db.Column(db.String(50))  # Human Resources, Business Development, etc.
    section = db.Column(db.String(50))  # TND, COLLEGE COLLAB, etc.
    doj = db.Column(db.String(20))  # Date of joining
    reference_number = db.Column(db.String(20))
    email_id = db.Column(db.String(100))
    
    # Metrics
    total_enrollments = db.Column(db.Integer, default=0)
    mtd_leads = db.Column(db.Integer, default=0)  # Month to date leads
    ms_azure_900 = db.Column(db.Integer, default=0)
    seo_starter = db.Column(db.Integer, default=0)
    seo_smm = db.Column(db.Integer, default=0)
    dm_crash = db.Column(db.Integer, default=0)
    job_ready = db.Column(db.Integer, default=0)
    azure_combo = db.Column(db.Integer, default=0)
    recruitment = db.Column(db.Integer, default=0)
    college_db = db.Column(db.Integer, default=0)
    client_db = db.Column(db.Integer, default=0)
    school_lead_db = db.Column(db.Integer, default=0)
    
    # Daily metrics
    daily_leads_generated = db.Column(db.Integer, default=0)
    daily_leads_contacted = db.Column(db.Integer, default=0)
    daily_prospects = db.Column(db.Integer, default=0)
    daily_suspects = db.Column(db.Integer, default=0)
    
    # Recruitment specific metrics
    applications_received = db.Column(db.Integer, default=0)
    interviewed = db.Column(db.Integer, default=0)
    on_hold = db.Column(db.Integer, default=0)
    shortlisted = db.Column(db.Integer, default=0)
    rejected = db.Column(db.Integer, default=0)
    
    # Support/help required
    support_required = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)