from flask_security import Security, SQLAlchemyUserDatastore, SQLAlchemySessionUserDatastore
from application.model import *

user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
security = Security()

def init_security(app):
    security.init_app(app, user_datastore)
