from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime, timedelta

app = Flask(__name__)

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reservation.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email config (Gmail SMTP)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'titancaptain51@gmail.com'
app.config['MAIL_PASSWORD'] = 'vtxy ngvy jpfy chkt'  # App password
app.config['MAIL_DEFAULT_SENDER'] = 'titancaptain51@gmail.com'

db = SQLAlchemy(app)
mail = Mail(app)

# Database model
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    date = db.Column(db.String(20))
    time = db.Column(db.String(10))
    seats = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Reservation {self.name}>"

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# Reservation route
@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        date = request.form['date']
        time = request.form['time']

        try:
            seats = int(request.form.get('seats', 1))
        except ValueError:
            return render_template('reserve.html', error="Invalid seat number. Please enter a valid number of seats.")

        if seats < 1 or seats > 6:
            return render_template('reserve.html', error="Please choose a valid number of seats (1–6).")

        twelve_hours_ago = datetime.utcnow() - timedelta(hours=12)

        recent_email = Reservation.query.filter(
            Reservation.email == email,
            Reservation.created_at > twelve_hours_ago
        ).first()

        if recent_email:
            return render_template(
                'limit_reached.html',
                message="You can only make a reservation once every 12 hours from the same email address."
            )

        if Reservation.query.count() >= 10:
            return render_template('limit_reached.html', message="Sorry, the reservation limit of 10 has been reached.")

        new_reservation = Reservation(
            name=name,
            email=email,
            date=date,
            time=time,
            seats=seats
        )
        db.session.add(new_reservation)
        db.session.commit()

        send_confirmation_email(email, name)

        return render_template('thank_you.html', name=name)

    return render_template('reserve.html')

# View bookings
@app.route('/bookings')
def bookings():
    reservations = Reservation.query.all()
    return render_template('bookings.html', reservations=reservations)

# Email sender
def send_confirmation_email(customer_email, name):
    msg = Message('Reservation Confirmation', recipients=[customer_email])
    msg.body = f"Thank you, {name}!\nYour reservation has been successfully made.\nWe look forward to seeing you!"
    try:
        mail.send(msg)
        print(f"Confirmation email sent to {customer_email}")
    except Exception as e:
        print(f"Failed to send confirmation email: {e}")

# App runner
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

