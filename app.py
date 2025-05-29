from flask import Flask, request, render_template, redirect, session, flash, jsonify
from models import db, User, Profile, BloodBank
from datetime import datetime, date
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret_key'
# app.config['UPLOAD_FOLDER'] = 'static/uploads'

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf'}  # Allowed file types

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)  # Create folder if it doesn't exist

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        profile = Profile.query.filter_by(user_id=user.id).first()
        profile_completed = profile is not None and profile.latitude is not None and profile.longitude is not None
        
        # Fetch donation history if the profile is completed
        donation_history = []
        if profile_completed:
            if profile.last_donation:
                donation_history.append({
                    "date": profile.last_donation.strftime('%d-%m-%Y')
                })
        
        return render_template('index.html', user=user, profile_completed=profile_completed, donation_history=donation_history)
    return render_template('index.html', user=None, profile_completed=False, donation_history=[])


@app.route('/about')
def about():
    user = None
    if 'email' in session:  # Check if the user is logged in
        user = User.query.filter_by(email=session['email']).first()
    return render_template('about.html', user=user)

@app.route('/contact')
def contact():
    user = None
    if 'email' in session:  # Check if the user is logged in
        user = User.query.filter_by(email=session['email']).first()
    return render_template('contact.html', user=user)

@app.route('/profile')
def profile():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        if user:
            return render_template('profile.html', user=user)
    
    return render_template('profile.html', user=None)  # Handle case where user is not logged in




@app.route('/register_donor', methods=['GET', 'POST'])
def register_donor():
    if request.method == 'POST':
        print("Form data received:", request.form)  # Log form data to see if it's received correctly

        if request.form['password'] != request.form['confirm_password']:
            print("Passwords do not match")
            flash('Passwords do not match!', 'error')
            return redirect('/register')
            # return render_template('register.html', error="Passwords do not match")

        if User.query.filter_by(email=request.form['email']).first():
            print("User already exists")
            return jsonify({"message": "User already exists"}), 400  # Return error message in JSON format
            # return render_template('register.html', error="User already exists")

        try:
            dob = datetime.strptime(request.form['dob'], '%Y-%m-%d').date()
            # Check if 'last_donation' is provided, otherwise set it to None
            # if request.form['last_donation']:
            #     last_donation = datetime.strptime(request.form['last_donation'], '%Y-%m-%d').date()
            # else:
            #     last_donation = date(1, 1, 1)  # User didn't provide the date, make it None
            # latitude = float(request.form['latitude'])
            # longitude = float(request.form['longitude'])
            # donated_before = request.form['donated_before'].lower() == 'yes'
        except ValueError:
            print("Invalid date format")
            return render_template('register.html', error="Invalid date format")

        new_user = User(
            name=request.form['name'],
            dob=dob,
            phone=request.form['phone'],
            email=request.form['email'],
            address=request.form['address'],
            state=request.form['state'],
            city=request.form['city'],
            pincode=request.form['pincode'],
            bloodgroup=request.form['bloodgroup'],
            # latitude=latitude,
            # longitude=longitude,
            # donated_before=donated_before,
            # last_donation=last_donation,
            password=request.form['password']
        )

        db.session.add(new_user)
        db.session.commit()
        
        print("User registered successfully!")
        return jsonify({"message": "Registration Successful. You can now login"}), 200
        return redirect('/login')

    return render_template('register.html')

# @app.route('/register_donor', methods=['POST'])
# def register_donor():
#     # You can call your existing register() logic here
#     return register()


