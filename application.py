from cs50 import SQL
from datetime import datetime
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = "journalexpress(cs50)"

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///journal.db")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # Check if username was entered
        username = request.form.get("username")
        if not username:
            return render_template("register.html", message="username invalid")

        # Check if password was entered
        password = request.form.get("password")
        if not password:
            return render_template("register.html", message="password invalid")

        # Check if password confirmation was entered
        password_confirm = request.form.get("confirmation")
        if not password_confirm:
            return render_template("register.html", message="please confirm password")

        # Check if password and password confirmation match
        if password != password_confirm:
            return render_template("register.html", message="passwords do not match")

        # Query for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Check if username already exists
        if len(rows) == 1:
            return render_template("register.html", message="username in use")

        # Check of username fits requirements
        char_space = 0
        for char in username:
            if char.isspace() == True:
                char_space += 1
        if char_space > 0:
            return render_template("register.html", message="username cannot include spaces")

        # Check if password fits requirements
        if len(password) < 7:
            return render_template("register.html", message="password too short")
        char_not_dig = 0
        for char in password:
            if char.isdigit() == False:
                char_not_dig += 1
        if char_not_dig == len(password):
            return render_template("register.html", message="password must include digit")


        # Insert new user into the database
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username,
                   generate_password_hash(password, method='pbkdf2:sha256', salt_length=8))

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/login", methods=["POST", "GET"])
def login():

    session.pop("user_id", None)

    # User reached route via POST (submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html", message="username invalid")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", message="password invalid")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("login.html", message="username and/or password is incorrect")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        if "user_id" in session:
            return redirect("/")
        return render_template("login.html")


@app.route("/logout")
def logout():
    # Logout of session
    session.pop("user_id", None)
    return redirect("/")


@app.route("/", methods=["POST", "GET"])
def index():
    if "user_id" in session:

        # Retreive posts from user's following list profiles
        feed = db.execute("SELECT * FROM journals WHERE user_id IN (SELECT follow_user_id FROM follows WHERE profile_user_id = ?) OR user_id = ?", session["user_id"], session["user_id"])
        if not feed:
            return render_template("index.html", message="Huh? Quite empty in here. Follow some other users to listen to what they have to say or check out the rest of the community at the explore page!")
        return render_template("index.html", feed=reversed(feed))

    else:
        return redirect("/login")


@app.route("/explore", methods=["POST", "GET"])
def explore():
    if "user_id" in session:

        # User reached route via POST (submitting a form via POST)
        if request.method == "POST":

            # If a search was made/follow button wasnt clicked
            follow = request.form.get("follow")
            if not follow:

                genre = request.form.get("genre")
                lookup = request.form.get("lookup")

                # If a genre wasn't chosen
                if not genre:
                    # If a keyword wasn't typed in
                    if not lookup:
                        return render_template("explore.html", message="{Search up some keywords or pick a genre to start your exploration}") # asks user to provide an input before searching

                    # If only a keyword was typed
                    explore = db.execute("SELECT * FROM journals WHERE (journal IN (SELECT journal FROM journals WHERE journal LIKE '%' || ? || '%' AND user_id IN (SELECT id FROM users WHERE privacy = 0))) OR (user IN (SELECT username FROM users WHERE privacy = 0 AND username LIKE '%' || ? || '%'))", lookup, lookup)
                    return render_template("explore.html", explore=reversed(explore))

                # If only a genre was picked
                if not lookup:
                    explore = db.execute("SELECT * FROM journals WHERE genre = ? AND user_id IN (SELECT id FROM users WHERE privacy = 0)", genre)
                    return render_template("explore.html", explore=reversed(explore))

                # If both a keyword and a genre was searched
                explore = db.execute("SELECT * FROM journals WHERE (journal IN (SELECT journal FROM journals WHERE journal LIKE '%' || ? || '%' AND user_id IN (SELECT id FROM users WHERE privacy = 0)) AND genre = ?) OR (user IN (SELECT username FROM users WHERE username LIKE '%' || ? || '%' AND privacy = 0) AND genre = ?)", lookup, genre, lookup, genre)
                return render_template("explore.html", explore=reversed(explore))

            # If a follow button was clicked
            else:
                # check if already following the user
                check = db.execute("SELECT id FROM follows WHERE follow_user_id = ? AND profile_user_id = ?", follow, session["user_id"])
                if len(check) != 1:
                    follow_user = db.execute("SELECT username FROM users WHERE id = ?", follow)
                    user = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
                    db.execute("INSERT INTO follows (profile_user_id, follow_user_id, profile, follows) VALUES(?, ?, ?, ?)", session["user_id"], follow, user[0]["username"], follow_user[0]["username"])

                    return redirect("/")

                else:
                    return render_template("search.html", message="{You already followed that user!}")

        # User reached route via GET (as by clicking a link or via redirect)
        else:
            return render_template("explore.html")

    else:
        return redirect("/login")


@app.route("/profile", methods=["POST", "GET"])
def profile():
    if "user_id" in session:

        # User reached route via POST (submitting a form via POST)
        if request.method == "POST":

            # Variable button value assignment
            delete = request.form.get("delete")
            unfollow = request.form.get("unfollow")
            remove = request.form.get("remove")

            # If not unfollowing a user
            if not unfollow:
                # if not removing a follower
                if not remove:
                    # delete a post
                    db.execute("DELETE FROM journals WHERE id = ?", delete)
                    return redirect("/profile")

                # Remove a user from following you
                else:
                    db.execute("DELETE FROM follows WHERE profile_user_id = ? AND follow_user_id = ?", remove, session["user_id"])
                    return redirect("/profile")

            # Unfollow a user
            else:
                db.execute("DELETE FROM follows WHERE follow_user_id = ? AND profile_user_id = ?", unfollow, session["user_id"])
                return redirect("/profile")

        # User reached route via GET (as by clicking a link or via redirect)
        else:

            username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
            entries = db.execute("SELECT * FROM journals WHERE user_id = ?", session["user_id"])
            following = db.execute("SELECT follow_user_id, follows FROM follows WHERE profile_user_id = ?", session["user_id"])
            followers = db.execute("SELECT profile_user_id, profile FROM follows WHERE follow_user_id = ?", session["user_id"])

            return render_template("profile.html", entries=reversed(entries), username=username[0]["username"], followers=len(followers), following=len(following), followinglist=following, followerlist=followers)
    else:
        return redirect("/login")


