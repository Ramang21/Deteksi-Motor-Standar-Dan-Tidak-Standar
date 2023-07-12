from flask import Flask, Response, render_template, request, session, redirect, url_for
import detection_camera 
# from flask_mysqldb import MySQL
# import MySQLdb.cursors
import mysql.connector

app = Flask(__name__)
app.static_folder = 'static'
app.secret_key = 'your secret key'

mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="demor"
)
cursor = mydb.cursor()

# Enter your database connection details below
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_DB'] = 'demor'

# mysql = MySQL(app)

@app.route('/')
# def home():
#     return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL

        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        user = cursor.fetchone()
        # If account exists in accounts table in out database
        if user:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = user[0]
            session['username'] = user[1]
            # Redirect to home page
            return redirect(url_for('Dashboard'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)

@app.route("/Dashboard")
def Dashboard():
    return render_template('Dashboard.html')

@app.route('/video_feed')
def video_feed():
    return Response(detection_camera.get_frame(),
    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/Data")
def Data():
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT * FROM registrasi_tidak_standard ORDER BY id desc")
    datatidakstandard = cursor.fetchall()
    return render_template('Data.html', datatidakstandard=datatidakstandard)

@app.route("/Capture", methods=['GET', 'POST'])
def Capture():
    return render_template('Capture.html')

@app.route("/Registrasi-Tidak-Standard", methods=['GET', 'POST'])
def RegistrasiTidakStandard():
    if request.method=='POST':
        nomor_identitas = request.form['nomor_identitas']
        nama = request.form['nama']
        nomor_plat = request.form['nomor_plat']
        status = request.form['status']
        tanggal = request.form['tanggal']
        keterangan = request.form['keterangan']
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("INSERT INTO registrasi_tidak_standard (nomor_identitas, nama, nomor_plat, status, tanggal, keterangan) VALUES (%s, %s, %s, %s, %s, %s)", (nomor_identitas, nama, nomor_plat, status, tanggal, keterangan))
        mydb.commit()
        cursor.close()
        return redirect(url_for('Data'))
    return render_template('Registrasiplat.html')

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.route('/Hapus-Data/<string:id>', methods = ['POST','GET'])
def HapusData(id):
    cursor = mydb.cursor(dictionary=True)
    cursor.execute('DELETE FROM registrasi_tidak_standard WHERE id = {0}'.format(id))
    mydb.commit()
    # flash('Data Berhasil Dihapus!')
    return redirect(url_for('Data'))

# @app.route('/hapusdata/<string:id>', methods = ['POST','GET'])
# def Data(id):
#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cursor.execute('DELETE FROM data WHERE id = {0}'.format(id))
#     mysql.connection.commit()
#     flash('Data Berhasil Dihapus!')
#     return redirect(url_for('Data'))