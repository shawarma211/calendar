import functools
import re
import sqlite3
import os
from flask import (session,\
        request, flash, redirect, \
        render_template, g, url_for, abort, current_app
        )
from flask.blueprints import Blueprint
from .db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

def get_user_info(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')

        if user_id is not None:
            db = get_db()
            g.user = db.execute(
                'SELECT * FROM user WHERE id = ?',
                (user_id,)
            ).fetchone()

        return func(*args, **kwargs)
    
    return wrapper


@bp.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password_confirm = request.form.get('password-confirm')

        error = None

        if not username or not password or not password_confirm:
            error = 'Пожалуйста, заполните все поля'
        elif password != password_confirm:
            error = 'Пароли не совпадают'

        if error is None:
            db = get_db()

            try:
                db.execute(
                    'INSERT INTO user (username, password) VALUES (?, ?)',
                    (username, password)
                )
                db.commit()
            except sqlite3.IntegrityError:
                error = 'Имя пользователя уже занято'
            else:
                return redirect(url_for('calendar.index'))
        
        flash(error)
        return redirect(url_for('auth.registration'))

    return render_template('registration.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        error = None

        db = get_db()
        user = db.execute(
            'SELECT password, id FROM user WHERE username = ?',
            (username,)
        ).fetchone()

        if user is None or user['password'] != password:
            error = 'Неправильное имя пользователя или пароль'

        if error is None:
            session['user_id'] = user['id']
            return redirect(url_for('calendar.index'))
        else:
            flash(error)
            return redirect(url_for('auth.login'))

    return render_template('login.html')


@bp.route('/profile', methods=['GET', 'POST'])
@get_user_info
def profile():
    if 'user' not in g or g.user is None:
        abort(403)
    
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')

        avatar = request.files.get('avatar')
        avatar_filename=None
        if avatar and avatar.filename != '':
            avatar_filename =  f'{g.user["username"]}.jpg'
            avatar.save(os.path.join(current_app.config['UPLOAD_FOLDER'], avatar_filename))

        db = get_db()
        db.execute(
            'UPDATE user SET first_name = ?, last_name = ?, avatar = ? WHERE id = ?',
            (first_name, last_name, avatar_filename, g.user['id'])
        )
        db.commit()
    
    return render_template('profile.html', user=g.user)


@bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('calendar.index'))