@app.route("/journal", methods=["POST", "GET"])
def journal():
    if "user_id" in session:

        # User reached route via POST (submitting a form via POST)
        if request.method == "POST":

            journal = request.form.get("journal")
            genre = request.form.get("genre")

            # If journal entry was not provided
            if not journal:
                return render_template("journal.html", message="Please provide a journal entry")
            # If no genre was selected
            if not genre:
                return render_template("journal.html", message="Please proide a genre")

            # Add journal data into database
            username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
            db.execute("INSERT INTO journals (user_id, user, journal, genre, date) VALUES(?, ?, ?, ?, ?)", session["user_id"], username[0]["username"], journal, genre, datetime.now())

            return redirect("/")

        # User reached route via GET (as by clicking a link or via redirect)
        else:
            return render_template("journal.html")
    else:
        return redirect("/login")

@app.route("/search", methods=["POST", "GET"])
def search():
    if "user_id" in session:

        # User reached route via POST (submitting a form via POST)
        if request.method == "POST":

            # If a follow button wasn't clicked
            follow = request.form.get("follow")
            if not follow:


                search = request.form.get("search")
                # If a search wasn't made
                if not search:
                    return render_template("search.html", message="Search a user to follow")

                # If a user/keyword was searched
                users = db.execute("SELECT id, username FROM users WHERE username LIKE '%' || ? || '%' AND id != ?", search, session["user_id"])

                # check if any users match the search
                if len(users) < 1:
                    return render_template("search.html", message="No users found")

                return render_template("search.html", users=users, message="{ohh, look at that!}")

            # If a follow button is clicked
            else:
                # check if already following the user
                check = db.execute("SELECT id FROM follows WHERE follow_user_id = ? AND profile_user_id = ?", follow, session["user_id"])
                user = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
                if len(check) != 1:
                    follow_user = db.execute("SELECT username FROM users WHERE id = ?", follow)
                    db.execute("INSERT INTO follows (profile_user_id, follow_user_id, profile, follows) VALUES(?, ?, ?, ?)", session["user_id"], follow, user[0]["username"], follow_user[0]["username"])

                    return redirect("/")

                else:
                    return render_template("search.html", message="{You already followed that user!}")

        # User reached route via GET (as by clicking a link or via redirect)
        else:
            return render_template("search.html", message="{Follow some inspiring souls to learn from unique perspectives}")
    else:
        return redirect("/login")

@app.route("/settings", methods=["POST", "GET"])
def settings():
    if "user_id" in session:

        # User reached route via POST (submitting a form via POST)
        if request.method == "POST":

            change_username = request.form.get("change_username")
            privacy = request.form.get("privacy")
            delete = request.form.get("delete")
            # If privacy wasnt clicked
            if not privacy:

                # Render change username page
                if change_username == "0":
                    return render_template("change_user.html")

                # Ensure username was submitted
                username = request.form.get("username")
                if not username:
                    return render_template("change_user.html", message="Please enter your username")

                # Ensure password was submitted
                password = request.form.get("password")
                if not password:
                    return render_template("change_user.html", message="Please enter your password")

                # Check if username belongs to current logged in account and if it the password is correct
                check = db.execute("SELECT * FROM users WHERE username = ? AND id = ?", username, session["user_id"])
                if len(check) != 1 or not check_password_hash(check[0]["hash"], password):
                    return render_template("change_user.html", message="username and/or password is incorrect (or doesn't belong to current logged in account)")

                new_username = request.form.get("new_username")

                # Check if desired username is available
                check = db.execute("SELECT username FROM users WHERE username = ?", new_username)
                if len(check) > 0:
                    return render_template("change_user.html", message="Not available")

                # Update all tables in database
                db.execute("UPDATE users SET username = ? WHERE id = ?", new_username, session["user_id"])
                db.execute("UPDATE journals SET user = ? WHERE user_id = ?", new_username, session["user_id"])
                db.execute("UPDATE follows SET profile = ? WHERE profile_user_id = ?", new_username, session["user_id"])
                db.execute("UPDATE follows SET follows = ? WHERE follow_user_id = ?", new_username, session["user_id"])
                return redirect("/login")

            # Change privacy setting
            else:
                if privacy == "0":
                    db.execute("UPDATE users SET privacy = ? WHERE id = ?", "1", session["user_id"])
                else:
                    db.execute("UPDATE users SET privacy = ? WHERE id = ?", "0", session["user_id"])
                return redirect("/settings")

        # User reached route via GET (as by clicking a link or via redirect)
        else:
            # Display privacy indicator according to privacy setting
            check = db.execute("SELECT privacy FROM users WHERE id = ?", session["user_id"])
            if check[0]["privacy"] == 0:
                return render_template("settings.html", priv_val=check[0]["privacy"], indicator="#ed5d4a")
            else:
                return render_template("settings.html", priv_val=check[0]["privacy"], indicator="#78f082")

        return redirect("/login")