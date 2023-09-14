from flask_restful import Resource, reqparse, Api
from application.model import *
from werkzeug.security import generate_password_hash
from flask import current_app as app
from application.resources import *
# from application.resources.VenueAPI import VenueAPI

# Step 1
api = Api() 

# Step 3
def init_api(app):
    api.init_app(app)

# Step 2
def add_resources():    
    api.add_resource(ShowAPI, '/api/show/<int:venue_id>/post', '/api/show/<int:show_id>')
    api.add_resource(VenuesAPI, '/api/venues')
    api.add_resource(VenueAPI, '/api/venue', '/api/venue/<int:id>')
    api.add_resource(BookingAPI, '/api/booking/<int:show_id>', '/api/bookings', '/api/rating/<int:booking_id>')
    api.add_resource(SearchAPI, '/api/shows')
    api.add_resource(LocationAPI, '/api/locations')
    api.add_resource(TagsAPI, '/api/tags')
    return
