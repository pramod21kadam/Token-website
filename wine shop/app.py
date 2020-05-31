import flask
import datetime, json
from dbhandler import dbhandler

db = dbhandler()
app = flask.Flask(__name__)
app.secret_key = '@@$^%^$#$%@$#FsfdgsDFBDF12312'

@app.route('/')
def home():
    if flask.session.get('logged_in') == True:
        return flask.redirect(flask.url_for('admin'))
    nav_links = {}
    nav_links['adminlogin'] = 'Login'
    nav_links['signup'] = 'Signup'
    nav_links['about'] = 'About'
    return flask.render_template("index.html", nav_links = nav_links, lable = "Beer")

@app.route('/getToken', methods = ["GET","POST"])
def gettoken():
    if flask.session.get('token') == True:
        return flask.render_template("token.html", nav_links =  {"about":"About"}, tokenno = flask.session.get("token_no"), timeslot = flask.session.get("timeslot"), name= flask.session.get("name"),lable = "Beer")
    if flask.request.method == "POST":
        name = flask.request.form['name']
        number = flask.request.form['number']
        if db.checkusername(name) == True:
            _,result = db.searchtoken(name,number)
            return flask.render_template("token.html", nav_links =  {"about":"About"}, tokenno=result, lable = "Beer")
        else:
            timefrom = flask.request.form["time_slot"]
            timeto = datetime.datetime.strftime((datetime.datetime.strptime(timefrom,"%I:%M  %p") + datetime.timedelta(seconds=3600)), "%I:%M %p")
            print(timefrom)
            print(timeto)
            result = (db.gettoken(name, number, timefrom, timeto))
            if result[0]:
                flask.session['name'] = name
                flask.session['token'] = result[0]
                flask.session['token_no'] = result[1]
                flask.session['timeslot'] = timefrom +" to "+ timeto
                return flask.redirect( flask.url_for('gettoken'))
            else:
                return "not available"
    else:
        timeslots = db.gettimeslots()
        slots = []
        for i in timeslots:
            now = datetime.datetime.strptime(datetime.datetime.now().strftime("%I:%M %p"), "%I:%M %p")
            if now <= datetime.datetime.strptime(i[1], "%I:%M %p"):
                slots.append(i)
        print(slots)
        return flask.render_template("form.html", nav_links = {"about":"About"}, lable = "Beer", time_slot=slots)

@app.route('/AdminLogin', methods=['GET', 'POST'])
def adminlogin():
    if flask.session.get('logged_in') == True:
        return flask.redirect(flask.url_for('admin'))
    if flask.request.method == 'POST':
        username = flask.request.form['username']
        password = flask.request.form['password']
        if db.login(username,password):
            flask.session['logged_in'] = True
            flask.session['username'] = username
            return flask.redirect(flask.url_for('admin'))
        else:
            return flask.redirect(flask.url_for('home'))
    else:
        nav_links = {"signup":"Signup", 'about':"About"}
        return flask.render_template("AdminLogin.html", nav_links = nav_links, lable= "Beer")

@app.route('/Admin')
def admin():
    if flask.session.get('logged_in') == True:
        nav_links = {}
        dropdown = {}
        dropdown["settings"] = "Settings"
        nav_links["drop"] = dropdown
        nav_links['logout'] = "Logout"
        nav_links['about'] = "About"
        return flask.render_template('Admin.html', username = flask.session.get('username'), nav_links = nav_links, lable = f' {flask.session["username"]}', timeslots = db.getalltimeslots())
    else:
        return flask.redirect(flask.url_for('adminlogin'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if flask.session.get('logged_in') == True:
        return flask.redirect(flask.url_for('admin')) 
    if flask.request.method == 'POST':
        username = flask.request.form['username']
        password = flask.request.form['password1']
        if db.signup(username,password):
            return flask.redirect(flask.url_for('adminlogin'))
    nav_links = {}
    nav_links['home'] = "Home"
    nav_links['about'] = 'About'
    return flask.render_template('signup.html', nav_links = nav_links, lable = "Beer")

@app.route('/logout')
def logout():
    flask.session.pop('logged_in', None)
    flask.session.pop('username', None)
    return flask.redirect(flask.url_for('home'))

@app.route('/about')
def about():
    nav_links = {}
    if flask.session.get('logged_in') == True:
        nav_links['admin'] = "Dashboard"
        nav_links['logout'] = "Logout"
    return flask.render_template("about.html", nav_links = nav_links, lable = "Beer")

@app.route('/check_username', methods = ['POST'])
def check_username():
    username = flask.request.form['username']
    if username and flask.request.method == 'POST':
        if db.checkusername(username):
            resp = flask.jsonify('Username unavailable')
            resp.status_code = 200
            return resp
        else:
            resp = flask.jsonify('Username available')
            resp.status_code = 200
            return resp
    else:
        resp = flask.jsonify('Username is required field')
        resp.status_code = 200
        return resp

@app.route('/settings')
def settings():
    if flask.session.get('logged_in') == True:
        nav_links = {}   
        nav_links['logout'] = "Logout"
        nav_links['about'] = "About"
        return  flask.render_template("update.html", username = flask.session.get('username'), nav_links = nav_links, lable = f' {flask.session["username"]}', timeslots = db.getalltimeslots())
    else:
        return flask.redirect(flask.url_for('adminlogin'))

@app.route("/getcustomer",methods = ['GET'])
def getcustomer():
    return json.dumps(db.users())

@app.route("/change", methods = ["POST"])
def update():
    if flask.request.method == "POST":
        for i in flask.request.form:
            r = i.split(";")
            if r[1] == "status":
                db.executeDB(f'UPDATE token set {r[1]} = "{flask.request.form[i]}" WHERE time_from = "{r[0]}"', commit=True)
                # db.conn.execute(f'UPDATE token set {r[1]} = "{flask.request.form[i]}" WHERE time_from = "{r[0]}"')
                print(f'UPDATE token set {r[1]} = "{flask.request.form[i]}" WHERE time_from = "{r[0]}"')
            else:
                db.conn.execute(f'UPDATE token set numberoftokens = {flask.request.form[i]} WHERE time_from = "{r[0]}"')
            db.conn.commit() 
    return flask.redirect( flask.url_for('settings') )

if __name__ == "__main__":
    app.run(debug=True)