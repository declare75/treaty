var mapPeers = {};
var mapScreenSharePeers = {};
var usernameInput = document.querySelector('#username');
var btnJoin = document.querySelector('#btn-join');
var username;
var webSocket;
var isScreenSharing = false; // 🛠️ ADDED: Track screen sharing state

// Обработка входящих WebSocket-сообщений
function webSocketOnMessage(event) {
    var parsedData = JSON.parse(event.data);

    var peerUsername = parsedData['peer'];
    var action = parsedData['action'];

    if (username == peerUsername) {
        return;
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
        peer.setRemoteDescription(answer).catch(error => {
            console.error(`Failed to set remote description for ${peerUsername}:`, error);
        });
        return;
    }
    if (action == 'new-screen-offer') {
        var offer = parsedData['message']['sdp'];
        createScreenShareAnswerer(offer, peerUsername, receiver_channel_name);
        return;
    }
    if (action == 'new-screen-answer') {
        var answer = parsedData['message']['sdp'];
        var peer = mapScreenSharePeers[peerUsername][0];
        peer.setRemoteDescription(answer).catch(error => {
            console.error(`Failed to set screen share remote description for ${peerUsername}:`, error);
        });
        return;
    }
    if (action == 'screen-share-stopped') {
        stopScreenShareReceiver(peerUsername);
        return;
    }
}

