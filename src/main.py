#This is the source code for the student Grocery Planner , created by Damir & Tahmid
#The project uses Flask as a local web framework, with sqlite being used to create the necessary databases.
from flask import Flask, request, session, redirect
import sqlite3

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
def register_user(username, password):

    conn = sqlite3.connect("users.db")

    #
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

#To be added later
def verify_login(username, password):
    pass

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


    #On the webpage, return HTML elements for a simple login page.
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

#Main dashboard to be added later
@app.route("/dashboard")
def dashboard():
    return "This is a dashboard."

if __name__ == "__main__":
    create_database()
    app.run(debug=True)
