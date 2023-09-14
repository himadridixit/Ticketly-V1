from flask import Flask, send_file
from flask_msearch import Search
from application.api import *
from application.security import *
from application.model import *
from application.config import *

def create_app():
    app = Flask (__name__, template_folder="templates", static_folder = "static")
    app.config.from_object(LocalDevelopmentConfig)
    init_db(app)
    Search().init_app(app)
    init_security(app)
    add_resources()
    init_api(app)
    app.app_context().push()
    return app

app = create_app()

@app.route('/favicon.ico')
def favicon():
    return send_file('favicon.ico')

@app.errorhandler(404)
def pagenotfound():
    return "Page not found. Please return to the homepage."

@app.errorhandler(403)
def not_allowed():
    return "You are not allowed to access this page. Please return to the homepage."

from application.controllers import *

if __name__ == '__main__':
    app.run(debug=False)

