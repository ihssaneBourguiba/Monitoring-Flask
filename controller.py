from flask import Flask,jsonify, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from models import db, User, EndDevice,IotDevices
from forms import LoginForm, AjouterEndDeviceForm, AjouterIoTForm,PredictionForm
from flask_wtf import CSRFProtect
import os
from config import Config
import json
from pysnmp.hlapi import *
from snmp import get_snmp_data
import paho.mqtt.client as mqtt
import random
import time
import threading
import matplotlib.pyplot as plt
import numpy as np
import datetime
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from datetime import timedelta
from matplotlib.dates import DayLocator, DateFormatter
import requests
from prediction import predict_temperature_for_iot
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
iot_device_data = {}


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

    end_devices_data = [{
        "id": device.id,
        "latitude": device.latitude,
        "longitude": device.longitude,
        "ip_address": device.ip_address,
        "mac_address": device.mac_address,
    } for device in end_devices]

    end_devices_json = json.dumps(end_devices_data, default=str)

    return render_template('carte_end_devices.html', title='Carte des Devices', end_devices_json=end_devices_json)


# ...

# Add this route to your Flask application
@app.route('/get_snmp_data/<int:end_device_id>')
@login_required
def get_snmp_data_for_device(end_device_id):
    end_device = EndDevice.query.get_or_404(end_device_id)
    snmp_data = get_snmp_data(end_device.ip_address, 'SNS', oids_to_query)  # Correction here
    return jsonify(snmp_data)
 
# ...


# Configuration MQTT du listener
mqtt_broker_host = "localhost"
mqtt_broker_port = 1883
mqtt_topic = "iot_device_data"

# Fonction de rappel lors de la réception d'un message MQTT
# Update the on_message function
def on_message(client, userdata, msg):
    iot_device_data = json.loads(msg.payload)
    print(f"Received IoT Device Data via MQTT: {iot_device_data}")

    mac = iot_device_data.get("mac")
    temp = iot_device_data.get("temp")
    datetime_str = iot_device_data.get("datetime")
    latitude = iot_device_data.get("latitude")
    longitude = iot_device_data.get("longitude")

    with app.app_context():
        # Ajoutez un nouvel enregistrement avec toutes les données de l'IoT
        new_iot_device = IotDevices(
            mac=mac,
            temp=temp,
            datetime=datetime_str,
            latitude=latitude,
            longitude=longitude
        )
        db.session.add(new_iot_device)
        db.session.commit()



# Rest of your code...

# Initialisation du client MQTT
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message

# Connexion au broker MQTT
mqtt_client.connect(mqtt_broker_host, mqtt_broker_port, 60)
mqtt_client.subscribe(mqtt_topic)

# Fonction pour créer des données IoT simulées et les publier sur MQTT
def publish_simulated_iot_device():
    while True:
        with app.app_context():
            existing_iots = IotDevices.query.all()

        for iot_device in existing_iots:
            temp = random.uniform(20.0, 30.0)
            datetime_str = time.strftime("%Y-%m-%d %H:%M:%S")

            # Publie toutes les données de l'IoT via MQTT
            mqtt_client.publish(mqtt_topic, json.dumps({
                "mac": iot_device.mac,
                "temp": temp,
                "datetime": datetime_str,
                "latitude": iot_device.latitude,
                "longitude": iot_device.longitude
            }))
            
            time.sleep(1)  # Ajoutez un délai après chaque publication si nécessaire

        time.sleep(260)  # Ajoutez un délai entre chaque itération de la boucle externe




# Boucle pour publier des données IoT simulées toutes les 10 secondes
def mqtt_publisher():
    while True:
        publish_simulated_iot_device()

# Ajoutez une boucle pour traiter les messages MQTT en arrière-plan
# Modify mqtt_listener to include rendering mqtt_data.html
# Modify mqtt_listener to handle rendering after processing MQTT message
def mqtt_listener():
    while True:
        mqtt_client.loop_forever()

        # After processing MQTT message, render mqtt_data.html
        iot_devices = IotDevices.query.all()
        iot_devices_data = [{
            "id": device.id,
            "mac": device.mac,
            "temp": device.temp,
            "datetime": device.datetime,
            "latitude": device.latitude,
            "longitude": device.longitude,
        } for device in iot_devices]

        iot_devices_json = json.dumps(iot_devices_data, default=str)

        # Use Flask's app_context to render the template
        with app.app_context():
            render_template('mqtt_data.html', title='IoT Device Data', iot_devices_json=iot_devices_json)
            
            # Add this block for database interaction within the app context
            for device in iot_devices:
                iot_device = IotDevices(
                    mac=device.mac,
                    temp=device.temp,
                    datetime=device.datetime,
                    latitude=device.latitude,
                    longitude=device.longitude
                )

                db.session.add(iot_device)
                db.session.commit()

