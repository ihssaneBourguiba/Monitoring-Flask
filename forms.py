
from flask_wtf import FlaskForm
from wtforms import StringField , FloatField , PasswordField, SubmitField, BooleanField
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
