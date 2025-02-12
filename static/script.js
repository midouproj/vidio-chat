const socket = io();
let peerConnection;
const config = {
    iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
};

const roomId = window.location.pathname.split("/").pop();

// انضمام إلى الغرفة
socket.emit("join_room", { room_id: roomId });

// استقبال عرض (offer)
socket.on("offer", async ({ offer }) => {
    if (!peerConnection) {
        createPeerConnection();
    }
    try {
        await peerConnection.setRemoteDescription(new RTCSessionDescription(offer));
        const answer = await peerConnection.createAnswer();
        await peerConnection.setLocalDescription(answer);
        socket.emit("answer", { room_id: roomId, answer });
    } catch (error) {
        console.error("❌ خطأ في معالجة العرض:", error);
    }
});

// استقبال إجابة (answer)
socket.on("answer", async ({ answer }) => {
    try {
        if (peerConnection && peerConnection.remoteDescription) {
            await peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
        } else {
            console.warn("⚠️ تم تلقي الإجابة قبل إعداد الاتصال بالكامل.");
        }
    } catch (error) {
        console.error("❌ خطأ في معالجة الإجابة:", error);
    }
});

// استقبال مرشح ICE
socket.on("ice_candidate", ({ candidate }) => {
    if (peerConnection) {
        peerConnection.addIceCandidate(new RTCIceCandidate(candidate)).catch(console.error);
    }
});

// إنشاء اتصال WebRTC
function createPeerConnection() {
    peerConnection = new RTCPeerConnection(config);

    peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
            socket.emit("ice_candidate", { room_id: roomId, candidate: event.candidate });
        }
    };

    peerConnection.ontrack = (event) => {
        const remoteVideo = document.getElementById("remoteVideo");
        if (remoteVideo.srcObject !== event.streams[0]) {
            remoteVideo.srcObject = event.streams[0];
        }
    };

    navigator.mediaDevices.getUserMedia({ video: true, audio: true })
        .then((stream) => {
            document.getElementById("localVideo").srcObject = stream;
            stream.getTracks().forEach((track) => peerConnection.addTrack(track, stream));
        })
        .catch(console.error);
}

// إرسال عرض (offer) عند دخول الغرفة
async function startCall() {
    if (!peerConnection) {
        createPeerConnection();
    }
    try {
        const offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);
        socket.emit("offer", { room_id: roomId, offer });
    } catch (error) {
        console.error("❌ خطأ أثناء إنشاء العرض:", error);
    }
}

// تشغيل المكالمة عند دخول المستخدم الثاني
socket.on("user_joined", () => {
    startCall();
});
