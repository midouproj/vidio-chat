from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

ROOM_FILE = "rooms.json"

def load_rooms():
    """تحميل قائمة الغرف من ملف JSON."""
    if not os.path.exists(ROOM_FILE):
        return {}

    with open(ROOM_FILE, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}

def save_rooms(data):
    """حفظ قائمة الغرف إلى ملف JSON."""
    with open(ROOM_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

@app.route("/add_room", methods=["POST"])
def add_room():
    """إضافة غرفة جديدة مع كلمة مرور."""
    data = request.json
    room_id = data.get("room_id")
    password = data.get("password")

    if not room_id or not password:
        return jsonify({"error": "يجب إدخال room_id و password"}), 400

    rooms = load_rooms()
    if room_id in rooms:
        return jsonify({"error": "هذه الغرفة موجودة بالفعل"}), 409

    rooms[room_id] = password
    save_rooms(rooms)

    return jsonify({"message": "تمت إضافة الغرفة بنجاح!", "room_id": room_id})

@app.route("/delete_room", methods=["POST"])
def delete_room():
    """حذف غرفة بناءً على معرفها."""
    data = request.json
    room_id = data.get("room_id")

    if not room_id:
        return jsonify({"error": "يجب إدخال room_id"}), 400

    rooms = load_rooms()
    if room_id not in rooms:
        return jsonify({"error": "الغرفة غير موجودة"}), 404

    del rooms[room_id]
    save_rooms(rooms)

    return jsonify({"message": "تم حذف الغرفة بنجاح", "room_id": room_id})

@app.route("/list_rooms", methods=["GET"])
def list_rooms():
    """إرجاع قائمة بجميع الغرف المسجلة."""
    rooms = load_rooms()
    return jsonify(rooms)

if __name__ == "__main__":
    app.run(debug=True)
