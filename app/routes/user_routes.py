from flask import Blueprint, render_template, request, redirect, url_for
from app import kanvas_db
from app.models import User
from flask_login import login_user, logout_user, login_required

user_bp = Blueprint('user', __name__, url_prefix='/users')

@user_bp.route('/')
def index():
    users = User.query.all()
    return render_template('users/index.html', users=users)

@user_bp.route('/<int:id>')
def show(id):
    user = User.query.get_or_404(id)
    return render_template('users/show.html', user=user)

@user_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        new_user = User(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            email=request.form['email'],
            university_entry_year=request.form['university_entry_year']
        )
        kanvas_db.session.add(new_user)
        kanvas_db.session.commit()
        return redirect(url_for('user.index'))
    return render_template('users/create.html')

@user_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.email = request.form['email']
        user.university_entry_year = request.form['university_entry_year']
        kanvas_db.session.commit()
        return redirect(url_for('user.index'))
    return render_template('users/edit.html', user=user)

@user_bp.route('/delete/<int:id>')
def delete(id):
    user = User.query.get_or_404(id)
    kanvas_db.session.delete(user)
    kanvas_db.session.commit()
    return redirect(url_for('user.index'))
