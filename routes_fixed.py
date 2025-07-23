from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, date
import uuid
import os
import csv
from models import db, User, PMSEntry
from app import app

# Constants
SECTIONS = ['Human Resources', 'Business Development', 'Sales & Marketing', 'Marketing']

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.role == 'admin':
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials', 'danger')
    
    return render_template('admin_login.html')

@app.route('/login', methods=['GET', 'POST'])
def intern_login():
    if current_user.is_authenticated and current_user.role == 'intern':
        return redirect(url_for('intern_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.role == 'intern':
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('intern_dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    
    return render_template('intern_login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('admin_login'))
    
    # Get all interns
    interns = User.query.filter_by(role='intern').all()
    
    # Get today's entries
    today = date.today()
    today_entries = PMSEntry.query.filter(PMSEntry.date == today).all()
    
    # Debug info
    print(f"Found {len(today_entries)} entries for today")
    for entry in today_entries:
        print(f"Entry: {entry.user.name}, {entry.post}, {entry.total_enrollments}")
    
    return render_template('admin_dashboard.html', interns=interns, entries=today_entries)

@app.route('/admin/analytics')
@login_required
def admin_analytics():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('admin_login'))
    
    # Get all interns
    interns = User.query.filter_by(role='intern').all()
    
    # Get all entries
    entries = PMSEntry.query.all()
    
    # Get today's entries
    today = date.today()
    today_entries = PMSEntry.query.filter(PMSEntry.date == today).all()
    
    # Get unique posts from interns
    posts = []
    for intern in interns:
        if intern.post and intern.post not in posts:
            posts.append(intern.post)
    
    # Calculate team performance data
    team_data = {}
    
    # Group interns by post instead of section
    for post in posts:
        post_interns = [i for i in interns if i.post == post]
        post_entries = []
        
        # Collect all entries for interns in this post
        for intern in post_interns:
            post_entries.extend(intern.pms_entries)
        
        if post_interns:
            # Find PoC (assuming is_poc flag is set in the database)
            poc = next((i for i in post_interns if i.is_poc), post_interns[0] if post_interns else None)
            
            # Calculate team progress
            target_per_intern = 50  # Default target per intern
            total_target = len(post_interns) * target_per_intern
            
            # Sum total enrollments from all entries
            total_achieved = sum(entry.total_enrollments for entry in post_entries if hasattr(entry, 'total_enrollments'))
            
            progress = int((total_achieved / total_target * 100) if total_target > 0 else 0)
            
            team_data[post] = {
                'poc': poc,
                'members': post_interns,
                'progress': progress,
                'total_target': total_target,
                'total_achieved': total_achieved,
                'entries': post_entries
            }
    
    # Calculate summary metrics
    total_interns = len(interns)
    total_enrollments = sum(entry.total_enrollments for intern in interns 
                           for entry in intern.pms_entries if hasattr(entry, 'total_enrollments'))
    
    # Calculate overall progress (assuming target is 50 per intern)
    target_per_intern = 50
    total_target = total_interns * target_per_intern
    overall_progress = int((total_enrollments / total_target * 100) if total_target > 0 else 0)
    
    # Calculate school lead DB total
    school_lead_db = sum(entry.school_lead_db for intern in interns 
                        for entry in intern.pms_entries if hasattr(entry, 'school_lead_db'))
    
    # Prepare metrics for the template
    metrics = {
        'total_interns': total_interns,
        'total_enrollments': total_enrollments,
        'overall_progress': overall_progress,
        'school_lead_db': school_lead_db
    }
    
    # Prepare data for section chart
    section_labels = []
    section_targets = []
    section_achievements = []
    
    for post in posts:
        section_labels.append(post)
        post_interns = [i for i in interns if i.post == post]
        post_target = len(post_interns) * target_per_intern
        section_targets.append(post_target)
        
        post_achievements = sum(entry.total_enrollments for intern in post_interns 
                              for entry in intern.pms_entries if hasattr(entry, 'total_enrollments'))
        section_achievements.append(post_achievements)
    
    # Prepare data for trend chart
    trend_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    trend_data = []
    
    for post in posts:
        trend_data.append({
            'label': post,
            'data': [],  # This would be filled from actual data in a real implementation
            'borderColor': get_color_for_post(post),
            'backgroundColor': get_background_color_for_post(post),
            'borderWidth': 2,
            'fill': True,
            'tension': 0.4
        })
    
    # Prepare data for comparison chart
    comparison_labels = ['Leads', 'Prospects', 'Suspects', 'Conversions', 'Follow-ups']
    comparison_data = []
    
    for post in posts:
        comparison_data.append({
            'label': f'{post} Team',
            'data': [],  # This would be filled from actual data in a real implementation
            'backgroundColor': get_background_color_for_post(post, 0.2),
            'borderColor': get_color_for_post(post),
            'borderWidth': 2,
            'pointBackgroundColor': get_color_for_post(post)
        })
    
    # Prepare data for distribution chart
    distribution_labels = posts
    distribution_data = []
    
    for post in posts:
        post_achievements = sum(entry.total_enrollments for intern in interns if intern.post == post 
                              for entry in intern.pms_entries if hasattr(entry, 'total_enrollments'))
        distribution_data.append(post_achievements)
    
    return render_template('admin_analytics.html', 
                          interns=interns, 
                          entries=today_entries, 
                          all_entries=entries,
                          team_data=team_data,
                          sections=SECTIONS,
                          posts=posts,
                          metrics=metrics,
                          section_labels=section_labels,
                          section_targets=section_targets,
                          section_achievements=section_achievements,
                          trend_months=trend_months,
                          trend_data=trend_data,
                          comparison_labels=comparison_labels,
                          comparison_data=comparison_data,
                          distribution_labels=distribution_labels,
                          distribution_data=distribution_data)

# Helper function to get color for post
def get_color_for_post(post):
    color_map = {
        'Human Resources': '#17a2b8',
        'Business Development': '#28a745',
        'Sales & Marketing': '#6f42c1',
        'Marketing': '#dc3545'
    }
    return color_map.get(post, '#6c757d')  # Default gray color

# Helper function to get background color for post
def get_background_color_for_post(post, alpha=0.1):
    color = get_color_for_post(post)
    # Convert hex to rgba
    if color.startswith('#'):
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        return f'rgba({r}, {g}, {b}, {alpha})'
    return color

@app.route('/admin/upload_data', methods=['POST'])
@login_required
def upload_data():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('admin_login'))
    
    if 'dataFile' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('admin_analytics'))
    
    file = request.files['dataFile']
    
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('admin_analytics'))
    
    if file and (file.filename.endswith('.xlsx') or file.filename.endswith('.csv')):
        try:
            # Save the file temporarily
            file_path = os.path.join('instance', 'temp_data_file')
            file.save(file_path)
            
            # Process the file based on its type
            if file.filename.endswith('.xlsx'):
                # Check if pandas is installed
                try:
                    import pandas as pd
                except ImportError:
                    flash('Pandas library not installed. Please run the install_packages.py script or install manually using "pip install pandas openpyxl".', 'danger')
                    return redirect(url_for('admin_analytics'))
                
                try:
                    # Check if openpyxl is installed
                    try:
                        import openpyxl
                    except ImportError:
                        flash('Openpyxl library not installed. Please run the install_packages.py script or install manually using "pip install openpyxl".', 'danger')
                        return redirect(url_for('admin_analytics'))
                    
                    # Helper function to safely convert values to integers
                    def safe_int(value):
                        if pd.isna(value) or value == '-' or value == '':
                            return 0
                        try:
                            return int(value)
                        except (ValueError, TypeError):
                            return 0
                    
                    # Read the Excel file
                    df = pd.read_excel(file_path)
                    
                    # Process each row in the dataframe
                    for index, row in df.iterrows():
                        # Skip header or empty rows
                        if pd.isna(row['Intern Name']) or row['Intern Name'] == 'Intern Name':
                            continue
                            
                        # Check if user exists, create if not
                        user = User.query.filter_by(name=row['Intern Name']).first()
                        if not user:
                            username = row['Email Id'].split('@')[0] if not pd.isna(row['Email Id']) else row['Intern Name'].lower().replace(' ', '.')
                            # Convert pandas Timestamp to string if needed
                            doj = row['DOJ']
                            if isinstance(doj, pd.Timestamp):
                                doj = doj.strftime('%Y-%m-%d')
                            
                            user = User(
                                username=username,
                                name=row['Intern Name'],
                                email=row['Email Id'] if not pd.isna(row['Email Id']) else None,
                                role='intern',
                                post=row['Post'] if not pd.isna(row['Post']) else None,
                                doj=doj if not pd.isna(row['DOJ']) else None,
                                reference_number=row['Reference Number'] if not pd.isna(row['Reference Number']) else None,
                                poc_name=row['POC'] if not pd.isna(row['POC']) else None,
                                is_poc=False
                            )
                            user.set_password('password123')  # Default password
                            db.session.add(user)
                            db.session.flush()  # Get user ID without committing
                        
                        # Create or update PMS entry
                        # Convert pandas Timestamp to string if needed
                        doj = row['DOJ']
                        if isinstance(doj, pd.Timestamp):
                            doj = doj.strftime('%Y-%m-%d')
                            
                        entry = PMSEntry(
                            user_id=user.id,
                            date=datetime.now().date(),
                            poc=row['POC'] if not pd.isna(row['POC']) else None,
                            intern_name=row['Intern Name'],
                            post=row['Post'] if not pd.isna(row['Post']) else None,
                            doj=doj if not pd.isna(row['DOJ']) else None,
                            reference_number=row['Reference Number'] if not pd.isna(row['Reference Number']) else None,
                            email_id=row['Email Id'] if not pd.isna(row['Email Id']) else None,
                            total_enrollments=safe_int(row['Total Enrollments']),
                            ms_azure_900=safe_int(row['MS Azure 900']),
                            seo_starter=safe_int(row['SEO Starter']),
                            seo_smm=safe_int(row['SEO + SMM']),
                            dm_crash=safe_int(row['DM-Crash']),
                            job_ready=safe_int(row['8Hrs Job Ready']),
                            azure_combo=safe_int(row['Azure Combo']),
                            recruitment=safe_int(row['Recruitment']),
                            college_db=safe_int(row['College DB']),
                            client_db=safe_int(row['Client DB']),
                            school_lead_db=safe_int(row['School Lead DB'])
                        )
                        db.session.add(entry)
                    
                    # Set POC flags for users who are POCs
                    poc_names = df['POC'].dropna().unique()
                    for poc_name in poc_names:
                        poc_user = User.query.filter_by(name=poc_name).first()
                        if poc_user:
                            poc_user.is_poc = True
                    
                    # Commit all changes
                    db.session.commit()
                    flash(f'Excel file processed successfully. {len(df)} records imported.', 'success')
                    
                except ImportError:
                    flash('Pandas library not installed. Please install it to process Excel files.', 'danger')
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error processing Excel file: {str(e)}', 'danger')
            else:  # CSV file
                try:
                    # Helper function to safely convert values to integers
                    def safe_int(value):
                        if not value or value == '-' or value == '':
                            return 0
                        try:
                            return int(value)
                        except (ValueError, TypeError):
                            return 0
                            
                    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                        reader = csv.DictReader(csvfile)
                        row_count = 0
                        
                        for row in reader:
                            # Check if user exists, create if not
                            user = User.query.filter_by(name=row['Intern Name']).first()
                            if not user:
                                username = row['Email Id'].split('@')[0] if row['Email Id'] else row['Intern Name'].lower().replace(' ', '.')
                                user = User(
                                    username=username,
                                    name=row['Intern Name'],
                                    email=row['Email Id'] if row['Email Id'] else None,
                                    role='intern',
                                    post=row['Post'] if row['Post'] else None,
                                    doj=row['DOJ'] if row['DOJ'] else None,
                                    reference_number=row['Reference Number'] if row['Reference Number'] else None,
                                    poc_name=row['POC'] if row['POC'] else None,
                                    is_poc=False
                                )
                                user.set_password('password123')  # Default password
                                db.session.add(user)
                                db.session.flush()  # Get user ID without committing
                            
                            # Create or update PMS entry
                            entry = PMSEntry(
                                user_id=user.id,
                                date=datetime.now().date(),
                                poc=row['POC'] if row['POC'] else None,
                                intern_name=row['Intern Name'],
                                post=row['Post'] if row['Post'] else None,
                                doj=row['DOJ'] if row['DOJ'] else None,
                                reference_number=row['Reference Number'] if row['Reference Number'] else None,
                                email_id=row['Email Id'] if row['Email Id'] else None,
                                total_enrollments=safe_int(row['Total Enrollments']),
                                ms_azure_900=safe_int(row['MS Azure 900']),
                                seo_starter=safe_int(row['SEO Starter']),
                                seo_smm=safe_int(row['SEO + SMM']),
                                dm_crash=safe_int(row['DM-Crash']),
                                job_ready=safe_int(row['8Hrs Job Ready']),
                                azure_combo=safe_int(row['Azure Combo']),
                                recruitment=safe_int(row['Recruitment']),
                                college_db=safe_int(row['College DB']),
                                client_db=safe_int(row['Client DB']),
                                school_lead_db=safe_int(row['School Lead DB'])
                            )
                            db.session.add(entry)
                            row_count += 1
                        
                        # Set POC flags for users who are POCs
                        poc_names = set()
                        csvfile.seek(0)  # Reset file pointer
                        reader = csv.DictReader(csvfile)
                        for row in reader:
                            if row['POC']:
                                poc_names.add(row['POC'])
                        
                        for poc_name in poc_names:
                            poc_user = User.query.filter_by(name=poc_name).first()
                            if poc_user:
                                poc_user.is_poc = True
                        
                        # Commit all changes
                        db.session.commit()
                        flash(f'CSV file processed successfully. {row_count} records imported.', 'success')
                        
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error processing CSV file: {str(e)}', 'danger')
            
            # Clean up the temporary file
            if os.path.exists(file_path):
                os.remove(file_path)
                
        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'danger')
    else:
        flash('Invalid file type. Please upload an Excel (.xlsx) or CSV (.csv) file.', 'danger')
    
    return redirect(url_for('admin_analytics'))