// Подключение по WebSocket при клике на кнопку "Join"
btnJoin.addEventListener('click', () => {
    username = usernameInput.value;
    console.log('username: ', username);

    if (username == '') {
        return;
    }

    usernameInput.value = '';
    usernameInput.disabled = true;
    usernameInput.style.visibility = 'hidden';
    btnJoin.disabled = true;
    btnJoin.style.visibility = 'hidden';

    var labelUsername = document.querySelector('#label-username');
    labelUsername.innerHTML = username;

    var loc = window.location;
    var wsStart = (loc.protocol === 'https:') ? 'wss://' : 'ws://';
    var endPoint = wsStart + loc.host + '/ws/videocall/';
    console.log('endPoint: ', endPoint);

    webSocket = new WebSocket(endPoint);

    webSocket.addEventListener('open', (e) => {
        console.log('Connection Opened!');
        sendSignal('new-peer', {});
    });

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

navigator.mediaDevices.enumerateDevices()
    .then(devices => {
        const audioInputs = devices.filter(device => device.kind === 'audioinput');
        const hasVideo = devices.some(device => device.kind === 'videoinput');

        if (audioInputs.length === 0) {
            console.warn('Микрофон не найден.');
            return;
        }

        const constraints = {
            audio: {
                deviceId: audioInputs[0].deviceId,
                echoCancellation: {ideal: true},
                noiseSuppression: {ideal: true},
                autoGainControl: {ideal: true},
                sampleRate: 48000,
                channelCount: 2
            },
            video: hasVideo
        };

        return navigator.mediaDevices.getUserMedia(constraints);
    })
    .then(stream => {
        if (!stream) return;

        const audioContext = new AudioContext();
        const source = audioContext.createMediaStreamSource(stream);

        const highpass = audioContext.createBiquadFilter();
        highpass.type = 'highpass';
        highpass.frequency.setValueAtTime(100, audioContext.currentTime);

        const compressor = audioContext.createDynamicsCompressor();
        compressor.threshold.setValueAtTime(-50, audioContext.currentTime);
        compressor.knee.setValueAtTime(40, audioContext.currentTime);
        compressor.ratio.setValueAtTime(12, audioContext.currentTime);
        compressor.attack.setValueAtTime(0, audioContext.currentTime);
        compressor.release.setValueAtTime(0.25, audioContext.currentTime);

        const destination = audioContext.createMediaStreamDestination();

        source.connect(highpass);
        highpass.connect(compressor);
        compressor.connect(destination);

        const processedAudioStream = destination.stream;
        const audioTrack = processedAudioStream.getAudioTracks()[0];
        const videoTrack = stream.getVideoTracks()[0] || null;

        localStream = new MediaStream();
        if (audioTrack) localStream.addTrack(audioTrack);
        if (videoTrack) localStream.addTrack(videoTrack);

        console.log('Filtered audio track:', audioTrack);
        localVideo.srcObject = localStream;
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

var btnSendMsg = document.querySelector('#btn-send-msg');
var messageList = document.querySelector('#message-list');
var messageInput = document.querySelector('#msg');
btnSendMsg.addEventListener('click', sendMsgOnClick);

function sendMsgOnClick() {
    var message = messageInput.value;
    if (!message) return;

    var li = document.createElement('li');
    li.appendChild(document.createTextNode('Me: ' + message));
    messageList.appendChild(li);

    var dataChannels = getDataChannels();
    message = username + ': ' + message;

    for (let index in dataChannels) {
        try {
            dataChannels[index].send(message);
        } catch (error) {
            console.error('Failed to send message:', error);
        }
    }
    messageInput.value = '';
}

function sendSignal(action, message) {
    var jsonStr = JSON.stringify({
        'peer': username,
        'action': action,
        'message': message,
    });
    if (webSocket.readyState === WebSocket.OPEN) {
        webSocket.send(jsonStr);
    }
}

function createOfferer(peerUsername, receiver_channel_name) {
    var peer = new RTCPeerConnection(null);

    addLocalTracks(peer);

    var dc = peer.createDataChannel('channel');
    dc.addEventListener('open', () => {
        console.log('Connection opened for', peerUsername);
    });
    dc.addEventListener('message', dcOnMessage);

    var remoteVideo = createVideo(peerUsername);
    setOnTrack(peer, remoteVideo);

    mapPeers[peerUsername] = [peer, dc, receiver_channel_name];

    peer.addEventListener('iceconnectionstatechange', () => {
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
        })
        .catch(error => {
            console.error('Failed to create offer:', error);
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
            console.log('Connection opened for', peerUsername);
        });
        peer.dc.addEventListener('message', dcOnMessage);
        mapPeers[peerUsername] = [peer, peer.dc, receiver_channel_name];
    });

    peer.addEventListener('iceconnectionstatechange', () => {
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
        .catch(error => {
            console.error(`Failed to set remote description or create answer for ${peerUsername}:`, error);
        });
}

function createScreenShareOfferer(peerUsername, receiver_channel_name, screenStream) {
    var peer = new RTCPeerConnection(null);

    const audioTrack = localStream.getAudioTracks()[0];
    const screenTrack = screenStream.getVideoTracks()[0];
    const screenMediaStream = new MediaStream([audioTrack, screenTrack]);

    screenMediaStream.getTracks().forEach(track => {
        console.log('Adding screen share track:', track.kind);
        const sender = peer.addTrack(track, screenMediaStream);
        if (track.kind === 'audio') {
            const params = sender.getParameters();
            if (!params.encodings) {
                params.encodings = [{}];
            }
            params.encodings[0].maxBitrate = 128000;
            sender.setParameters(params).catch(e => {
                console.warn('Failed to set audio bitrate:', e);
            });
        }
    });

    mapScreenSharePeers[peerUsername] = [peer, null, receiver_channel_name];

    peer.addEventListener('iceconnectionstatechange', () => {
        var iceConnectionState = peer.iceConnectionState;
        if (iceConnectionState === 'failed' || iceConnectionState === 'disconnected' || iceConnectionState === 'closed') {
            delete mapScreenSharePeers[peerUsername];
            if (iceConnectionState != 'closed') {
                peer.close();
            }
            const remoteScreenVideo = document.getElementById(peerUsername + '-screen-video');
            if (remoteScreenVideo) {
                removeVideo(remoteScreenVideo);
            }
        }
    });
    peer.addEventListener('icecandidate', (event) => {
        if (event.candidate) {
            console.log('New screen share ice candidate', JSON.stringify(peer.localDescription));
            return;
        }

        sendSignal('new-screen-offer', {
            'sdp': peer.localDescription,
            'receiver_channel_name': receiver_channel_name
        });
    });

    peer.createOffer()
        .then(o => peer.setLocalDescription(o))
        .then(() => {
            console.log('Screen share local description set successfully.');
        })
        .catch(error => {
            console.error('Failed to create screen share offer:', error);
        });
}

function createScreenShareAnswerer(offer, peerUsername, receiver_channel_name) {
    var peer = new RTCPeerConnection(null);

    const audioTrack = localStream.getAudioTracks()[0];
    if (audioTrack) {
        peer.addTrack(audioTrack, localStream);
    }
    peer.addTransceiver('video', { direction: 'recvonly' });

    var remoteScreenVideo = createScreenVideo(peerUsername);
    setOnTrack(peer, remoteScreenVideo);

    mapScreenSharePeers[peerUsername] = [peer, null, receiver_channel_name];

    peer.addEventListener('iceconnectionstatechange', () => {
        var iceConnectionState = peer.iceConnectionState;
        if (iceConnectionState === 'failed' || iceConnectionState === 'disconnected' || iceConnectionState === 'closed') {
            delete mapScreenSharePeers[peerUsername];
            if (iceConnectionState != 'closed') {
                peer.close();
            }
            removeVideo(remoteScreenVideo);
        }
    });
    peer.addEventListener('icecandidate', (event) => {
        if (event.candidate) {
            console.log('New screen share ice candidate', JSON.stringify(peer.localDescription));
            return;
        }

        sendSignal('new-screen-answer', {
            'sdp': peer.localDescription,
            'receiver_channel_name': receiver_channel_name
        });
    });

    peer.setRemoteDescription(offer)
        .then(() => {
            console.log('Screen share remote description set successfully for %s.', peerUsername);
            return peer.createAnswer();
        })
        .then(a => {
            console.log('Screen share answer created!');
            peer.setLocalDescription(a);
        })
        .catch(error => {
            console.error(`Failed to set screen share remote description or create answer for ${peerUsername}:`, error);
        });
}

function addLocalTracks(peer) {
    localStream.getTracks().forEach(track => {
        console.log('Adding track:', track.kind);
        const sender = peer.addTrack(track, localStream);
        if (track.kind === 'audio') {
            const params = sender.getParameters();
            if (!params.encodings) {
                params.encodings = [{}];
            }
            params.encodings[0].maxBitrate = 128000;
            sender.setParameters(params).catch(e => {
                console.warn('Failed to set audio bitrate:', e);
            });
        }
    });
}

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
    videoWrapper.appendChild(remoteVideo);
    videoContainer.appendChild(videoWrapper);
    return remoteVideo;
}

function createScreenVideo(peerUsername) {
    var videoContainer = document.querySelector('#video-container');
    var remoteScreenVideo = document.createElement('video');
    remoteScreenVideo.id = peerUsername + '-screen-video';
    remoteScreenVideo.autoplay = true;
    remoteScreenVideo.playsInline = true;
    var videoWrapper = document.createElement('div');
    videoWrapper.appendChild(remoteScreenVideo);
    videoContainer.appendChild(videoWrapper);
    return remoteScreenVideo;
}

function setOnTrack(peer, remoteVideo) {
    let remoteStream = new MediaStream();
    remoteVideo.srcObject = remoteStream;

    peer.addEventListener('track', (event) => {
        const track = event.track;
        if (!remoteStream.getTracks().includes(track)) {
            remoteStream.addTrack(track);
            console.log(`Added track ${track.kind} to ${remoteVideo.id}`);
            remoteVideo.srcObject = remoteStream;
            remoteVideo.play().catch(e => console.warn(`Failed to play video ${remoteVideo.id}:`, e));
        }
    });
}

function removeVideo(remoteVideo) {
    if (remoteVideo && remoteVideo.parentNode) {
        remoteVideo.parentNode.remove();
    }
}

function getDataChannels() {
    var dataChannels = [];
    for (let peerUsername in mapPeers) {
        var dataChannel = mapPeers[peerUsername][1];
        dataChannels.push(dataChannel);
    }
    return dataChannels;
}

var btnShareScreen = document.querySelector('#btn-share-screen');
// 🛠️ MODIFIED: Toggle screen sharing on click
btnShareScreen.addEventListener('click', () => {
    if (isScreenSharing) {
        stopScreenShare();
    } else {
        startScreenShare();
    }
});

function startScreenShare() {
    navigator.mediaDevices.getDisplayMedia({video: true})
        .then(screenStream => {
            const screenTrack = screenStream.getVideoTracks()[0];

            for (let peerUsername in mapPeers) {
                const receiver_channel_name = mapPeers[peerUsername][2];
                createScreenShareOfferer(peerUsername, receiver_channel_name, screenStream);
            }

            const localScreenVideo = createScreenVideo('local');
            const localScreenStream = new MediaStream([screenTrack]);
            localScreenVideo.srcObject = localScreenStream;

            // 🛠️ ADDED: Update button and state
            isScreenSharing = true;
            btnShareScreen.textContent = 'Stop Sharing';

            screenTrack.onended = () => {
                stopScreenShare();
            };
        })
        .catch(error => {
            console.error('Ошибка при доступе к экрану:', error);
        });
}

function stopScreenShare() {
    for (let peerUsername in mapScreenSharePeers) {
        const [peer, , receiver_channel_name] = mapScreenSharePeers[peerUsername];
        peer.close();
        const remoteScreenVideo = document.getElementById(peerUsername + '-screen-video');
        if (remoteScreenVideo) {
            removeVideo(remoteScreenVideo);
        }
        delete mapScreenSharePeers[peerUsername];
        sendSignal('screen-share-stopped', { 'receiver_channel_name': receiver_channel_name });
    }

    const localScreenVideo = document.getElementById('local-screen-video');
    if (localScreenVideo) {
        removeVideo(localScreenVideo);
    }

    // 🛠️ ADDED: Reset button and state
    isScreenSharing = false;
    btnShareScreen.textContent = 'Share Screen';
}

function stopScreenShareReceiver(peerUsername) {
    if (mapScreenSharePeers[peerUsername]) {
        const [peer, ,] = mapScreenSharePeers[peerUsername];
        peer.close();
        const remoteScreenVideo = document.getElementById(peerUsername + '-screen-video');
        if (remoteScreenVideo) {
            removeVideo(remoteScreenVideo);
        }
        delete mapScreenSharePeers[peerUsername];
    }
}