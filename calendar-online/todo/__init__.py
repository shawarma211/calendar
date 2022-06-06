from distutils.command.upload import upload
import os
from flask import Flask
from . import db


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='very_secret',
        DATABASE=os.path.join(app.instance_path, 'calendar.db'),
        UPLOAD_FOLDER='upload'
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'])
    except OSError:
        pass
    
    
    db.init_app(app)

    from . import calendar, auth
    app.register_blueprint(calendar.bp)
    app.register_blueprint(auth.bp)

    return app
    