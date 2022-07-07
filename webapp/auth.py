from flask import Blueprint, render_template, request, flash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html")

@auth.route('/logout')
def logout():
    return "<p>Logout</p>"

@auth.route('/signUp', methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':
        email = request.form.get('email')
        firstSecondName = request.form.get('firstSecondName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if len(email) < 4:
            flash('Email must be greater than 4 chars.', category='error')
        elif len(firstSecondName) < 2:
            flash('First and Second name must be greater than 1 chars.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        else:
            flash('Account created!', category='success')

    return render_template("signUp.html")