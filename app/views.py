"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""
import os, random, datetime
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from forms import LoginForm, MyForm
from models import UserProfile
from werkzeug.utils import secure_filename


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html')


@app.route('/profile/', methods=["GET", "POST"])
def profile():
    myform= MyForm()
    
    if request.method == 'POST':
        if myform.validate_on_submit():
            first_name= myform.first_name.data
            last_name= myform.last_name.data
            gender= myform.gender.data
            email= myform.email.data
            location= myform.location.data
            biography= myform.biography.data
            upload= myform.upload.data
            
            filename= secure_filename(upload.filename)
            upload.save(os.path.join(
                app.config['UPLOAD_FOLDER'], filename
                ))
            
            profile_date = datetime.date.today().strftime("%b %d, %Y")
            user_id = genId(first_name, last_name, location)
            
            new_profile = UserProfile(first_name=first_name, last_name=last_name, gender=gender, email=email, location=location, biography=biography, upload=filename, profile_creation=profile_date)
            
            db.session.add(new_profile)
            db.session.commit()
                
            
            flash('Profile added!')
            return redirect(url_for("profiles"))
            
        flash_errors(myform)
    return render_template('profile.html', form=myform)
    

@app.route('/profiles/', methods=["GET", "POST"])
def profiles():
    
    users = UserProfile.query.all()

    user_list = [{"userid": user.id} for user in users]
    
    if request.method == "GET":
        file_folder = app.config['UPLOAD_FOLDER']
        return render_template("profiles.html", users=users)
    
    elif request.method == "POST":
        response = make_response(jsonify({"users": user_list}))                                           
        response.headers['Content-Type'] = 'application/json'            
        return response
        
        
        
@app.route('/profile/<userid>', methods=["GET", "POST"])
def get_profile(userid):
    
    user = UserProfile.query.filter_by(id=userid).first()
    
    if request.method == "GET":
        file_folder = app.config['UPLOAD_FOLDER']
        return render_template("user_profile.html", user=user)
    
    elif request.method == "POST":
        if user is not None:
            response = make_response(jsonify(userid=user.id, first_name=user.first_namename, last_name=user.last_namename, gender=user.gender, email=user.email, upload=user.upload,  location=user.location, biography=user.biography,
                    profile_creation=user.profile_creation))
            response.headers['Content-Type'] = 'application/json'            
            return response
        else:
            flash('No User Found', 'danger')
            return redirect(url_for("profiles"))



@app.route("/login", methods=["GET", "POST"])
def login():
    
    if current_user.is_authenticated:
        # if user is already logged in, just redirect them to our secure page
        # or some other page like a dashboard
        return render_template('secure_page.html')
        
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = UserProfile.query.filter(username== "mrbowla", UserProfile.password == "lab5").first()
        if user is not None:
            login_user(user)
        
        else:
            flash('Username or Password is incorrect.', 'danger')
            flash_errors(form)
            return render_template('login.html', form=form)
        flash('Logged in successfully.', 'success')
        return render_template('secure_page.html')
        
        
    else:
        flash('Username or Password is incorrect.', 'danger')
        flash_errors(form)
        return render_template('login.html', form=form)
        # change this to actually validate the entire form submission
        # and not just one field
    #if form.username.data:
            # Get the username and password values from the form.
           
            

            # using your model, query database for a user based on the username
            # and password submitted
            # store the result of that query to a `user` variable so it can be
            # passed to the login_user() method.

            # get user id, load into session
           # login_user(user)

            # remember to flash a message to the user
          #  return redirect(url_for("home"))  # they should be redirected to a secure-page route instead
   # return render_template("login.html", form=form)


@app.route("/logout/")
@login_required
def logout():
    # Logout the user and end the session
    logout_user()
    flash('You have been logged out.', 'danger')
    return render_template('home.html')



# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return UserProfile.query.get(int(id))




def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'danger')
            
            
###
# The functions below should be applicable to all Flask apps.
###


@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
    
    
def genId(first_name, last_name, location):
    nid = []
    for x in first_name:
        nid.append(str(ord(x)))
    for x in last_name:
        nid.append(str(ord(x)))
    for x in location:
        nid.append(str(ord(x)))
    
    random.shuffle(nid)
    
    nid = "".join(nid)
    
    return nid[:7]


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")
