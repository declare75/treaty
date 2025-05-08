console.log('In videocall.js!');

var mapPeers = {};
var usernameInput = document.querySelector('#username');
var btnJoin = document.querySelector('#btn-join');
var username;
var webSocket;

// Обработка входящих WebSocket-сообщений
function webSocketOnMessage(event) {
    var parsedData = JSON.parse(event.data);

    var peerUsername = parsedData['peer'];
    var action = parsedData['action'];

    if (username == peerUsername) {
        return
    }
    var receiver_channel_name = parsedData['message']['receiver_channel_name'];

    if (action == 'new-peer') {
        createOfferer(peerUsername, receiver_channel_name);
        return;
    }
    if (action == 'new-offer') {
        var offer = parsedData['message']['sdp'];

        createAnswerer(offer, peerUsername, receiver_channel_name);
        return;
    }
    if (action == 'new-answer') {
        var answer = parsedData['message']['sdp'];

        var peer = mapPeers[peerUsername][0];

        peer.setRemoteDescription(answer);

        return;
    }
}

// Подключение по WebSocket при клике на кнопку "Join"
btnJoin.addEventListener('click', () => {
    username = usernameInput.value;
    console.log('username: ', username);

    if (username == '') {
        return; // Не подключаться, если имя пустое
    }

    // Отключение UI после ввода
    usernameInput.value = '';
    usernameInput.disabled = true;
    usernameInput.style.visibility = 'hidden';
    btnJoin.disabled = true;
    btnJoin.style.visibility = 'hidden';

    // Показ имени пользователя
    var labelUsername = document.querySelector('#label-username');
    labelUsername.innerHTML = username;

    // Подготовка WebSocket-соединения
    var loc = window.location;
    var wsStart = (loc.protocol === 'https:') ? 'wss://' : 'ws://';
    var endPoint = wsStart + loc.host + '/ws/videocall/';
    console.log('endPoint: ', endPoint);

    webSocket = new WebSocket(endPoint);

    // Событие: соединение установлено
    webSocket.addEventListener('open', (e) => {
        console.log('Connection Opened!');

        sendSignal('new-peer', {});
    });

    // Обработка других событий WebSocket
    webSocket.addEventListener('message', webSocketOnMessage);
    webSocket.addEventListener('close', (e) => {
        console.log('Connection closed!');
    });
    webSocket.addEventListener('error', (e) => {
        console.log('Error Occurred!');
    });
});

// Инициализация локального потока
var localStream = new MediaStream();
const localVideo = document.querySelector('#local-video');


// Запрос списка устройств
navigator.mediaDevices.enumerateDevices()
    .then(devices => {
        // Проверяем наличие микрофона и камеры
        const audioInputs = devices.filter(device => device.kind === 'audioinput');
        const hasVideo = devices.some(device => device.kind === 'videoinput');

        if (audioInputs.length === 0) {
            console.warn('Микрофон не найден.');
            return;
        }

        // Можно показать выбор микрофона, если их несколько
        if (audioInputs.length > 1) {
            console.log('Доступные микрофоны:');
            audioInputs.forEach((device, index) => {
                console.log(`${index + 1}: ${device.label || 'Без названия'} — ${device.deviceId}`);
            });
        }

        // Настройка ограничений — только доступные устройства
        const constraints = {
            audio: {
                deviceId: audioInputs[0].deviceId // Можно позволить выбрать пользователю
            },
            video: hasVideo // Только если есть камера
        };

        // Запрашиваем доступ к устройствам
        return navigator.mediaDevices.getUserMedia(constraints);
    })
    .then(stream => {
        if (!stream) return;
        localStream = stream;
        console.log('Audio tracks:', stream.getAudioTracks());
        localVideo.srcObject = stream;
        localVideo.muted = true;

        const audioTracks = localStream.getAudioTracks();
        const videoTracks = localStream.getVideoTracks();

        btnToggleAudio.addEventListener('click', () => {
            if (audioTracks.length === 0) return;

            audioTracks[0].enabled = !audioTracks[0].enabled;
            btnToggleAudio.innerHTML = audioTracks[0].enabled ? 'Audio Mute' : 'Audio Unmute';
        });

        btnToggleVideo.addEventListener('click', () => {
            if (videoTracks.length === 0) return;

            videoTracks[0].enabled = !videoTracks[0].enabled;
            btnToggleVideo.innerHTML = videoTracks[0].enabled ? 'Video Mute' : 'Video Unmute';
        });

    })
    .catch(error => {
        console.error('Ошибка доступа к устройствам:', error);
    });


