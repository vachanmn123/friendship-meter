"""

Project: Friendship-Meter
Author: Vachan MN
LICENSE: MIT LICENSE

file: app.py

Main file for the application. This file conatins the routes and controllers. Execution starts here.
"""
# Import Required Modules
from flask import Flask, render_template, request, redirect, url_for
import string
import random

# Define the flask app
app = Flask(__name__)
rooms = []


@app.route("/hello")
def hello():
    """
    route for "/hello". Returns a string "Hello World"
    """
    return "Hello, World!"


@app.route("/", methods=["GET"])
def index():
    """
    route for "/". Returns the home page.
    """
    return render_template("index.html")


@app.route("/createroom", methods=["POST"])
def create_room():
    """
    route for "/createroom". If room code is specified, add to room. Else, generate a random room code. Finally return waiting page.
    """
    # get username from form.
    username = request.form.get("name")
    room_code = None
    if request.form.get("room") == "":
        # If room code is not specified, create a new room.
        room_code = "".join(random.choices(string.ascii_uppercase + string.digits, k=7))
        rooms.append(
            {
                "room_code": room_code,
                "players": [username],
                "self_answers": {username: []},
                "friend_answers": {username: []},
            }
        )
    else:
        # If room code is specified, add to the room.
        room_code = request.form.get("room")
        for room in rooms:
            if room["room_code"] == room_code:
                if len(room["players"]) < 2:
                    room["players"].append(username)
                    room["self_answers"][username] = []
                    room["friend_answers"][username] = []
                else:
                    # If 2 people are already in the room. Return error.
                    return "Room Full."
    return redirect(url_for("room", room=room_code, name=username))


@app.route("/room", methods=["GET", "POST"])
def room():
    """
    route for "/room" if GET, returns the game page. else if POST, returns the results waiting page.
    """
    self_questions = [
        "What is your bestie's name?",
        "What is your age?",
        "What is your height?",
        "What is your weight?",
    ]
    friend_questions = [
        "What is your friend's bestie's name?",
        "What is your friend's age?",
        "What is your friend's height?",
        "What is your friend's weight?",
    ]
    if request.method == "GET":
        # If GET, return the game page.
        # Get the room code and name from the URL.
        room_code = request.args.get("room")
        username = request.args.get("name")
        # Find the room from room code.
        for room in rooms:
            if room["room_code"] == room_code:
                # Make a string of player.
                usernames = ", ".join(room["players"])
                if len(room["players"]) == 2:
                    # Return the game page.
                    return render_template(
                        "room.html",
                        room=room_code,
                        players=usernames,
                        uname=username,
                        self_questions=self_questions,
                        friend_questions=friend_questions,
                    )
                else:
                    # If there is not enough players, return the waiting page.
                    return render_template(
                        "notenufplayers.html",
                        room=room_code,
                        uname=username,
                        players=usernames,
                    )
        # If room code is not found, return to home.
        return redirect(url_for("index"))
    elif request.method == "POST":
        # If POST, return the results waiting page.
        # Get username and room code from the form.
        username = request.form.get("username")
        room_code = request.form.get("room")
        # Find the room from room code.
        current_room = None
        for room in rooms:
            if room["room_code"] == room_code:
                current_room = room
        if current_room is None:
            # If the room was not found, return to home.
            return redirect(url_for("index"))
        # Get the answers and add to the room data.
        i = 0
        while i < len(self_questions):
            current_room["self_answers"][username].append(
                request.form.get(f"self_{i}").toLowerCase()
            )
            i = i + 1
        i = 0
        while i < len(friend_questions):
            current_room["friend_answers"][username].append(
                request.form.get(f"friend_{i}").toLowerCase()
            )
            i = i + 1
        # Return redirect to results.
        return redirect(url_for("results", room=room_code, name=username))


@app.route("/results", methods=["GET"])
def results():
    """
    route for "/results". Returns the results page if all players answered. else returns waiting page.
    """
    # Get the room code and username from the URL.
    room_code = request.args.get("room")
    username = request.args.get("name")
    # Find the room from room code.
    current_room = None
    for room in rooms:
        if room["room_code"] == room_code:
            current_room = room
    if current_room is None:
        # If room is not found. Return to home.
        return redirect(url_for("index"))
    # Get the other player's info.
    players = current_room["players"]
    if players.index(username) == 0:
        other_player = players[1]
    else:
        other_player = players[0]
    if len(current_room["self_answers"][other_player]) <= 0:
        # If the other player has not yet answered. Return waiting page.
        usernames = ",".join(current_room["players"])
        return render_template(
            "waitingforother.html", room=room_code, uname=username, players=usernames
        )
    # Calculate the score.
    score = 0
    i = 0
    while i < len(current_room["self_answers"][username]):
        if (
            current_room["self_answers"][username][i]
            == current_room["friend_answers"][other_player][i]
        ):
            # If both answers match, add a point.
            score = score + 1
        i = i + 1
    i = 0
    while i < len(current_room["self_answers"][other_player]):
        if (
            current_room["self_answers"][other_player][i]
            == current_room["friend_answers"][username][i]
        ):
            # If both answers match, add a point.
            score = score + 1
        i = i + 1
    # Return the results page.
    return render_template(
        "results.html",
        room=room_code,
        name=username,
        score=score,
        room_data=current_room,
    )


if __name__ == "__main__":
    # Run the development server.
    app.run(debug=True, host="0.0.0.0", port=8000)