@app.route('/register_bank', methods=['POST'])
def register_bank():
    if request.form['password'] != request.form['confirm_password']:
        flash('Passwords do not match!', 'error')
        return jsonify({"message": "Passwords do not match"}), 400

    if BloodBank.query.filter_by(email=request.form['email']).first():
        return jsonify({"message": "Blood bank already registered with this email"}), 400

    try:
        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])
    except (ValueError, KeyError):
        return jsonify({"message": "Invalid or missing location data"}), 400

    new_bank = BloodBank(
        name=request.form['name'],
        phone=request.form['phone'],
        email=request.form['email'],
        address=request.form['address'],
        state=request.form['state'],
        city=request.form['city'],
        pincode=request.form['pincode'],
        latitude=latitude,
        longitude=longitude,
        password=request.form['password']
    )

    db.session.add(new_bank)
    db.session.commit()
    
    return jsonify({"message": "Blood Bank Registration Successful. You can now login"}), 200

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        # if user and user.check_password(password):
        if user and user.password == password:
            session['email'] = user.email
            return redirect('/')
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')





@app.route('/logout')
def logout():
    session.pop('email', None)
    flash("You have been logged out successfully.")
    response = redirect('/login')
    # Set headers to prevent caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response




@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'email' not in session:
        flash("Unauthorized access. Please log in to update your profile.", "error")
        return redirect('/login')

    user = User.query.filter_by(email=session['email']).first()
    if not user:
        flash("User not found. Please try again.", "error")
        return redirect('/profile')

    profile = Profile.query.filter_by(user_id=user.id).first()
    if not profile:
        # If no profile exists, create a new one
        profile = Profile(user_id=user.id)
        db.session.add(profile)

    print("Form Data:", request.form.to_dict())

    try:
        # Update user details
        user.name = request.form['name']
        dob_str = request.form.get('dob')
        try:
            user.dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format for DOB. Please use YYYY-MM-DD.", "error")
            return redirect('/profile')

        user.phone = request.form['phone']
        user.email = request.form['email']
        user.address = request.form['address']
        user.state = request.form['state']
        user.city = request.form['city']
        user.pincode = request.form['pincode']
        user.bloodgroup = request.form['bloodgroup']

        # Update profile details
        profile.address = request.form['address']
        profile.state = request.form['state']
        profile.city = request.form['city']
        profile.pincode = request.form['pincode']
        profile.latitude = request.form.get('latitude', type=float)
        profile.longitude = request.form.get('longitude', type=float)
        profile.donated_before = request.form.get('donated_before') == 'yes'
        last_donation = request.form.get('last_donation')
        profile.last_donation = datetime.strptime(last_donation, '%Y-%m-%d').date() if last_donation else None
        profile.emergency_donation = 'emergency_donation' in request.form
        profile.on_medication = 'on_medication' in request.form
        profile.medical_conditions = request.form.get('medical_conditions', '')

        db.session.commit()
        flash("Profile updated successfully!", "success")
    except Exception as e:
        db.session.rollback()
        print("Error updating database:", str(e))  # Debugging
        flash("An error occurred while updating your profile. Please try again.", "error")

    return redirect('/profile')



# MAP
@app.route('/map')
def show_map():
    user = None
    if 'email' in session:  # Check if the user is logged in
        user = User.query.filter_by(email=session['email']).first()
    return render_template('map.html', user=user)


@app.route('/api/donors')
def api_donors():
    profiles = Profile.query.join(User).filter(
        Profile.latitude.isnot(None),
        Profile.longitude.isnot(None)
    ).all()

    donor_list = []
    for profile in profiles:
        donor_list.append({
            "name": profile.user.name,
            "bloodgroup": profile.user.bloodgroup,
            "city": profile.user.city,
            "latitude": profile.latitude,
            "longitude": profile.longitude,
             "contact": profile.user.phone  # Ensure this field is included
        })
    return jsonify(donor_list)

@app.route('/api/blood_banks')
def api_blood_banks():
    blood_banks = BloodBank.query.all()

    blood_bank_list = []
    for bank in blood_banks:
        blood_bank_list.append({
            "name": bank.name,
            "city": bank.city,
            "latitude": bank.latitude,
            "longitude": bank.longitude,
            "contact": bank.phone
        })
    return jsonify(blood_bank_list)


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    app.run(debug=True)