function sendSignal(action, message) {
    var jsonStr = JSON.stringify({
        'peer': username,
        'action': action,
        'message': message,
    });
    webSocket.send(jsonStr);
}

function createOfferer(peerUsername, receiver_channel_name) {
    var peer = new RTCPeerConnection(null);

    addLocalTracks(peer);

    var dc = peer.createDataChannel('channel');
    dc.addEventListener('open', () => {
        console.log('Connection opened!');
    })
    dc.addEventListener('message', dcOnMessage);

    var remoteVideo = createVideo(peerUsername);
    setOnTrack(peer, remoteVideo);

    mapPeers[peerUsername] = [peer, dc];

    peer.addEventListener('icecandidate', () => {
        var iceConnectionState = peer.iceConnectionState;

        if (iceConnectionState === 'failed' || iceConnectionState === 'disconnected' || iceConnectionState === 'closed') {
            delete mapPeers[peerUsername];

            if (iceConnectionState != 'closed') {
                peer.close();
            }

            removeVideo(remoteVideo);
        }
    });
    peer.addEventListener('icecandidate', (event) => {
        if (event.candidate) {
            console.log('New ice candidate', JSON.stringify(peer.localDescription));

            return;
        }

        sendSignal('new-offer', {
            'sdp': peer.localDescription,
            'receiver_channel_name': receiver_channel_name
        });
    });

    peer.createOffer()
        .then(o => peer.setLocalDescription(o))
        .then(() => {
            console.log('Local description set successfully.');
        });
}

function createAnswerer(offer, peerUsername, receiver_channel_name) {
    var peer = new RTCPeerConnection(null);

    addLocalTracks(peer);

    var remoteVideo = createVideo(peerUsername);
    setOnTrack(peer, remoteVideo);

    peer.addEventListener('datachannel', e => {
        peer.dc = e.channel;
        peer.dc.addEventListener('open', () => {
            console.log('Connection opened!');
        })
        peer.dc.addEventListener('message', dcOnMessage);

        mapPeers[peerUsername] = [peer, peer.dc];

    });

    peer.addEventListener('icecandidate', () => {
        var iceConnectionState = peer.iceConnectionState;

        if (iceConnectionState === 'failed' || iceConnectionState === 'disconnected' || iceConnectionState === 'closed') {
            delete mapPeers[peerUsername];

            if (iceConnectionState != 'closed') {
                peer.close();
            }

            removeVideo(remoteVideo);
        }
    });
    peer.addEventListener('icecandidate', (event) => {
        if (event.candidate) {
            console.log('New ice candidate', JSON.stringify(peer.localDescription));

            return;
        }

        sendSignal('new-answer', {
            'sdp': peer.localDescription,
            'receiver_channel_name': receiver_channel_name
        });
    });

    peer.setRemoteDescription(offer)
        .then(() => {
            console.log('Remote description set successfully for %s.', peerUsername);

            return peer.createAnswer();
        })
        .then(a => {
            console.log('Answer created!');

            peer.setLocalDescription(a);
        })
}

function addLocalTracks(peer) {
    localStream.getTracks().forEach(track => {
        console.log('Adding track:', track.kind);
        peer.addTrack(track, localStream);
    });
}

var messageList = document.querySelector('#message-list');

function dcOnMessage(event) {
    var message = event.data;

    var li = document.createElement('li');
    li.appendChild(document.createTextNode(message));
    messageList.appendChild(li);
}

function createVideo(peerUsername) {
    var videoContainer = document.querySelector('#video-container');

    var remoteVideo = document.createElement('video');

    remoteVideo.id = peerUsername + '-video';
    remoteVideo.autoplay = true;
    remoteVideo.playsInline = true;

    var videoWrapper = document.createElement('div');

    videoContainer.appendChild(videoWrapper);

    videoContainer.appendChild(remoteVideo);

    return remoteVideo;
}

function setOnTrack(peer, remoteVideo) {
    var remoteStream = new MediaStream();

    remoteVideo.srcObject = remoteStream;

    peer.addEventListener('track', async (event) => {
        remoteStream.addTrack(event.track, remoteStream);
    });
}

function removeVideo(remoteVideo) {
    var videoWrapper = video.parentNode;

    videoWrapper.parentNode.removeChild(videoWrapper);
}
