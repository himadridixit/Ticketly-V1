from flask_restful import Resource, reqparse
from application.model import *
from application.security import *
from datetime import datetime
import json
from flask import session, request


"""
1. Add Venue: /api/venue
2. Get Venue: /api/venue/<int: venue_id>
3. Edit Venue: /api/venue/<int:venue_id>
4. Delete venue: /api/venue/<int:venue_id>
"""

create_show_parser = reqparse.RequestParser()
create_show_parser.add_argument("name", type=str)
create_show_parser.add_argument("tags", type=str)
create_show_parser.add_argument("price", type=int)
create_show_parser.add_argument("timing", type=str)
class ShowAPI(Resource):

    def post(self, venue_id):
        args = create_show_parser.parse_args()
        show_name = args.get("name", None)
        tags = args.get("tags", None)
        price = args.get("price", None)
        timing = args.get("timing", None)
        timing_datetime = datetime.strptime(timing, "%Y-%m-%d %H:%M")

        if show_name is None or price is None:
            return "name and price are required", 400
        
        venue = Venue.query.filter_by(venue_id = venue_id).first()

        new_show = Show(venue_id=venue_id, Sname=show_name, Tags=tags, price=price, timing=timing_datetime, tickets_remaining=venue.capacity, rating=0)
        try:
            db.session.add(new_show)
            db.session.flush()
        except Exception as e:
            print(e)
            db.session.rollback()

        db.session.commit()
        
        return {"show_id":new_show.show_id,
                "venue_id":new_show.venue_id,
                "name":new_show.Sname,
                "timing":str(new_show.timing),
                "price":new_show.price,
                "tags":new_show.Tags}, 201
    
    def get(self, show_id):
        show = Show.query.filter_by(show_id = show_id).first() 
        if show:
            return {
                "show_id":show.show_id,
                "name":show.Sname, 
                "timing":str(show.timing),
                "price":show.price,
                "tags":show.Tags}, 200
        else:
            return "no show found", 404
   
    def delete(self, show_id):
        show = Show.query.filter_by(show_id = show_id).first()
        if show is None:
            return "no such show exists", 404
        else:
            try:
                db.session.delete(show)
                db.session.flush()
            except Exception as e:
                print(e)
                db.session.rollback()
            db.session.commit()
            return "show sucssesfully deleted", 201
    
    def put(self, show_id):
        args = create_show_parser.parse_args()

        show_name = args.get("name", None)
        tags = args.get("tags", None)
        price = args.get("price", None)
        timing = args.get("timing", None)
        timing_datetime = datetime.strptime(timing, "%Y-%m-%d %H:%M")

        show = Show.query.filter_by(show_id = show_id).first()
        if show is None:
            return "No such show", 404
        else:
            if show_name is not None:
                show.Sname = show_name
            if price is not None:
                show.price = price
            if tags is not None:
                show.Tags = tags
            if timing is not None:
                show.timing = timing_datetime
            try:
                db.session.add(show)
                db.session.flush()
            except Exception as e:
                print(e)
                db.session.rollback()
            db.session.commit()

            return {
                "show_id":show.show_id,
                "name":show.Sname,
                "timing":str(show.timing),
                "price":show.price,
                "Tags":show.Tags
                }, 201
            


create_venue_parser = reqparse.RequestParser()
create_venue_parser.add_argument("name", type=str)
create_venue_parser.add_argument("place", type=str)
create_venue_parser.add_argument("capacity", type=int)

class VenueAPI(Resource):   
    def post(self):
        args = create_venue_parser.parse_args()
        
        venue_name = args.get("name", None)
        place = args.get("place", None)
        capacity = args.get("capacity", None)

        if venue_name is None or place is None or capacity is None:
            return venue_name, 400
        
        new_venue = Venue(Vname=venue_name, place=place, capacity=capacity)
        try:
            db.session.add(new_venue)
            db.session.flush()
        except Exception as e:
            print(e)
            db.session.rollback()

        db.session.commit() 
        
        return {"venue_id":new_venue.venue_id, "name":new_venue.Vname, "place":new_venue.place, "capacity":new_venue.capacity}, 201
    
    def get(self, id):

        venue = Venue.query.filter_by(venue_id = id).first()

        if venue is None:
            return "No Such Venue Found", 404
        else:
            return {"venue_id":venue.venue_id, "name":venue.Vname, "place":venue.place, "capacity":venue.capacity}, 200
    
    def delete(self, id):

        venue = Venue.query.filter_by(venue_id = id).first()
        
        if venue is None:
            return "No such venue exists", 404
        else:
            try:
                db.session.delete(venue)
                db.session.flush()
            except Exception as e:
                print(e) 
                db.session.rollback()

            db.session.commit()

            return "show sucssesfully deleted", 201
    
    def put(self, id):

        args = create_venue_parser.parse_args()
        venuename = args.get("name", None)
        place = args.get("place", None)
        capacity = args.get("capacity", None)
        
        venue = Venue.query.filter_by(venue_id = id).first()

        if venue is None:
            return "no such venue found", 404
        else:
            if venuename is not None:
                venue.Vname = venuename
            if place is not None:
                venue.place = place
            if capacity is not None:
                venue.capacity = capacity
            try:
                db.session.add(venue)
                db.session.flush()
            except Exception as e:
                print(e)
                db.session.rollback()
            db.session.commit()
            
            return {
                    "venue_id":venue.venue_id,
                    "name":venue.Vname,
                    "place":venue.place,
                    "capacity":venue.capacity
                    }, 201
