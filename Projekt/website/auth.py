from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Category
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        
    

        if user:
            if check_password_hash(user.password, password):
                flash('Vitaj, ' + user.first_name + ' 👋..Nezabudni uviesť transakcie za dnešný deň 💸 ', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Nespávne heslo.', category='error')
        else:
            flash('Email neexistuje.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Tento email sa už používa.', category='error')
        elif len(email) < 4:
            flash('Email musí mať viac ako 3 písmená.', category='error')
        elif len(first_name) < 2:
            flash('Meno musí mať viac ako 1 písmeno.', category='error')
        elif password1 != password2:
            flash('Heslá sa nezhodujú', category='error')
        elif len(password1) < 7:
            flash('Heslo musí mať aspoň 7 písmen.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            addHardcodedRow(new_user)
            #db.session.close()
            login_user(new_user, remember=True)
            flash('Účet bol úspešne vytvorený.', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)


def addHardcodedRow(new_user):
    name = "Potraviny" 
    type = "výdaj"
    icon = "fa-solid fa-cart-shopping"
    user_id = new_user.id
    entry = Category(type, name, icon, user_id)
    db.session.add(entry)
    db.session.commit()

    name = "Výplata" 
    type = "príjem"
    icon = "fa-solid fa-hand-holding-dollar"
    user_id = new_user.id
    entry = Category(type, name, icon, user_id)
    db.session.add(entry)
    db.session.commit()


