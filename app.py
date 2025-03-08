from flask import Flask, render_template, redirect, url_for, session, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, ValidationError
import bcrypt
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__, static_url_path='/static')

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'madhura09'
app.config['MYSQL_DB'] = 'mydatabase'
app.secret_key = 'your_secret_key_here'

mysql = MySQL(app)

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    user_type = SelectField("User Type", choices=[('user', 'Regular User'), ('vet', 'Veterinarian')], validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self, field):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s", (field.data,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            raise ValidationError('Email Already Taken')

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class PetRegistrationForm(FlaskForm):
    name = StringField("Pet Name", validators=[DataRequired()])
    submit = SubmitField("Register Pet")

class PetCareForm(FlaskForm):
    pet_id = SelectField("Pet", coerce=int, validators=[DataRequired()])
    vet_id = SelectField("Veterinarian", coerce=int, validators=[DataRequired()])
    status = SelectField("Care Type", choices=[('vaccine', 'Vaccine'), ('daily_routine', 'Daily Routine'), ('checkup', 'Checkup'), ('other', 'Other')], validators=[DataRequired()])
    care_date = StringField("Care Date (YYYY-MM-DD)", validators=[DataRequired()])
    submit = SubmitField("Schedule Care")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        user_type = form.user_type.data

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (name, email, password, user_type) VALUES (%s, %s, %s, %s)", (name, email, hashed_password, user_type))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            session['user_id'] = user[0]
            session['user_type'] = user[4]  # Store user type in session
            return redirect(url_for('dashboard'))
        else:
            flash("Login failed. Please check your email and password")
            return redirect(url_for('login'))

    return render_template('login.html', form=form)

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        user_type = session['user_type']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        user = cursor.fetchone()

        if user_type == 'vet':
            cursor.execute("""
                SELECT p.name, pc.status, pc.care_date, u.name as owner_name
                FROM pet_care pc
                JOIN pets p ON pc.pet_id = p.id
                JOIN users u ON p.owner_id = u.id
                WHERE pc.vet_id = %s 
                ORDER BY pc.care_date DESC
            """, (user_id,))
            pets = cursor.fetchall()
            cursor.close()
            return render_template('vet_dashboard.html', user=user, pets=pets)
        else:
            cursor.execute("SELECT * FROM pets WHERE owner_id=%s", (user_id,))
            pets = cursor.fetchall()
            cursor.close()
            return render_template('user_dashboard.html', user=user, pets=pets)

    return redirect(url_for('login'))

@app.route('/register_pet', methods=['GET', 'POST'])
def register_pet():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    form = PetRegistrationForm()
    if form.validate_on_submit():
        name = form.name.data
        owner_id = session['user_id']

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO pets (name, owner_id) VALUES (%s, %s)", (name, owner_id))
        mysql.connection.commit()
        cursor.close()

        flash('Pet registered successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register_pet.html', form=form)

@app.route('/schedule_care', methods=['GET', 'POST'])
def schedule_care():
    if 'user_id' not in session or session['user_type'] != 'user':
        return redirect(url_for('login'))

    form = PetCareForm()

    # Populate the pet choices
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, name FROM pets WHERE owner_id = %s", (session['user_id'],))
    pets = cursor.fetchall()
    form.pet_id.choices = [(pet[0], pet[1]) for pet in pets]

    # Populate the vet choices
    cursor.execute("SELECT id, name FROM users WHERE user_type = 'vet'")
    vets = cursor.fetchall()
    form.vet_id.choices = [(vet[0], vet[1]) for vet in vets]

    if form.validate_on_submit():
        pet_id = form.pet_id.data
        vet_id = form.vet_id.data
        status = form.status.data
        care_date = datetime.strptime(form.care_date.data, '%Y-%m-%d').date()

        cursor.execute("INSERT INTO pet_care (pet_id, vet_id, status, care_date) VALUES (%s, %s, %s, %s)",
                       (pet_id, vet_id, status, care_date))
        mysql.connection.commit()
        cursor.close()

        flash('Care scheduled successfully!', 'success')
        return redirect(url_for('dashboard'))

    cursor.close()
    return render_template('schedule_care.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_type', None)
    flash("You have been logged out successfully.")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)