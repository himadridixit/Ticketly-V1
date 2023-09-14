from flask import Flask, render_template, request, url_for, redirect, session, jsonify, make_response
from flask import current_app as app
from application.model import * 
from application.security import *
from flask_security import roles_required, login_user, auth_required, current_user
import requests, json

url = "http://127.0.0.1:5000"

# 1. Implement Login for Admin
# 2. Implement Registration for Admin
# 3. Make a Dashboard page for Admin with roles_requried('admin') as its decorator
# 4. Remove the UserAPI from resources.py, as well as add_resources() function in api.py

# 1. ---- make a form to create a booking in /show_id endpoint
# 2. ----create a view to show list of all the bookings at /booking
# 3. create a view for rating 

@app.route("/", methods=["GET"])
def index():
    return redirect('/login/user')

# USER LOGIN
@app.route('/login/user', methods=['POST','GET'])
def user_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email = email).first()
        if user is not None:
            result = login_user(user)
            return redirect(url_for('user_dashboard')), 301
        else:
            return "Bad Request", 404
        
    elif request.method == "GET":
        return render_template('user_login.html')


# ADMIN LOGIN
@app.route('/login/admin', methods=['POST','GET'])
def admin_login():
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]

        admin = User.query.filter_by(email = email).first()

        result = login_user(admin)

        return redirect('/admin/dashboard'), 301
    
    elif request.method == "GET":
        return render_template('admin_login.html')


# ADMIN REGISTERATION
@app.route('/register/user', methods=['GET','POST'])
def register_user():
    if request.method =='POST':
        email = request.form['email']
        password = request.form['password']

        user_datastore.create_user(email=email, password=password, fs_uniquifier = email)
        db.session.commit() 

        user = User.query.filter_by(email = email).first()
        role = Role.query.filter_by(name = "user").first()

        user_datastore.add_role_to_user(user, role)
        
        db.session.commit()
        
        return redirect(url_for('user_login'))
    
    return render_template('user_register.html')


# ADMIN REGISTERATION
@app.route('/register/admin', methods=['GET','POST'])
def register_admin():
    if request.method =='POST':
        email = request.form['email']
        password = request.form['password']
        
        user_datastore.create_user(email = email, password = password, fs_uniquifier = email)
        db.session.commit()

        user = User.query.filter_by(email=email).first()
        role = Role.query.filter_by(name='admin').first()
        user_datastore.add_role_to_user(user,role)
        db.session.commit()
        
        return redirect(url_for('admin_login'))

    return render_template('admin_register.html')
        

# USER DASHBOARD
@app.route('/user/dashboard', methods=['GET', 'POST'])
@auth_required('session')
@roles_required('user')
def user_dashboard():
    if request.method == "GET":
        result = requests.get(url + "/api/venues")
        venues = result.json()
        l = requests.get(url + "/api/locations")
        locations = l.json()
        t = requests.get(url + "/api/tags")
        tags = t.json()
        return render_template("user_dashboard.html", venues = venues, locations=locations, tags=tags)                     
    elif request.method == "POST":
        rating = request.form['rating']
        location = request.form['location']
        tags = request.form['tags']
        show_name = request.form['show_name']
        venue_name = request.form['venue_name']
        formatted_url = url + "/api/shows?rating={}&location={}&tags={}&show_name={}&venue_name={}".format(rating,location,tags,show_name,venue_name)
        result = requests.get(formatted_url)
        show_list = result.json()
        return render_template('search_result.html', shows = show_list)
        

# BOOK SHOW
@app.route('/show/book/<int:show_id>', methods=['GET', 'POST'])
@auth_required('session')
@roles_required('user')
def book_ticket(show_id):
    if request.method == 'GET':
        return render_template('book_ticket.html', show_id = show_id, error_msg = "")
    elif request.method == 'POST':
        no_of_tickets = request.form['no_of_tickets']
        tick ={
            "no_of_tickets" : no_of_tickets
        }
        headers = {
            "Content-Type": "application/json",
            "Cookie": request.headers['Cookie']
        }
        result = requests.post(url + "/api/booking/"+str(show_id), data=json.dumps(tick), headers=headers)
        if result.status_code == 400:
            return render_template('book_ticket.html', show_id = show_id, error_msg = "Houseful")
        else:    
            return redirect('/user/dashboard')


# LIST OF BOOKINGS
@app.route('/bookings', methods=['GET'])
@auth_required('session')
@roles_required('user')
def user_bookings():
    result = requests.get(url + '/api/bookings',  headers = request.headers)
    bookings = result.json()
    return render_template("bookings.html", bookings=bookings)


