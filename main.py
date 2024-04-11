from flask import Flask, render_template, redirect, request, url_for
from flask_login import LoginManager, current_user, login_user, logout_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from config import config_dict

from util import hash_pass, verify_pass, validate_password
from forms import LoginForm, RegisterForm , CreateTeamForm, JoinTeamForm, SaveScriptForm

import random



app = Flask(__name__)
app.config.from_object(config_dict)


db = SQLAlchemy()
login_manager = LoginManager()

db.init_app(app)
login_manager.init_app(app)

# Users database class....
class Users(db.Model, UserMixin):

    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    name      = db.Column(db.String(64))
    ldap      = db.Column(db.String(64), unique=True)
    email         = db.Column(db.String(256), unique=True)
    password      = db.Column(db.LargeBinary)
    team_joined = db.Column(db.String(64))

    def __init__(self, **kwargs):
        for property, value in kwargs.items():

            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # Value is iterable and and is not a string..
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)
        setattr(self, "team_joined", 0)

    def __repr__(self):
        return str(self.ldap) 
    

# Teams database class....
class Teams(db.Model, UserMixin):

    __tablename__ = 'teams'

    teamid           = db.Column(db.Integer, primary_key=True)
    teamname      = db.Column(db.String(255))
    members          = db.Column(db.Integer, primary_key=True)
    member1      = db.Column(db.String(255), unique=True)
    member2      = db.Column(db.String(255), unique=True)
    member3      = db.Column(db.String(255), unique=True)
    member4      = db.Column(db.String(255), unique=True)
    script         = db.Column(db.Text, unique=True)

    def __repr__(self):
        return str(self.teamid) 



@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    ldap = request.form.get('ldap')
    user = Users.query.filter_by(ldap = ldap).first()
    return user if user else None


@app.route('/')
def index():
    if not current_user.is_authenticated:
        return render_template('home/home.html')
    
    if not current_user.team_joined:
        return render_template('home/index.html', team_name = None, script = None)
    else:
        # Return team name and team script also for joined team..
        teamid = current_user.team_joined

        # Search for the  teamid..
        team = Teams.query.filter_by(teamid = teamid).first()
        script = team.script

        if script == "":
            script = "# Start writing your code here..."
        return render_template('home/index.html', team_name = team.teamname, script = script)


# Login & Registration...

@app.route('/login', methods=['GET', 'POST'])
def login():

    login_form = LoginForm(request.form)
    if 'login' in request.form:

        # read form data
        ldap = request.form['ldap']
        password = request.form['password']

        # Locate user
        user = Users.query.filter_by(ldap = ldap).first()

        # Check the password..
        if user and verify_pass(password, user.password):

            login_user(user)
            return redirect(url_for('index'))

        # Something (ldap or pass) is not ok..
        return render_template('accounts/login.html',
                               msg='Wrong ldap or password',
                               form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():

    create_account_form = RegisterForm(request.form)
    if 'register' in request.form:

        ldap = request.form['ldap']
        email = request.form['email']
        password = request.form['password']

        # Check usename exists...
        user = Users.query.filter_by(ldap = ldap).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Ldap already registered',
                                   success=False,
                                   form=create_account_form)

        # Check email exists..
        user = Users.query.filter_by(email=email).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Email already registered',
                                   success=False,
                                   form=create_account_form)
        
        # Validate_password..
        validation, val_msg = validate_password(password)
        if not validation:
            return render_template('accounts/register.html',
                        msg=val_msg,
                        success=False,
                        form=create_account_form)

        # else we can create the user
        user = Users(**request.form)
        db.session.add(user)
        db.session.commit()

        # Delete user from session
        logout_user()
        
        return render_template('accounts/register.html',
                               msg='Account created successfully.',
                               success=True,
                               form=create_account_form)

    else:
        return render_template('accounts/register.html', form=create_account_form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))




# Team management ...


@app.route('/createteam', methods=['GET', 'POST'])
def create_team():

    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    # Check if the user has joined any team or not..
    if current_user.team_joined:
        return redirect(url_for('index' , msg = "Error", success = False))
    
    
    create_team_form = CreateTeamForm(request.form)
    if 'createteam' in request.form:

        # read form data
        teamname = request.form['teamname']

        # Search a unique teamid..
        found = False
        while not found:
            randomid = random.randint(100000,999999)
            team = Teams.query.filter_by(teamid = randomid).first()
            if not team:
                found = True
            
        # Hence, cerate team..
        team = {"teamname" : teamname,
                "teamid": randomid,
                "members" : 1,
                "member1": current_user.ldap,
                "member2": "",
                "member3": "",
                "member4": "",
                "script" : ""
                }

        team = Teams(**team)
        db.session.add(team)
        db.session.commit()

        current_user.team_joined = randomid
        db.session.commit()


        # Redircet to home page...
        return redirect(url_for('index', msg = "Team Created Succesfully", success = True))


    return render_template('teams/createteams.html', form=create_team_form)
    




@app.route('/jointeam', methods=['GET', 'POST'])
def join_team():

    
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    # Check if the user has joined any team or not..
    if current_user.team_joined:
        return redirect(url_for('index' , msg = "Error", success = False))
    
    join_team_form = JoinTeamForm(request.form)
    if 'jointeam' in request.form:

        # read form data
        teamid = request.form['teamid']

        # Search for the  teamid..
        team = Teams.query.filter_by(teamid = teamid).first()
        if not team:
            return render_template('teams/jointeams.html',
                               msg='Team Not Found!',
                               form=join_team_form)
        # Search for Max_participants..
        if team.members == 4:
            return render_template('teams/jointeams.html',
                               msg='Team Already Full!',
                               form=join_team_form)
    
        team.members += 1
        if team.members == 2: team.member2 = current_user.ldap
        elif team.members == 3: team.member3 = current_user.ldap
        elif team.members == 4: team.member4 = current_user.ldap

        current_user.team_joined = teamid
        db.session.commit()

        # Redircet to home page...
        return redirect(url_for('index', msg = "Team Joined Succesfully", success = True))


    return render_template('teams/jointeams.html', form=join_team_form)
    
# Save the team script..
@app.route('/savescript', methods=['GET', 'POST'])
def save_script():

    
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    # Check if the user has joined any team or not..
    if not current_user.team_joined:
        return redirect(url_for('index' , msg = "Error", success = False))
    
    save_script_form = SaveScriptForm(request.form)
    if "savescript" in request.form:

        # Read Script..
        script = request.form['script']
        teamid = current_user.team_joined

        # Search for the  teamid..
        team = Teams.query.filter_by(teamid = teamid).first()
        if not team:
            return render_template('teams/jointeams.html',
                               msg='Team Not Found!',
                               form=index)
        
        team.script = script       
        db.session.commit()

        return redirect(url_for('index'))

    return redirect(url_for('index'))
    


if __name__ == "__main__":
    app.run()