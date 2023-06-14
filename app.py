from flask import Flask, render_template, request, redirect, session, url_for
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin
from flask_mysqldb import MySQL
import pandas as pd
import pickle
import locale

app = Flask(__name__)
model = pickle.load(open("UsedCarr_model.pkl", 'rb'))
car = pd.read_excel("UsedCar Clean.xlsx")

name_mapping = {
    "honda jazz": 0,"honda cr-v": 1,"toyota yaris": 2,"nissan serena": 3,"toyota agya": 4,"honda mobilio": 5, "daihatsu ayla": 6,"toyota rush": 7, "daihatsu xenia": 8,"toyota avanza": 9,"mitsubishi xpander": 10,
    "toyota fortuner": 11,"daihatsu terios": 12,"volkswagen scirocco": 13,"toyota kijang innova": 14,"honda city": 15,"wuling almaz": 16,"wuling confero": 17,"suzuki ignis": 18,"hyundai creta": 19,"mitsubishi pajero": 20,"dfsk supercab": 21,"dfsk glory 580": 22,"dfsk glory 560": 23,"dfsk": 24,"suzuki apv": 25,
    "nissan livina": 26,"mitsubishi outlander": 27
}

fuel_type_mapping = {
    "Bensin": 0, "Diesel": 1,
}

km_driven_mapping = {
    "110.000-115.000": 0,"65.000-70.000": 1,"85.000-90.000": 2,"120.000-125.000": 3,"40.000-45.000": 4,"75.000-80.000": 5,"70.000-75.000": 6,
    "100.000-105.000": 7,"50.000-55.000": 8,"35.000-40.000": 9,"115.000-120.000": 10,"60.000-65.000": 11,"30.000-35.000": 12,
    "95.000-100.000": 13,"55.000-60.000": 14,"20.000-25.000": 15,"45.000-50.000": 16,"90.000-95.000": 17,"25.000-30.000": 18,"105.000-110.000": 19,
    "80.000-85.000": 20,"165.000-170.000": 21,"130.000-135.000": 22,"170.000-175.000": 23,"150.000-155.000": 24,"135.000-140.000": 25,
    "10.000-15.000": 26,
    "15.000-20.000": 27,
    "175.000-180.000": 28,
    "215.000-220.000": 29,
    "145.000-150.000": 30,
    "5.000-10.000": 31,
    "140.000-145.000": 32,
    "155.000-160.000": 33,
    "270.000-275.000": 34,
    "125.000-130.000": 35,
    "240.000-245.000": 36,
    "0-5.000": 37,
    "180.000-185.000": 38,
    "195.000-200.000": 39,
    "190.000-195.000": 40,
    "160.000-165.000": 41,
    "200.000-205.000": 42,
    "220.000-225.000": 43,
    "230.000-235.000": 44
}

transmission_mapping = {
    "Manual": 0,
    "Automatic": 1,
    "Automatic Triptonic": 2,
    # Tambahkan mapping nilai numerik ke non-numeric sesuai kebutuhan Anda
}

locale.setlocale(locale.LC_ALL, '')

def format_price(price):
    return locale.format_string("%d", price, grouping=True)

# Konfigurasi database MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'prediction_car'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Konfigurasi kunci rahasia untuk sesi
app.secret_key = 'kunci_rahasia'


# Inisialisasi objek MySQL
mysql = MySQL(app)

# Inisialisasi LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

# Model Pengguna
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Mengecek apakah pengguna ada dalam database
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()
        
        if user:
            # Membuat objek User dan login pengguna
            user_obj = User(user['id'])
            login_user(user_obj)
            
            # Menyimpan username dalam sesi
            session['username'] = user['username']
            
            return redirect('/profile')
        else:
            error = 'Username atau password salah'
            return render_template('login.html', error=error)
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Menghapus data sesi pengguna saat logout
    session.clear()
    return redirect('/login')

    
@app.route('/profile')
def profile():
    # Mengambil username dari sesi
    username = session['username'] if 'username' in session else None
    
    if username:
        # Mengambil data pengguna dari database berdasarkan username
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        
        if user:
            first_name = user['first_name']
            last_name = user['last_name']
            email = user['email']
            
            return render_template('profile.html', username=username, first_name=first_name, last_name=last_name, email=email)
    
    return redirect('/login')

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/products')
def products():
    # Logika untuk mengambil data produk
    return render_template('products.html')

@app.route('/prediction')
def prediction():
    # Logika untuk layanan
    car['name'] = car['name'].map(name_mapping)
    car['fuel_type'] = car['fuel_type'].map(fuel_type_mapping)
    car['km_driven'] = car['km_driven'].map(km_driven_mapping)
    car['transmission'] = car['transmission'].map(transmission_mapping)

    name_options = list(name_mapping.keys())
    fuel_type_options = list(fuel_type_mapping.keys())
    km_driven_options = list(km_driven_mapping.keys())
    transmission_options = list(transmission_mapping.keys())

    year = sorted(car['year'].unique(), reverse=True)

    return render_template("prediction.html", name=name_options, years=year, fuel_type=fuel_type_options, km_driven=km_driven_options, transmission=transmission_options)

@app.route('/predict', methods=['POST'])
def predict():
    name = request.form.get('name')
    year = int(request.form.get('year'))
    fuel_type = request.form.get('fuel_type')
    km_driven = request.form.get('km_driven')
    transmission = request.form.get('transmission')

    # Mengonversi name menjadi nilai numerik
    name = name_mapping[name]

    # Mengonversi fuel_type menjadi nilai numerik
    fuel_type = fuel_type_mapping[fuel_type]

    # Mengonversi km_driven menjadi nilai numerik
    km_driven = km_driven_mapping[km_driven]

    transmission = transmission_mapping[transmission]

    prediction = model.predict(pd.DataFrame([[name, year, fuel_type, km_driven, transmission]], columns=['name', 'year', 'fuel_type', 'km_driven', 'transmission']))

    formatted_prediction = format_price(prediction[0])

    return formatted_prediction

@app.route('/contact')
def contact():
    # Logika untuk layanan
    return render_template('contact.html')

@app.route('/wishlists')
def wishlists():
    #wishlists
    return render_template('wishlists.html')


if __name__ == '__main__':
    app.run(debug=True)