# GVING RATINGS
@app.route('/rating/<int:booking_id>', methods=['GET', 'POST'])
@auth_required('session')
@roles_required('user')
def rating(booking_id):
    if request.method == 'GET':
        return render_template('rating.html', booking_id = booking_id)
    elif request.method == 'POST':
        rating = request.form['rating']
        if int(rating) > 5 :
            return 'Bad Request', 400
        rate = {
            "rating": rating
        }
        headers = {
            "Content-Type": "application/json"
        }
        result = requests.patch(url + "/api/rating/"+str(booking_id), data=json.dumps(rate), headers=headers)
        return redirect(url_for('user_bookings'))


# ADMIN DASHBOARD
@app.route('/admin/dashboard', methods=['GET'])
@auth_required('session')
@roles_required('admin')
def admin_dashboard():
    result = requests.get(url + "/api/venues")
    venues = result.json()
    return render_template("admin_dashboard.html", venues = venues)


# CREATE VENUE
@app.route('/venue', methods = ['GET','POST'])
@auth_required('session')
@roles_required('admin')
def create_venue():
# if not current_user.has_role('admin'):
#     return redirect("/login/admin")
# else:
    if request.method == 'GET':
        return render_template('create_venue.html')
    elif request.method == 'POST':           
        name = request.form['name']
        place = request.form['place']
        capacity = request.form['capacity']

        venue = {   
            "name": name,
            "place": place,
            "capacity": int(capacity)
        }
        headers = {
            "Content-Type": "application/json"
        }

        result = requests.post(url + "/api/venue", headers=headers, data = json.dumps(venue))

        return redirect('/admin/dashboard')


# EDIT VENUE
@app.route("/venue/<int:venue_id>", methods = ["GET", "POST"])
@auth_required('session')
@roles_required('admin')
def edit_venue(venue_id):
    if request.method == "GET":
        result = requests.get(url + "/api/venue/" + str(venue_id))
        venue = result.json()
        return render_template("edit_venue.html", venue=venue)
    
    elif request.method == "POST":
        name = request.form['name']
        place = request.form['place']
        capacity = request.form['capacity']

        venue = {   
            "name": name,
            "place": place,
            "capacity": int(capacity)
        }
        headers = {
            "Content-Type": "application/json"
        }

        result = requests.put(url + "/api/venue/" + str(venue_id), headers=headers, data = json.dumps(venue))

        return redirect('/admin/dashboard')


# DELETE VENUE
@app.route("/venue/<int:venue_id>/delete", methods=['GET'])
@auth_required('session')
@roles_required('admin')
def delete_show(venue_id):
    result = requests.delete(url + "/api/venue/" + str(venue_id))
    return redirect("/admin/dashboard")


# DELETE SHOW
@app.route("/show/<int:show_id>/delete", methods=['GET'])
@auth_required('session')
@roles_required('admin')
def add_show(show_id):
    result = requests.delete(url + "/api/show/" + str(show_id))
    return redirect("/admin/dashboard")


# CREATE SHOW
@app.route("/show/<int:venue_id>", methods = ['GET','POST'])
@auth_required('session')
@roles_required('admin')
def create_show(venue_id):
    if request.method == 'GET':
        return render_template('create_show.html', venue_id = venue_id)
    if request.method == 'POST':
        name = request.form['name']
        tags = request.form['tags']
        price = request.form['price']
        date = request.form['date']
        time = request.form['time']
        timing = date + " " + time
        
        show = {
            "name" : name,
            "tags": tags,
            "price" : price,
            "timing" : timing
        }
        headers = {
            "Content-Type": "application/json"
        }

        result = requests.post(url + "/api/show/"+str(venue_id)+"/post", 
                               headers=headers, 
                               data= json.dumps(show))
        return redirect('/admin/dashboard')


# EDIT SHOW
@app.route("/show/<int:show_id>/edit", methods=["GET", "POST"])
@auth_required('session')
@roles_required('admin')
def edit_show(show_id):
    if request.method == "GET":
        result = requests.get(url + "/api/show/" + str(show_id))
        show = result.json()
        show['date'] = show['timing'].split(" ")[0]
        show['time'] = show['timing'].split(" ")[1]
        # return show
        return render_template("edit_show.html", show=show)
    elif request.method == "POST":
        name = request.form['name']
        tags = request.form['tags']
        price = request.form['price']
        date = request.form['date']
        time = request.form['time']
        timing = date + " " + time
        
        show = {
            "name" : name,
            "tags": tags,
            "price" : price,
            "timing" : timing
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        result = requests.put(url + "/api/show/" + str(show_id), 
                               headers = headers, 
                               data = json.dumps(show))

        return redirect('/admin/dashboard')







