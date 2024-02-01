
from flask_wtf import FlaskForm
from wtforms import StringField , FloatField , PasswordField, SubmitField, BooleanField,DateField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from models import User, EndDevice

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


'''
class AjouterEndDeviceForm(FlaskForm):
    ip_address = StringField('Adresse IP', validators=[DataRequired()])
    mac_address = StringField('Adresse MAC', validators=[DataRequired()])
    longitude = FloatField('Longitude')
    latitude = FloatField('Latitude')
    snmp_enabled = BooleanField('SNMP activé')
    submit = SubmitField('Ajouter')


'''
class AjouterEndDeviceForm(FlaskForm):
    ip_address = StringField('IP Address', validators=[DataRequired()])
    mac_address = StringField('MAC Address', validators=[DataRequired()])
    longitude = StringField('Longitude')
    latitude = StringField('Latitude')
    snmp_enabled = BooleanField('SNMP Enabled')
    submit = SubmitField('Ajouter un appareil')

class AjouterIoTForm(FlaskForm):
    mac = StringField('Adresse MAC', validators=[DataRequired()])
    latitude = FloatField('Latitude', validators=[DataRequired()])
    longitude = FloatField('Longitude', validators=[DataRequired()])
    submit = SubmitField('Ajouter')

class PredictionForm(FlaskForm):
    start_date = DateField('Start Date', validators=[DataRequired()], format='%Y-%m-%d')
    end_date = DateField('End Date', validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField('Visualiser les prédictions')