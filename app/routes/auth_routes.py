from flask import Blueprint, render_template, request, redirect, url_for
from app import kanvas_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print(request.form['username'])
        print(request.form['password'])
        return render_template('auth/login.html')

    return render_template('auth/login.html')