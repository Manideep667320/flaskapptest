from flask import Flask, render_template, redirect, request, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management and flash messages

# Function to create a database connection
def create_connection():
    conn = sqlite3.connect('Database.db')
    return conn

# Function to create the required table
def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

# Route for the login/register page
@app.route('/login_register', methods=['GET', 'POST'])
def login_register():
    if request.method == 'POST':
        # Handle Registration
        if 'name' in request.form:  # If the form contains 'name', it's a registration request
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']

            conn = create_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
                conn.commit()
                flash("Registration successful! Please log in.", "success")
            except sqlite3.IntegrityError:
                flash("Email already exists. Please try logging in or use a different email.", "error")
            finally:
                conn.close()
            return redirect('/login_register')

        # Handle Login
        elif 'email' in request.form and 'password' in request.form:  # Login form
            email = request.form['email']
            password = request.form['password']

            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
            user = cursor.fetchone()
            conn.close()

            if user:
                session['name'] = user[1]  # Set session with user name
                session['email'] = user[2]  # Set session with user email
                return redirect('/profile')
            else:
                flash("Invalid email or password. Please try again.", "error")
                return redirect('/login_register')
    return render_template('login_register.html')

# Route for the profile page
@app.route('/profile')
def profile():
    if 'name' in session:
        return render_template(
            'profile.html',
            username=session['name'],
            email=session['email'],
        )
    return redirect('/login_register')

# Route for the logout functionality
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect('/')

if __name__ == '__main__':
    create_table()  # Create table if not exists
    app.run(debug=True)
