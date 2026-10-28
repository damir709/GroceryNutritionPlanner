#This is the source code for the student Grocery Planner , created by Damir & Tahmid
#The project uses Flask as a local web framework, with sqlite being used to create the necessary databases.
#Hashlib and secrets libraries are used for password security
from flask import Flask, request, session, redirect
import sqlite3

#Creating the flask class object with a secret key
app = Flask(__name__)
app.secret_key = "2154"

#Method to create an SQL database
#Data is stored in users.db
def create_database():

    #Open users.db
    conn = sqlite3.connect("users.db")

    #Attempt to create the users table
    #Users will have an id, username, and password
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
            )
        """
    )
    #Commit this data to the database
    conn.commit()
    conn.close()


# User functions, writing to database
# This method takes a username and a password
def register_user(username, password):

    conn = sqlite3.connect("users.db")

    #Insert the username and password from the registration page into the database
    conn.execute(
        """
        INSERT INTO users
        (username, password)
        VALUES (?, ?)
        """,
        (username, password)
    )
    conn.commit()
    conn.close()
    
    return True

#Login verification
# This method verifies a username and a password combo are correct
def verify_login(username, password):
    
    conn = sqlite3.connect("users.db")

    #Select the password from the users table that matches a username.
    #For now, it assumes no passwords are the same
    user = conn.execute(
        """
        SELECT password
        FROM users
        WHERE username = ?
        """,
    (username,)).fetchone()
    
    conn.close()

    #If no user had that specific password
    if user is None:
        return False

    #Since the SQL query is returning a tuple, we need the first element as the password
    stored_password = user[0]

    #Return a boolean value, true is the user's password matched, false if it didn't
    return stored_password == password

#Routes for the Flask web framework, pages are viewed at 127.0.0.1:5000
#Example, the register route is found at http://127.0.0.1:5000/register

#Method for user registration
@app.route("/register", methods=["GET", "POST"])
def register():

    #If the user is requesting to send data to the Flask registration page
    if request.method == "POST":

        #Get the prompted username and password from the Flask server     
        username = request.form["username"]
        password = request.form["password"]

        #If successful or not, return so
        if register_user(username, password):
            return "Registration Successful!"
        
        return "Registration was not successful!"


    #On the webpage, return HTML elements for a simple registration page.
    return """
    <h2>Create Account</h2>

    <form method="POST">

        Username:
        <input type="text" name="username">

        <br><br>

        Password:
        <input type="password" name="password">

        <br><br>

        <input type="submit" value="Register">

    </form>
    """
#Method for user login checking
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        #Get the prompted username and password from the Flask server     
        username = request.form["username"]
        password = request.form["password"]

        #If the password from a user login matched what was in the database
        if verify_login(username, password) == True:

            #Create a session for that user with their username, and redirect them to the dashboard.
            session["username"] = username
            return redirect("/dashboard")

        #If the password did not match, say it is invalid.
        return "Invalid username or password."

    #On the webpage, return HTML elements for a login page.
    return """
    <h2>Account Login</h2>

    <form method="POST">
        Username:
        <input type="text" name="username">

        <br><br>

        Password:
        <input type="password" name="password">

        <br><br>

        <input type="submit" value="Login">
    </form>
    """

#Main dashboard to be added later
@app.route("/dashboard")
def dashboard():
    return "This is a dashboard."

#Debugging tool, used to show the users in a database
@app.route("/users")
def users():

    conn = sqlite3.connect("users.db")

    #Tool used to select the entire users table for debugging
    users = conn.execute(
        "SELECT * FROM users"
    ).fetchall()

    conn.close()

    return str(users)

if __name__ == "__main__":
    create_database()
    app.run(debug=True)
