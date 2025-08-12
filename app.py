from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import mysql.connector
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='0502',
    database='evoting'
)
cursor = conn.cursor(dictionary=True)

# -------- Helper decorators --------
def admin_login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('admin_logged_in'):
            return f(*args, **kwargs)
        return redirect(url_for('adminlogin'))
    return decorated

def voter_login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('voterid'):
            return f(*args, **kwargs)
        return redirect(url_for('login'))
    return decorated

# -------- Routes --------

@app.route('/')
def index():
    return render_template('index.html')

# Admin Login
@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (username, password))
        admin = cursor.fetchone()
        if admin:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = "Invalid admin credentials."
            return render_template('adminlogin.html', error=error)
    return render_template('adminlogin.html')

@app.route('/adminlogout')
def adminlogout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

# Voter Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        voterid = request.form['voterid']
        password = request.form['password']
        cursor.execute("SELECT * FROM voter WHERE voterid=%s AND password=%s", (voterid, password))
        voter = cursor.fetchone()
        if voter:
            if voter['voted'] == 1:
                error = "You have already voted."
                return render_template('login.html', error=error)
            session['voterid'] = voterid
            return redirect(url_for('dashboard'))
        else:
            error = "Invalid Voter ID or Password."
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('voterid', None)
    return redirect(url_for('index'))

# Voter dashboard to vote
@app.route('/dashboard', methods=['GET', 'POST'])
@voter_login_required
def dashboard():
    if request.method == 'POST':
        candidate_id = request.form.get('candidate.id')
        voterid = session['voterid']
        try:
            cursor.execute("UPDATE candidates SET votes = votes + 1 WHERE id=%s", (candidate_id,))
            cursor.execute("UPDATE voter SET voted = 1 WHERE voterid=%s", (voterid,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            return f"An error occurred: {str(e)}"
        session.pop('voterid', None)
        return redirect(url_for('result'))
    cursor.execute("SELECT * FROM candidates")
    candidates = cursor.fetchall()
    return render_template('dashboard.html', candidates=candidates)

# Admin dashboard: manage voters & candidates
@app.route('/admin_dashboard')
@admin_login_required
def admin_dashboard():
    # Fetch voters and candidates
    cursor.execute("SELECT * FROM voter")
    voters = cursor.fetchall()
    cursor.execute("SELECT * FROM candidates")
    candidates = cursor.fetchall()
    return render_template('admin_dashboard.html', voters=voters, candidates=candidates)

# Add voter
@app.route('/add_voter', methods=['POST'])
@admin_login_required
def add_voter():
    voterid = request.form['voterid']
    name = request.form['name']
    password = request.form['password']
    try:
        cursor.execute("INSERT INTO voter (voterid, name, password, voted) VALUES (%s, %s, %s, 0)", (voterid, name, password))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return f"Error: {str(e)}"
    return redirect(url_for('admin_dashboard'))

# Remove voter
@app.route('/remove_voter/<int:voterid>')
@admin_login_required
def remove_voter(voterid):
    try:
        cursor.execute("DELETE FROM voter WHERE voterid=%s", (voterid,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return f"Error: {str(e)}"
    return redirect(url_for('admin_dashboard'))

# Add candidate
@app.route('/add_candidate', methods=['POST'])
@admin_login_required
def add_candidate():
    cid = request.form['id']
    name = request.form['name']
    party = request.form['party']
    image = request.form['image']
    try:
        cursor.execute("INSERT INTO candidates (id, name, party, image, votes) VALUES (%s, %s, %s, %s, 0)", (cid, name, party, image))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return f"Error: {str(e)}"
    return redirect(url_for('admin_dashboard'))

# Remove candidate
@app.route('/remove_candidate/<int:id>')
@admin_login_required
def remove_candidate(id):
    try:
        cursor.execute("DELETE FROM candidates WHERE id=%s", (id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return f"Error: {str(e)}"
    return redirect(url_for('admin_dashboard'))

# Result page with chart data
@app.route('/result')
def result():
    cursor.execute("SELECT * FROM candidates ORDER BY votes DESC")
    candidates = cursor.fetchall()
    return render_template('result.html', candidates=candidates)

# API to serve data for charts
@app.route('/api/results')
@admin_login_required
def api_results():
    cursor.execute("SELECT name, votes FROM candidates ORDER BY votes DESC")
    data = cursor.fetchall()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