# 201: Created
# 200: Ok
class VenuesAPI(Resource):
    def get(self):
        venues = Venue.query.all()
        venue_list = []
        for venue in venues:
            venue_dict = {
                "venue_id":venue.venue_id,
                "Vname":venue.Vname,
                "place":venue.place,
                "capacity":venue.capacity,
                "shows":[]
            }
            for show in venue.shows:
                show_dict = {
                    "show_id":show.show_id,
                    "Sname":show.Sname,
                    "Tags":show.Tags,
                    "price":show.price,
                    "tickets_remaining":show.tickets_remaining,
                    "rating":show.rating,
                    "timing":str(show.timing)
                }
                venue_dict["shows"].append(show_dict)
            venue_dict["shows"] = list(reversed(venue_dict["shows"]))
            venue_list.append(venue_dict)
        return venue_list, 200
    
create_booking_parser = reqparse.RequestParser()
create_booking_parser.add_argument("no_of_tickets", type=int)
create_booking_parser.add_argument("rating", type=int)

class BookingAPI(Resource):
    def post(self, show_id):
        user_id = session["_user_id"]
        # # Creates a booking
        args = create_booking_parser.parse_args()
        no_of_tickets = args.get("no_of_tickets", None)

        show = Show.query.filter_by(show_id = show_id).first()
        if show.tickets_remaining >= no_of_tickets:
            booking = Booking(show_id = show_id, user_id = user_id, no_of_tickets = no_of_tickets)
            show.tickets_remaining = show.tickets_remaining - no_of_tickets
        else:
            return "Show is houseful. Please try booking another show.", 400
        try:
            db.session.add(booking)
            db.session.add(show)
            db.session.flush()
        except Exception as e:
            print(e)
            db.session.rollback()
        
        db.session.commit()
        return {
                "booking_id" : booking.booking_id,
                "user_id" : booking.user_id,
                "show_id" : booking.show_id,
                "no_of_tickets" : booking.no_of_tickets
        }, 201
    
    def get(self):
        # Retrieves all the bookings
        user_id = session["_user_id"]
        bookings = Booking.query.filter_by(user_id = int(user_id)).all()
        booking_list = []
        for booking in bookings:
            show = Show.query.filter_by(show_id = int(booking.show_id)).first()
            venue = Venue.query.filter_by(venue_id = int(show.venue_id)).first()
            booking_dict = {
                "show_id": booking.show_id,
                "booking_id": booking.booking_id,
                "no_of_tickets": booking.no_of_tickets,
                "show_name": show.Sname,
                "venue_name": venue.Vname,
                "venue_id": venue.venue_id,
                "show_timings": str(show.timing)
            }
            booking_list.append(booking_dict)
        return booking_list, 200

    def patch(self,booking_id):
        # Rates a booking
        args = create_booking_parser.parse_args()
        rating = args.get("rating", 0)
        booking = Booking.query.filter_by(booking_id = int(booking_id)).first() 
        
        if booking.rating is not None:
            return 'Bad Request', 400
        
        booking.rating = rating
        
        show = Show.query.filter_by(show_id = int(booking.show_id)).first()
        no_of_bookings = len(show.bookings)
        if show.rating is not None :
            show.rating =  ( (show.rating * (no_of_bookings-1)) + rating) / (no_of_bookings)
        else:
            show.rating = rating
        try :
            db.session.add(booking)
            db.session.add(show)
            db.session.flush()
        except Exception as e: 
            print(e)
            db.session.rollback()
        db.session.commit()

        return "Show successfully rated", 200    

class SearchAPI(Resource):
    def get(self):
        rating = request.args.get('rating')
        location = request.args.get('location')
        tags = request.args.get('tags')
        show_name = request.args.get('show_name')
        venue_name = request.args.get('venue_name')
        if rating == "" :
            rating = 0
        if location == "":
            location = "%%"
        if tags == "":
            tags = "%%"
        if show_name == "":
            show_name = "%%"
        if venue_name == "":
            venue_name = "%%"    

        # Show.query is different from db.session.query, kyunki Show.query is just a 
        shows = db.session.query(Show.show_id, Show.Sname, Show.rating, Show.Tags, Show.price, Show.timing, Show.tickets_remaining, Venue.Vname, Venue.place).join(Venue).filter(Show.rating >= rating).filter(Venue.place.like(location)).filter(Show.Tags.ilike(tags)).filter(Show.Sname.ilike(show_name)).filter(Venue.Vname.ilike(venue_name)).all()
        show_list = []
        for show in shows:
            show_dict = {
                "show_id": show.show_id,
                "show_name": show.Sname,
                "show_ratings": show.rating,
                "show_tag": show.Tags,
                "show_price": show.price,
                "show_timing": str(show.timing),
                "show_tickets_remaining": show.tickets_remaining,
                "venue_name": show.Vname,
                "venue_location": show.place    
            }
            show_list.append(show_dict)
        return show_list
        
class LocationAPI(Resource):
    def get(self):
        location_list = []
        venues = Venue.query.distinct(Venue.place).all()
        for venue in venues:
            location_list.append(venue.place)
        return location_list

class TagsAPI(Resource):
        def get(self):
            tags_list = []
            shows = Show.query.distinct(Show.Tags).all()
            for show in shows:
                tags_list.append(show.Tags)
            return tags_list
            