from ast import Return
from tracemalloc import start
from unicodedata import name
from flask import Flask, render_template, request, redirect, url_for
import string
import random

app = Flask(__name__)
rooms = []


@app.route("/hello")
def hello():
    return "Hello, World!"


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/createroom", methods=["POST"])
def create_room():
    username = request.form.get("name")
    room_code = None
    if request.form.get("room") == "":
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
        room_code = request.form.get("room")
        for room in rooms:
            if room["room_code"] == room_code:
                if len(room["players"]) < 2:
                    room["players"].append(username)
                    room["self_answers"][username] = []
                    room["friend_answers"][username] = []
                else:
                    return "Room Full."
    return redirect(url_for("room", room=room_code, name=username))


@app.route("/room", methods=["GET", "POST"])
def room():
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
        room_code = request.args.get("room")
        username = request.args.get("name")
        for room in rooms:
            if room["room_code"] == room_code:
                usernames = ", ".join(room["players"])
                if len(room["players"]) >= 2:
                    return render_template(
                        "room.html",
                        room=room_code,
                        players=usernames,
                        uname=username,
                        self_questions=self_questions,
                        friend_questions=friend_questions,
                    )
                else:
                    return render_template(
                        "notenufplayers.html",
                        room=room_code,
                        uname=username,
                        players=usernames,
                    )
        return redirect(url_for("index"))
    elif request.method == "POST":
        username = request.form.get("username")
        room_code = request.form.get("room")
        current_room = None
        for room in rooms:
            if room["room_code"] == room_code:
                current_room = room
        if current_room is None:
            return redirect(url_for("index"))
        i = 0
        while i < len(self_questions):
            current_room["self_answers"][username].append(request.form.get(f"self_{i}"))
            i = i + 1
        i = 0
        while i < len(friend_questions):
            current_room["friend_answers"][username].append(
                request.form.get(f"friend_{i}")
            )
            i = i + 1
        return redirect(url_for("results", room=room_code, name=username))


@app.route("/results", methods=["GET"])
def results():
    room_code = request.args.get("room")
    username = request.args.get("name")
    current_room = None
    for room in rooms:
        if room["room_code"] == room_code:
            current_room = room
    if current_room is None:
        return redirect(url_for("index"))
    players = current_room["players"]
    if players.index(username) == 0:
        other_player = players[1]
    else:
        other_player = players[0]
    if len(current_room["self_answers"][other_player]) <= 0:
        usernames = ",".join(current_room["players"])
        return render_template(
            "waitingforother.html", room=room_code, uname=username, players=usernames
        )
    score = 0
    i = 0
    while i < len(current_room["self_answers"][username]):
        if (
            current_room["self_answers"][username][i]
            == current_room["friend_answers"][other_player][i]
        ):
            score = score + 1
        i = i + 1
    i = 0
    while i < len(current_room["self_answers"][other_player]):
        if (
            current_room["self_answers"][other_player][i]
            == current_room["friend_answers"][username][i]
        ):
            score = score + 1
        i = i + 1
    return render_template(
        "results.html",
        room=room_code,
        name=username,
        score=score,
        room_data=current_room,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
