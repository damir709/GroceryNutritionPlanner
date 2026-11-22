#This is the source code for the student Grocery Planner , created by Damir & Tahmid
#The project uses Flask as a local web framework, with sqlite being used to create the necessary databases.
#Hashlib and secrets libraries are used for password security
from flask import Flask, request, session, redirect
import sqlite3

#Creating the flask class object with a secret key
app = Flask(__name__)
app.secret_key = "2154"

#Method to create an SQL database for users, and baskets
#Data is stored in users.db
def create_database():

    #Open users.db
    conn = sqlite3.connect("users.db")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS basket (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1
        )
    """)

    #Commit this data to the database
    conn.commit()
    conn.close()

    #Create another database of items that users can browse
    #Open users .db
    conn = sqlite3.connect("items.db")

    #Create a table for the item information
    #Items will have a name, brand, food group, calories, price, type, and a location
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            brand TEXT NOT NULL,
            food_group TEXT,
            calories INTEGER NOT NULL,
            price DECIMAL(7, 2) NOT NULL,
            type TEXT NOT NULL,
            location TEXT
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

    #If the user is requesting to send data to the Flask registration page...
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

            #Create a session for that user with their username, and redirect them to the search page.
            session["username"] = username
            return redirect("/dashboard")

        #If the password did not match, say it is invalid.
        return "Invalid username or password."

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

#Method to searching items
@app.route("/search", methods=["GET", "POST"])
def search():

    #Users must be logged in to search for items
    if "username" not in session:
        return redirect("/login")

    #Create a list to hold potential item search results
    results = []
    html_results = ""

    #If the user is requesting to submit text in the search route...
    if request.method == "POST":

        #Get the term the user wants to search, like "Banana"
        search_term = request.form["search"]

        #Connect to the items database
        conn = sqlite3.connect("items.db")

        #Select the items that match what the user has searched
        index = conn.execute(
            """
            SELECT *
            FROM items
            WHERE name LIKE ?
            """,
            ('%' + search_term + '%',)
        )

        #Fetch all the results for the user and display them
        results = index.fetchall()

        #Since results are lists, format them with HTML
        html_results = ""

        #For every element in the results query, format them and display them to the user
        for item in results:
            html_results += f"""
            <p>
            <strong>{item[1]}</strong><br>
            Brand: {item[2]}<br>
            Calories: {item[4]}<br>
            Price: ${item[5]}
            </p>

            <a href="/add_to_basket/{item[0]}">
                Add To Basket
            </a>
            <hr>
            """
        
        conn.close()

    return f"""
    <h2>Search Items</h2>
    <a href="/dashboard">Dashboard</a> |
    <a href="/basket">Basket</a> |
    <a href="/items">All Items</a>
    <br><br>

    <form method="POST">
    <input type="text" name="search">
    <input type="submit" value="Search">
    </form>
    <br>

    {html_results}
    """

#Method for viewing every item in the items database, debugging tool
@app.route("/items")
def items():

    conn = sqlite3.connect("items.db")

    items = conn.execute(
        "SELECT * FROM items"
    ).fetchall()

    conn.close()

    return str(items)


#Method for viewing a user basket
#Baskets are created in the flask user session, while users are logged on they can access their basket
#Baskets are currently not stored upon user logout
@app.route("/basket")
def basket():

    #User must be logged in
    if "username" not in session:
        return redirect("/login")

    username = session["username"]

    #Get the user's ID
    users_conn = sqlite3.connect("users.db")

    user = users_conn.execute(
        """
        SELECT id
        FROM users
        WHERE username = ?
        """,
        (username,)
    ).fetchone()

    users_conn.close()

    if user is None:
        return "User not found."

    user_id = user[0]

    #Open both databases
    basket_conn = sqlite3.connect("users.db")
    items_conn = sqlite3.connect("items.db")

    #Get everything in this user's basket
    basket_items = basket_conn.execute(
        """
        SELECT item_id, quantity
        FROM basket
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchall()

    html = """
    <h2>Your Basket</h2>

    <a href="/dashboard">Dashboard</a> |
    <a href="/search">Search</a>

    <hr>
    """

    total = 0

    #Display each basket item
    for basket_item in basket_items:

        item_id = basket_item[0]
        quantity = basket_item[1]

        item = items_conn.execute(
            """
            SELECT *
            FROM items
            WHERE id = ?
            """,
            (item_id,)
        ).fetchone()

        if item:

            name = item[1]
            brand = item[2]
            price = item[5]

            subtotal = price * quantity

            html += f"""
            <p>
            <strong>{name}</strong><br>
            Brand: {brand}<br>
            Quantity: {quantity}<br>
            Price: ${price:.2f}<br>
            Subtotal: ${subtotal:.2f}
            </p>

            <hr>
            """

            total += subtotal

    html += f"""
    <h3>Total: ${total:.2f}</h3>
    """

    basket_conn.close()
    items_conn.close()

    return html


#Method for adding items to a user basket
@app.route("/add_to_basket/<int:item_id>")
def add_to_basket(item_id):

    if "username" not in session:
        return redirect("/login")

    username = session["username"]

    conn = sqlite3.connect("users.db")

    #Get the user's ID
    user = conn.execute(
        """
        SELECT id
        FROM users
        WHERE username = ?
        """,
        (username,)
    ).fetchone()

    user_id = user[0]

    #Add the item to the basket
    conn.execute(
        """
        INSERT INTO basket
        (user_id, item_id, quantity)
        VALUES (?, ?, 1)
        """,
        (user_id, item_id)
    )

    conn.commit()
    conn.close()

    return redirect("/basket")



#Main dashboard
@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect("/login")

    return f"""
    <h1>Welcome {session["username"]}</h1>

    <button onclick="window.location.href='/search'">
        Search Items
    </button>

    <br><br>

    <button onclick="window.location.href='/basket'">
        View Basket
    </button>

    <br><br>

    <button onclick="window.location.href='/items'">
        Browse All Items
    </button>

    <br><br>

    <button onclick="window.location.href='/logout'">
        Logout
    </button>
    """

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
