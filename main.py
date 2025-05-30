from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO

app = Flask(__name__)
app.config["SECRET_KEY"] = "hjhjsdahhds"
socketio = SocketIO(app)


rooms = {
    "8": {"members": 0, "messages": []},
    "9": {"members": 0, "messages": []},
    "10": {"members": 0, "messages": []},
    "11": {"members": 0, "messages": []},
    "12": {"members": 0, "messages": []},
}

@app.route("/", methods=["GET"])
def home():
    session.clear()
    return render_template("homepage.html")

@app.route("/join", methods=["GET", "POST"])
def join():
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")

        if not name:
            return render_template("home.html", error="Please enter a name.", code=code, name=name)

        if code not in rooms:
            return render_template("home.html", error="Invalid class code.", code=code, name=name)

        session["room"] = code
        session["name"] = name
        return redirect(url_for("room"))
    ## molq ako stane problem opravi route functionality 
    return render_template("home.html")
    
@app.route("/homepage")
def homepage():
    return render_template("homepage.html")

    
@app.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))

    return render_template("room.html", code=room, messages=rooms[room]["messages"])

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return 
    ##ne pipai
    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")

@socketio.on("connect")
def connect():
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")
    ##ako shte pipash neshto me pitai tvurde mn vreme si izubih s tova
@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1

    send({"name": name, "message": "has left the room"}, to=room)##lubimata mi chast
    print(f"{name} has left the room {room}")

if __name__ == "__main__":
    socketio.run(app, debug=True)
