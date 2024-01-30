from flask import Flask,jsonify, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo
from flask_sqlalchemy import SQLAlchemy
from models import db, User, EndDevice
from forms import LoginForm,AjouterEndDeviceForm
from flask_wtf import CSRFProtect
import os
from config import Config
import json
from pysnmp.hlapi import *
from snmp import get_snmp_data
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
csrf = CSRFProtect(app)

app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'connexion'
community_string = "SNS"
oids_to_query = ["1.3.6.1.2.1.25.2.2.0", "1.3.6.1.2.1.25.2.3.1.6.1", "1.3.6.1.2.1.25.2.3.1.6.2",
                     "1.3.6.1.2.1.25.3.3.1.2.6", "1.3.6.1.2.1.25.3.3.1.2.7", "1.3.6.1.2.1.25.3.3.1.2.8",
                     "1.3.6.1.2.1.25.3.3.1.2.9", "1.3.6.1.2.1.25.3.3.1.2.10", "1.3.6.1.2.1.25.3.3.1.2.11",
                     "1.3.6.1.2.1.25.3.3.1.2.12", "1.3.6.1.2.1.25.3.3.1.2.13"]



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/index')
def index():
    # Your view logic here
    return render_template('index.html', title='Accueil')


@app.route('/connexion', methods=['GET', 'POST'])
def connexion():
    form = LoginForm()  # Use the new LoginForm

    if form.validate_on_submit():
        print('Form submitted successfully')
        user = User.query.filter_by(username=form.username.data, password=form.password.data).first()

        if user:
            login_user(user)
            flash('Vous êtes maintenant connecté.', 'success')
            return redirect(url_for('choix_redirection'))
        else:
            flash('La connexion a échoué. Veuillez vérifier votre nom d\'utilisateur et votre mot de passe.', 'danger')

    return render_template('connexion.html', title='Connexion', form=form)
@app.route('/choix_redirection')
@login_required
def choix_redirection():
    if current_user.is_authenticated:
        return render_template('choix_redirection.html')
    else:
        flash('Veuillez vous connecter pour accéder à cette page.', 'warning')
        return redirect(url_for('connexion'))

# Mise à jour de la route dans votre fichier principal
@app.route('/ajouter_end_device', methods=['GET', 'POST'])
@login_required
def ajouter_end_device():
    form = AjouterEndDeviceForm()

    if form.validate_on_submit():
        new_end_device = EndDevice(
            ip_address=form.ip_address.data,
            mac_address=form.mac_address.data,
            longitude=form.longitude.data,
            latitude=form.latitude.data,
            snmp_enabled=form.snmp_enabled.data,
            user=current_user
        )

        db.session.add(new_end_device)
        db.session.commit()

        flash('Nouvel appareil ajouté avec succès.', 'success')
        return redirect(url_for('index'))

    return render_template('ajouter_end_device.html', title='Ajouter un appareil', form=form)

# Ajoutez cette route dans votre fichier principal

@app.route('/carte_end_devices')
@login_required
def carte_end_devices():

    end_devices = EndDevice.query.all()
    end_devices_data = []

    for device in end_devices:
             
        end_devices_data.append({
            "id": device.id,
            "latitude": device.latitude,
            "longitude": device.longitude,
            "ip_address": device.ip_address,
            "mac_address": device.mac_address,
        })

    end_devices_json = json.dumps(end_devices_data, default=str)
    return render_template('carte_end_devices.html', title='Carte des End Devices', end_devices_json=end_devices_json)


# ...

# Add this route to your Flask application
@app.route('/get_snmp_data/<int:end_device_id>')
@login_required
def get_snmp_data_for_device(end_device_id):
    end_device = EndDevice.query.get_or_404(end_device_id)
    snmp_data = get_snmp_data(end_device.ip_address, 'SNS', oids_to_query)  # Correction here
    return jsonify(snmp_data)
 
# ...

 
'''
# Ajoutez cette route dans votre fichier principal
@app.route('/details_end_device/<int:end_device_id>')
@login_required
def details_end_device(end_device_id):
    end_device = EndDevice.query.get_or_404(end_device_id)
    return render_template('details_end_device.html', title='Détails de l\'End Device', end_device=end_device)
'''
if __name__ == '__main__':
    app.run(debug=False)