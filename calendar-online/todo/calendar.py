import os
from flask import current_app, render_template
from flask import render_template, request, g, url_for, flash, abort, redirect, send_from_directory
from flask.blueprints import Blueprint
from datetime import datetime
from .db import get_db
from .auth import get_user_info
from .calendar_build import calendar


bp = Blueprint('calendar', __name__)

months=0


@bp.route('/', methods=['GET', 'POST'])
@get_user_info
def index():
    db = get_db()
    global months
    
    months=0
    month_days=calendar(months)
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    
    user = g.user if 'user' in g else None
    
    return render_template('index.html', month=month_days, today=today, user=user)


@bp.route('/calendar/next', methods=['POST'])
def next_month():
    if request.method == 'POST':
        global months
        months += 1
        month_days = calendar(months)

    user = g.user if 'user' in g else None

    return render_template('index.html', month=month_days, user=user)



@bp.route('/calendar/back', methods=['POST'])  
def back_month():
    if request.method == 'POST':
        global months
        months -= 1
        month_days = calendar(months)
    
    user = g.user if 'user' in g else None
    
    return render_template('index.html', month=month_days, user=user)


@bp.route('/<date>', methods=['GET','POST'])
@get_user_info
def day(date):
    db=get_db()
    
    if request.method == 'POST':
        if 'user' not in g:
            flash('Войдите, чтобы добавлять дела')
            return redirect(url_for('auth.login'))

        todo = request.form.get('todo')
        
        if todo:
            db.execute(
                'INSERT INTO calendar (name, date, is_done, user_id) VALUES (?, ?, ?, ?)',
                (todo, date, False, g.user['id'])
            )
            db.commit()
    
    user = g.user if 'user' in g else None
    
    todos = db.execute(
        'SELECT * FROM calendar WHERE date = ? AND user_id = ?',
        (date, user['id'])
        ).fetchall()
    db.commit()

    return render_template('day.html', todos=todos, date=date, user=user)


@bp.route('/todo/<int:id>')
@get_user_info
def todo(id):
    db = get_db()

    todo = db.execute(
        'SELECT * FROM calendar WHERE id = ?',
        (id,)
    ).fetchone()
    
    user = g.user if 'user' in g else None

    return render_template('todo.html' ,todo=todo, user=user)



@bp.route('/alltodos', methods=['GET', 'POST'])
@get_user_info
def all_todos():
    db = get_db()

    if request.method == 'POST':
        if 'user' not in g:
            flash('Войдите, чтобы добавлять дела')
            return redirect(url_for('auth.login'))

        todo = request.form.get('todo')
        date_str = request.form.get('date')

        date = datetime.fromisoformat(date_str).strftime('%d-%m-%y')
        
        if todo:
            db.execute(
                'INSERT INTO calendar (name, date, is_done, user_id) VALUES (?, ?, ?, ?)',
                (todo, date, False, g.user['id'])
            )
            db.commit() 
    
    user = g.user if 'user' in g else None
    
    todos = db.execute(
        'SELECT * FROM calendar WHERE user_id = ?',
        (user['id'],)
    ).fetchall()

    return render_template('all_todos.html', todos=todos, user=user)


@bp.route('/calendar/<int:id>/<date>/delete', methods=['POST'])
@get_user_info
def delete(id, date):
    user_id = g.user['id'] if 'user' in g else None

    db = get_db()
    db.execute(
        'DELETE FROM calendar WHERE id = ? AND user_id = ?',
        (id, user_id)
    )
    db.commit()

    return redirect(url_for('calendar.day', date=date))


@bp.route('/upload/<filename>')
def get_upload(filename):
    folder = os.path.abspath(current_app.config['UPLOAD_FOLDER'])
    return send_from_directory(folder, filename)