# ...

@app.route('/mqtt_data')
@login_required
def mqtt_data():
    iot_devices = IotDevices.query.all()

    iot_devices_data = [{
        "id": device.id,
        "mac": device.mac,
        "temp": device.temp,
        "datetime": device.datetime,
        "latitude": device.latitude,
        "longitude": device.longitude,
    } for device in iot_devices]

    iot_devices_json = json.dumps(iot_devices_data, default=str)

    mac_list = [device["mac"] for device in iot_devices_data]
    time_list = [device["datetime"] for device in iot_devices_data]
    temp_list = [device["temp"] if device["temp"] is not None else 0 for device in iot_devices_data]

    # Convert time strings to datetime objects for proper sorting
    time_list = [datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S") if time_str is not None else None for time_str in time_list]

    # Filter out None values
    valid_data = [(mac, time, temp) for mac, time, temp in zip(mac_list, time_list, temp_list) if time is not None]

    # Sort data based on datetime
    sorted_data = sorted(valid_data, key=lambda x: x[1])

    mac_list, time_list, temp_list = zip(*sorted_data)

    # Create Matplotlib chart
    generate_temperature_chart(mac_list, time_list, temp_list)

    return render_template('mqtt_data.html', title='IoT Device Data', iot_devices_json=iot_devices_json, chart_filename='static/temperature_chart.png')

# ...



def generate_temperature_chart(mac_list, time_list, temp_list):
    plt.figure(figsize=(10, 6))

    # Plot temperature curves for each device
    for i, mac in enumerate(set(mac_list)):
        device_temps = [temp_list[j] for j in range(len(mac_list)) if mac_list[j] == mac]
        device_times = [time_list[j] for j in range(len(mac_list)) if mac_list[j] == mac]
        
        plt.plot(device_times, device_temps, label=f'Device {mac}')

    plt.xlabel('Time')
    plt.ylabel('Temperature (°C)')
    plt.title('Temperature Changes for IoT Devices Over Time')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the chart to a file or use BytesIO to display it directly in the HTML template
    chart_filename = 'static/temperature_chart.png'
    plt.savefig(chart_filename)
    plt.close()

import os

# ... (your existing imports)



@app.route('/ajouter_iot', methods=['GET', 'POST'])
@login_required
def ajouter_iot():
    form = AjouterIoTForm()

    if form.validate_on_submit():
        mac = form.mac.data
        latitude = form.latitude.data
        longitude = form.longitude.data

        iot_device = IotDevices(
            mac=mac,
            latitude=latitude,
            longitude=longitude
        )

        db.session.add(iot_device)
        db.session.commit()

        flash('Nouvel IoT ajouté avec succès.', 'success')
        return redirect(url_for('index'))

    return render_template('ajouter_iot.html', title='Ajouter un IoT', form=form)

# ...

@app.route('/prediction/<int:iot_device_id>', methods=['GET', 'POST'])
@login_required
def show_prediction(iot_device_id):
    # Récupérer les détails de l'appareil IoT à partir de la base de données
    iot_device = IotDevices.query.get_or_404(iot_device_id)

    # Initialiser les variables de dates
    start_date = None
    end_date = None

    # Instantiate the PredictionForm
    prediction_form = PredictionForm()

    # Vérifier si le formulaire est soumis
    if prediction_form.validate_on_submit():
        start_date = prediction_form.start_date.data
        end_date = prediction_form.end_date.data

        # Effectuer des prédictions de température en utilisant l'API Open Meteo
        chart_filename = predict_temperature_for_iot(iot_device.latitude, iot_device.longitude, start_date, end_date)


        # Sauvegarder l'objet iot_device dans la base de données avec le nouveau chart_filename
        db.session.commit()

    # Afficher les prédictions sur la page prediction.html
    return render_template('prediction.html', title='Prédictions de Température', 
                           latitude=iot_device.latitude, longitude=iot_device.longitude,
                           prediction_form=prediction_form, chart_filename='static/temperature_chart.png')

# ...


if __name__ == '__main__':
    def run_app():
        app.run(debug=False)

    flask_thread = threading.Thread(target=run_app)
    flask_thread.start()

    # Lancement du listener MQTT en arrière-plan
    mqtt_thread = threading.Thread(target=mqtt_listener)
    mqtt_thread.start()

    # Lancement du publisher MQTT en arrière-plan
    mqtt_publisher_thread = threading.Thread(target=mqtt_publisher)
    mqtt_publisher_thread.start()

    