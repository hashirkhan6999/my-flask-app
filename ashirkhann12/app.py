from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from datetime import datetime, timedelta, date
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from flask_migrate import Migrate
from flask import request 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'
migrate = Migrate(app, db)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    people = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    canceled = db.Column(db.Boolean, default=False)
    canceled_at = db.Column(db.DateTime, nullable=True)
    table_number = db.Column(db.Integer, nullable=True)
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def setup_admin():
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/cancel', methods=['GET', 'POST'])
def cancel_reservation():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        if not email:
            flash("Please enter your email to cancel.")
            return redirect(url_for('cancel_reservation'))
        
        active_reservations = Reservation.query.filter_by(email=email, canceled=False).all()
        if not active_reservations:
            flash("No active reservations found for this email.")
            return redirect(url_for('cancel_reservation'))
        
        for res in active_reservations:
            res.canceled = True
            res.canceled_at = datetime.utcnow()
        db.session.commit()
        
        send_cancellation_email(email, len(active_reservations))
        flash(f"Your {len(active_reservations)} reservation(s) have been canceled. A confirmation email has been sent.")
        return redirect(url_for('home'))
    
    return render_template('cancel.html')

def send_cancellation_email(to_email, count):
    sender = "titancaptain51@gmail.com"
    password = "qivx vrxk jnnc atdx"
    subject = "Reservation Cancellation Confirmation"
    body = f"Hello,\n\nYour reservation has been successfully canceled.\n\nThank you!"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender, password)
        server.sendmail(sender, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        print("Failed to send cancellation email:", e)

@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        date_str = request.form.get('date', '').strip()
        time_str = request.form.get('time', '').strip()
        people_str = request.form.get('people', '').strip()
        notes = request.form.get('notes', '').strip()

        if not all([name, email, phone, date_str, time_str, people_str]):
            flash("Please fill in all fields.")
            return redirect(url_for('reserve'))

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            time_obj_val = datetime.strptime(time_str, "%H:%M").time()
            people = int(people_str)
        except ValueError:
            flash("Invalid input format.")
            return redirect(url_for('reserve'))

        today = date.today()
        if date_obj < today:
            flash("You cannot book a reservation for previous days.")
            return redirect(url_for('reserve'))

        if time_obj_val < datetime.strptime("09:00", "%H:%M").time() or time_obj_val > datetime.strptime("19:00", "%H:%M").time():
            flash("You can only book a reservation between 9:00 AM and 7:00 PM.")
            return redirect(url_for('reserve'))

      
        recent_booking = Reservation.query.filter(
            Reservation.email == email,
            Reservation.date == date_obj,
            Reservation.time == time_obj_val,
            Reservation.created_at >= datetime.utcnow() - timedelta(minutes=30),
            Reservation.canceled == False
        ).first()

        if recent_booking:
            flash("You’ve already made a reservation recently for this time. Try again after 30 minutes.")
            return redirect(url_for('reserve'))

       
        table_definitions = [
            {"number": 1, "seats": 1},
            {"number": 2, "seats": 2},
            {"number": 3, "seats": 3},
            {"number": 4, "seats": 4},
            {"number": 5, "seats": 5},
            {"number": 6, "seats": 6},
            {"number": 7, "seats": 2},
            {"number": 8, "seats": 4},
            {"number": 9, "seats": 3},
            {"number": 10, "seats": 1}
        ]

        reservation_datetime = datetime.combine(date_obj, time_obj_val)
        buffer_minutes = 60  

        available_table = None

        for table in table_definitions:
            if table["seats"] < people:
                continue


            conflicting_reservations = Reservation.query.filter(
                Reservation.date == date_obj,
                Reservation.canceled == False,
                Reservation.people <= table["seats"]
            ).all()

            conflict_found = False
            for res in conflicting_reservations:
                existing_datetime = datetime.combine(res.date, res.time)
                time_diff = abs((existing_datetime - reservation_datetime).total_seconds()) / 60

                if time_diff < buffer_minutes:
 
                    conflict_found = True
                    break

            if not conflict_found:
                available_table = table
                break

        if not available_table:
            flash("No available tables for this time. Please try another time.")
            return redirect(url_for('reserve'))

       
        new_reservation = Reservation(
            name=name,
            email=email,
            phone=phone,
            date=date_obj,
            time=time_obj_val,
            people=people,
            notes=notes,
            table_number=available_table["number"]
        )
        db.session.add(new_reservation)
        db.session.commit()

        send_confirmation_email(
            email, name, date_str, time_str, people, new_reservation.id, available_table["number"]
        )
        return redirect(url_for('thank_you', name=name))

    return render_template('reserve.html')

def send_confirmation_email(to_email, name, date_str, time_str, people, res_id, table_number):
    sender = "titancaptain51@gmail.com"
    password = "qivx vrxk jnnc atdx"
    subject = "Reservation Confirmed"
    body = f"""Hello {name},

Your reservation for {people} people on {date_str} at {time_str} is confirmed.
Your table number is: {table_number}.
Reservation ID: {res_id}.

Thank you!"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender, password)
        server.sendmail(sender, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        print("Failed to send email:", e)

@app.route('/thank_you')
def thank_you():
    name = request.args.get('name')
    return render_template('thank_you.html', name=name)

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('bookings'))
        flash("Invalid credentials.")
    return render_template('admin_login.html')

@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_reservation(id):
    reservation = Reservation.query.get_or_404(id)
    db.session.delete(reservation)
    db.session.commit()
    flash("Reservation deleted successfully.")
    return redirect(url_for('bookings'))

@app.route('/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

@app.route('/bookings')
@login_required
def bookings():
    search_id = request.args.get('search_id', type=int) 
    today = date.today()

    if search_id:
       
        matched_reservations = Reservation.query.filter(
            Reservation.id == search_id,
            Reservation.canceled == False
        ).all()

       
        todays_bookings = [r for r in matched_reservations if r.date == today]
        future_bookings = [r for r in matched_reservations if r.date > today]

        
        canceled_reservations = []
    else:
        
        todays_bookings = Reservation.query.filter(
            Reservation.date == today,
            Reservation.canceled == False
        ).order_by(Reservation.time.asc()).all()

        future_bookings = Reservation.query.filter(
            Reservation.date > today,
            Reservation.canceled == False
        ).order_by(Reservation.date.asc(), Reservation.time.asc()).all()

        canceled_reservations = Reservation.query.filter(
            Reservation.canceled == True
        ).order_by(Reservation.canceled_at.desc()).all()


    table_definitions = [
        {"number": 1, "seats": 1},
        {"number": 2, "seats": 2},
        {"number": 3, "seats": 3},
        {"number": 4, "seats": 4},
        {"number": 5, "seats": 5},
        {"number": 6, "seats": 6},
        {"number": 7, "seats": 2},
        {"number": 8, "seats": 4},
        {"number": 9, "seats": 3},
        {"number": 10, "seats": 1}
    ]

    availability = {t["number"]: True for t in table_definitions}
    assigned_tables = {}

    for res in todays_bookings:
        suitable = [t for t in table_definitions if t["seats"] >= res.people and availability[t["number"]]]
        if suitable:
            assigned = suitable[0]
            assigned_tables[res.id] = assigned["number"]
            availability[assigned["number"]] = False
        else:
            assigned_tables[res.id] = None

    tables_info = []
    for t in table_definitions:
        tables_info.append({
            "number": t["number"],
            "seats": t["seats"],
            "status": "reserved" if not availability[t["number"]] else "available"
        })

    table_rows = [tables_info[i:i+3] for i in range(0, len(tables_info), 3)]

    bookings_with_expiration = []
    for res in todays_bookings:
        expiration = res.created_at + timedelta(minutes=30)
        bookings_with_expiration.append({
            "reservation": res,
            "expiration": expiration
        })

    return render_template(
        'admin_dashboard.html',
        todays_bookings=todays_bookings,
        future_bookings=future_bookings,
        canceled_reservations=canceled_reservations,
        assigned_tables=assigned_tables,
        table_rows=table_rows,
        datetime=datetime,
        timedelta=timedelta,
        bookings_with_expiration=bookings_with_expiration,
        search_id=search_id 
    )

if __name__ == '__main__':
    app.run(debug=True, port=5500, host='0.0.0.0')