@app.route('/admin/delete_all_data')
@login_required
def delete_all_data():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('admin_login'))
    
    try:
        # Delete all PMS entries
        PMSEntry.query.delete()
        
        # Keep admin users but delete all interns
        User.query.filter_by(role='intern').delete()
        
        # Commit the changes
        db.session.commit()
        
        flash('All data has been successfully deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting data: {str(e)}', 'danger')
    
    return redirect(url_for('admin_analytics'))

@app.route('/admin/team-management')
@login_required
def team_management():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('admin_login'))
    
    # Get all interns
    interns = User.query.filter_by(role='intern').all()
    
    return render_template('team_management.html', interns=interns)

@app.route('/admin/users')
@login_required
def manage_users():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@app.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        name = request.form.get('name')
        email = request.form.get('email')
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('add_user'))
        
        user = User(username=username, role=role, name=name, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('User added successfully', 'success')
        return redirect(url_for('manage_users'))
    
    return render_template('add_user.html')

@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.role = request.form.get('role')
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        
        if request.form.get('password'):
            user.set_password(request.form.get('password'))
        
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('manage_users'))
    
    return render_template('edit_user.html', user=user)

@app.route('/admin/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    if user.username == 'admin':
        flash('Cannot delete admin user', 'danger')
        return redirect(url_for('manage_users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash('User deleted successfully', 'success')
    return redirect(url_for('manage_users'))

@app.route('/admin/reports')
@login_required
def admin_reports():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    # Get filter parameters
    user_id = request.args.get('user_id', type=int)
    section = request.args.get('section')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Base query
    query = PMSEntry.query
    
    # Apply filters
    if user_id:
        query = query.filter_by(user_id=user_id)
    if section:
        query = query.filter_by(section=section)
    if start_date:
        query = query.filter(PMSEntry.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(PMSEntry.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    # Get entries
    entries = query.order_by(PMSEntry.date.desc()).all()
    
    # Get all interns for filter dropdown
    interns = User.query.filter_by(role='intern').all()
    
    return render_template('admin_reports.html', entries=entries, interns=interns, sections=SECTIONS)

@app.route('/intern/dashboard')
@login_required
def intern_dashboard():
    if current_user.role != 'intern':
        flash('Access denied. Intern privileges required.', 'danger')
        return redirect(url_for('intern_login'))
    
    # Get today's entries for the current user
    today = date.today()
    today_entries = PMSEntry.query.filter_by(user_id=current_user.id, date=today).all()
    
    # Create a dictionary to store entries by section
    entries_by_section = {section: None for section in SECTIONS}
    
    # Fill in existing entries
    for entry in today_entries:
        if hasattr(entry, 'section') and entry.section in entries_by_section:
            entries_by_section[entry.section] = entry
    
    # Get all interns for team structure
    interns = User.query.filter_by(role='intern').all()
    
    return render_template('dashboard.html', 
                           entries_by_section=entries_by_section, 
                           sections=SECTIONS,
                           interns=interns)

@app.route('/intern/update_pms', methods=['POST'])
@login_required
def update_pms():
    if current_user.role != 'intern':
        flash('Access denied. Intern privileges required.', 'danger')
        return redirect(url_for('intern_login'))
    
    section = request.form.get('section')
    
    if section not in SECTIONS:
        flash('Invalid section', 'danger')
        return redirect(url_for('intern_dashboard'))
    
    today = date.today()
    
    # Check if entry already exists for today and this section
    entry = PMSEntry.query.filter_by(
        user_id=current_user.id,
        date=today,
        section=section
    ).first()
    
    # If entry doesn't exist, create a new one
    if not entry:
        entry = PMSEntry(
            user_id=current_user.id,
            date=today,
            section=section
        )
        db.session.add(entry)
    
    # Update entry fields
    entry.total_enrollments = request.form.get('total_enrollments', type=int) or 0
    entry.ms_azure_900 = request.form.get('ms_azure_900', type=int) or 0
    entry.seo_starter = request.form.get('seo_starter', type=int) or 0
    entry.seo_smm = request.form.get('seo_smm', type=int) or 0
    entry.dm_crash = request.form.get('dm_crash', type=int) or 0
    entry.job_ready = request.form.get('job_ready', type=int) or 0
    entry.azure_combo = request.form.get('azure_combo', type=int) or 0
    entry.recruitment = request.form.get('recruitment', type=int) or 0
    entry.college_db = request.form.get('college_db', type=int) or 0
    entry.client_db = request.form.get('client_db', type=int) or 0
    entry.school_lead_db = request.form.get('school_lead_db', type=int) or 0
    
    db.session.commit()
    
    flash(f'{section} data updated successfully', 'success')
    return redirect(url_for('intern_dashboard'))

@app.route('/intern/history')
@login_required
def intern_history():
    if current_user.role != 'intern':
        flash('Access denied. Intern privileges required.', 'danger')
        return redirect(url_for('intern_login'))
    
    # Get filter parameters
    section = request.args.get('section')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Base query for current user's entries
    query = PMSEntry.query.filter_by(user_id=current_user.id)
    
    # Apply filters
    if section:
        query = query.filter_by(section=section)
    if start_date:
        query = query.filter(PMSEntry.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(PMSEntry.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    # Get entries
    entries = query.order_by(PMSEntry.date.desc()).all()
    
    return render_template('intern_history.html', entries=entries, sections=SECTIONS)