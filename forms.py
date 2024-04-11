from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Email, DataRequired

# login and registration

# Create class respectively for the forms - login and registration..

class LoginForm(FlaskForm):
    ldap = StringField('ldap',
                         id='ldap_login',
                         validators=[DataRequired()])
    password = PasswordField('Password',
                             id='pwd_login',
                             validators=[DataRequired()])



class RegisterForm(FlaskForm):
    name = StringField('Name',
                         id='Name_create',
                         validators=[DataRequired()])
    
    ldap = StringField('ldap',
                         id='ldap_create',
                         validators=[DataRequired()])
    
    email = StringField('Email',
                      id='email_create',
                      validators=[DataRequired(), Email()])
    
    password = PasswordField('Password',
                             id='pwd_create',
                             validators=[DataRequired()])



class CreateTeamForm(FlaskForm):
    teamname = StringField('teamname',
                             id='teamname',
                             validators=[DataRequired()])

class JoinTeamForm(FlaskForm):
    teamid = StringField('teamid',
                             id='teamid',
                             validators=[DataRequired()])
    
class SaveScriptForm(FlaskForm):
    script = StringField('scipt',
                             id='script',
                             validators=[DataRequired()])
    
