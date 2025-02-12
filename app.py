from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room, emit
import manage_rooms
import json
import os

app = manage_rooms.app  # ✅ استخدام التطبيق من manage_rooms.py
socketio = SocketIO(app, cors_allowed_origins="*")

# تحميل بيانات الغرف
ROOMS_FILE = "rooms.json"
if os.path.exists(ROOMS_FILE):
    with open(ROOMS_FILE, "r") as file:
        rooms = json.load(file)
else:
    rooms = {}

@app.route('/', methods=['GET', 'POST'])
def index():
    """الصفحة الرئيسية لواجهة تسجيل الدخول إلى الغرف"""
    error = None
    if request.method == 'POST':
        room_id = request.form.get("room_id")
        password = request.form.get("password")

        if room_id and password:
            if room_id in rooms:
                if rooms[room_id] == password:
                    return redirect(url_for('video_chat', room_id=room_id))
                else:
                    error = "❌ ID أو الرقم السري خاطئ!"
            else:
                rooms[room_id] = password
                with open(ROOMS_FILE, "w") as file:
                    json.dump(rooms, file)
                return redirect(url_for('video_chat', room_id=room_id))

    return render_template('index.html', error=error)

@app.route('/video_chat/<room_id>', methods=['GET'])
def video_chat(room_id):
    """صفحة غرفة الفيديو بعد التحقق من ID وكلمة المرور"""
    if room_id in rooms:
        return render_template('video_chat.html', room_id=room_id)
    return redirect(url_for('index'))

# 🟢 **WebRTC Events via WebSockets** 🟢

@socketio.on("join_room")
def handle_join(data):
    """حدث عند دخول المستخدم إلى الغرفة"""
    room_id = data.get("room_id")
    join_room(room_id)
    emit("user_joined", {"room_id": room_id}, room=room_id, broadcast=True)

@socketio.on("leave_room")
def handle_leave(data):
    """حدث عند مغادرة المستخدم للغرفة"""
    room_id = data.get("room_id")
    leave_room(room_id)
    emit("user_left", {"room_id": room_id}, room=room_id, broadcast=True)

@socketio.on("offer")
def handle_offer(data):
    """إرسال عرض WebRTC (Offer) للمستخدم الآخر"""
    room_id = data["room_id"]
    offer = data["offer"]
    emit("offer", {"offer": offer}, room=room_id, include_self=False)

@socketio.on("answer")
def handle_answer(data):
    """إرسال إجابة WebRTC (Answer) عند استلام العرض"""
    room_id = data["room_id"]
    answer = data["answer"]
    emit("answer", {"answer": answer}, room=room_id, include_self=False)

@socketio.on("ice_candidate")
def handle_ice_candidate(data):
    """تمرير مرشحات ICE بين المستخدمين لتحسين الاتصال"""
    room_id = data["room_id"]
    candidate = data["candidate"]
    emit("ice_candidate", {"candidate": candidate}, room=room_id, include_self=False)

# تشغيل الخادم
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=True)
