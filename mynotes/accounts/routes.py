from flask import Blueprint
from flask import render_template, redirect,flash, url_for, request
from mynotes import app, bcrypt, db, mail
from mynotes.accounts.forms import LoginForm, RegistrationForm, RequestResetForm, ResetPasswordForm
from mynotes.models import load_user, User
from flask_login import login_user, logout_user, current_user
from flask_mail import Message

accounts = Blueprint('accounts',__name__)

@accounts.route('/login',methods = ['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            if user.activated:
                login_user(user,form.remember.data)
                flash(f'Welcome {user.username}','success')
                return redirect(url_for('rticles.articles'))
            else:
                token = user.get_reset_token()
                msg = Message('Account activation',sender=app.config['MAIL_USERNAME'] ,recipients=[user.email])
                msg.body = f'''To confirm email, visit the following link:{url_for('accounts.activate',token=token,_external=True)}
                If you did not make this request then simply ignore this email'''
                mail.send(msg)
                flash(f'Your account exists but is not activated. Activation link was sent to your email','warning')
                return render_template('login.html',form = form)
        else:
            flash(f'Wrong email or password','danger')
            return render_template('login.html',form = form)
    return render_template('login.html', form = form)

@accounts.route('/logout')
def logout():
    logout_user()
    flash(f'You have successfully loged out','success')
    return redirect(url_for('accounts.login'))

@accounts.route('/register', methods = ['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,email=form.email.data,password=bcrypt.generate_password_hash(form.password.data).decode('utf-8'))
        db.session.add(user)
        db.session.commit()
        
        token = user.get_reset_token()
        msg = Message('Account activation',sender=app.config['MAIL_USERNAME'] ,recipients=[user.email])
        msg.body = f'''To confirm email, visit the following link:{url_for('accounts.activate',token=token,_external=True)}
        If you did not make this request then simply ignore this email'''
        mail.send(msg)

        flash(f'Your account was created! Activate your account before logging in. Activation link was sent to your email','success')
        return redirect(url_for('accounts.login'))
    return render_template('register.html', form = form)


@accounts.route('/activate/<token>',methods=['GET'])
def activate(token):
    if current_user.is_authenticated:
        flash('You are allready authenticated','warning')
        return redirect(url_for('accounts.login'))
    else:
        user = User.verify_reset_token(token)
        if not user:
            flash('Wrong activation token','danger')
            return redirect(url_for('accounts.login'))
        else:
            user.activated = True
            db.session.commit()
            flash('Account was activated. You can log in now','success')
            return redirect(url_for('accounts.login'))

@accounts.route('/req_reset',methods=['GET','POST'])
def req_reset():
    if current_user.is_authenticated and current_user.activated:
        flash('You are allready logged in','warning')
        return redirect(url_for('rticles.articles'))
    else:
        form = RequestResetForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email = form.email.data).first()
            send_reset_email(user)
            flash('Reset token has been sent to your email','info')
            return redirect(url_for('accounts.login'))
        return render_template('req_reset.html',form=form)

@accounts.route('/reset_password/<token>',methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated and current_user.activated:
        return redirect(url_for('rticles.articles'))
    else:
        user = User.verify_reset_token(token)
        if not user:
            flash('Token token is not valid','danger')
            return redirect(url_for('accounts.req_reset'))
        form = ResetPasswordForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user.password = hashed_password
            db.session.commit()
            flash(f'Your password was updated','success')
            return redirect(url_for('accounts.login'))
        return render_template('reset_password.html',form = form,token=token)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',sender=app.config['MAIL_USERNAME'] ,recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
    {url_for('accounts.reset_password',token=token,_external=True)}
    If you did not make this request then simply ignore this email'''
    mail.send(msg)
