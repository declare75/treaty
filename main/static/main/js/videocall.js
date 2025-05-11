var mapPeers = {};
var mapScreenSharePeers = {};
var usernameInput = document.querySelector('#username');
var btnJoin = document.querySelector('#btn-join');
var username;
var webSocket;
var isScreenSharing = false;
var currentCenterVideo = null;
var mapAvatars = {};
var localScreenStream = null;

function webSocketOnMessage(event) {
    var parsedData = JSON.parse(event.data);
    var peerUsername = parsedData['peer'];
    var action = parsedData['action'];

    if (username == peerUsername) {
        return;
    }
    var receiver_channel_name = parsedData['message']['receiver_channel_name'];

    if (action == 'connection_rejected') {

        var reason = parsedData['message']['reason'];
        alert(reason);
        if (webSocket) {
            webSocket.close();
        }
        return;
    }

    if (action == 'new-peer') {
        var avatarUrl = parsedData['message']['avatar_url'] || '/static/main/img/noimageavatar.svg';
        mapAvatars[peerUsername] = avatarUrl;
        createOfferer(peerUsername, receiver_channel_name);

        sendSignal('send-avatar', {
            avatar_url: window.avatarUrl || '/static/main/img/noimageavatar.svg',
            receiver_channel_name: receiver_channel_name
        });
        return;
    }
    if (action == 'send-avatar') {
        var avatarUrl = parsedData['message']['avatar_url'] || '/static/main/img/noimageavatar.svg';
        mapAvatars[peerUsername] = avatarUrl;
        var avatarImg = document.getElementById(peerUsername + '-avatar');
        if (avatarImg) {
            avatarImg.src = avatarUrl;
        }
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
        var peerEntry = mapScreenSharePeers[peerUsername];
        if (peerEntry && peerEntry.senderPeer) {
            peerEntry.senderPeer.setRemoteDescription(answer).catch(error => {
                console.error(`Failed to set screen share remote description for ${peerUsername}:`, error);
            });
        }
        return;
    }
    if (action == 'screen-share-stopped') {
        stopScreenShareReceiver(peerUsername);
        return;
    }
    if (action == 'video-status') {
        var videoEnabled = parsedData['message']['video_enabled'];
        var videoContainer = document.getElementById(peerUsername + '-video-container');
        if (videoContainer) {
            var video = videoContainer.querySelector('video');
            var avatar = videoContainer.querySelector('img.avatar');
            if (video && avatar) {
                video.style.display = videoEnabled ? 'block' : 'none';
                avatar.style.display = videoEnabled ? 'none' : 'block';
            }
        }
        return;
    }
}

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
    var roomID = window.roomID || new URLSearchParams(loc.search).get('roomID') || '';
    var endPoint = wsStart + loc.host + '/ws/videocall/' + roomID + '/';
    console.log('endPoint: ', endPoint);

    webSocket = new WebSocket(endPoint);

    webSocket.addEventListener('open', (e) => {
        console.log('Connection Opened!');
        sendSignal('new-peer', {
            avatar_url: window.avatarUrl || '/static/main/img/noimageavatar.svg'
        });
    });

    webSocket.addEventListener('message', webSocketOnMessage);
    webSocket.addEventListener('close', (e) => {
        console.log('Connection closed!');

        usernameInput.disabled = false;
        usernameInput.style.visibility = 'visible';
        btnJoin.disabled = false;
        btnJoin.style.visibility = 'visible';
    });
    webSocket.addEventListener('error', (e) => {
        console.log('Error Occurred!');
    });
});

var localStream = new MediaStream();
const localVideoContainer = document.createElement('div');
localVideoContainer.id = 'local-video-container';
localVideoContainer.className = 'video-container';
const localVideo = document.createElement('video');
localVideo.id = 'local-video';
localVideo.autoplay = true;
localVideo.playsInline = true;
const localAvatar = document.createElement('img');
localAvatar.id = 'local-avatar';
localAvatar.className = 'avatar';
localAvatar.src = window.avatarUrl || '/static/main/img/noimageavatar.svg';
localVideoContainer.appendChild(localVideo);
localVideoContainer.appendChild(localAvatar);

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

        const leftBlock = document.querySelector('#left-background-block');
        leftBlock.appendChild(localVideoContainer);

        const audioTracks = localStream.getAudioTracks();
        const videoTracks = localStream.getVideoTracks();


        localVideo.style.display = (videoTracks.length === 0 || !videoTracks[0].enabled) ? 'none' : 'block';
        localAvatar.style.display = (videoTracks.length === 0 || !videoTracks[0].enabled) ? 'block' : 'none';

        if (videoTracks.length > 0) {
            videoTracks[0].addEventListener('enabledchange', () => {
                localVideo.style.display = videoTracks[0].enabled ? 'block' : 'none';
                localAvatar.style.display = videoTracks[0].enabled ? 'none' : 'block';
                sendSignal('video-status', { video_enabled: videoTracks[0].enabled });
                console.log(`Local video enabled: ${videoTracks[0].enabled}`);
            });
        }

        btnToggleAudio.addEventListener('click', () => {
            if (audioTracks.length === 0) return;
            audioTracks[0].enabled = !audioTracks[0].enabled;
            btnToggleAudio.classList.toggle('muted', !audioTracks[0].enabled);
        });

        btnToggleVideo.addEventListener('click', () => {
            if (videoTracks.length === 0) return;
            videoTracks[0].enabled = !videoTracks[0].enabled;
            btnToggleVideo.classList.toggle('muted', !videoTracks[0].enabled);
            localVideo.style.display = videoTracks[0].enabled ? 'block' : 'none';
            localAvatar.style.display = videoTracks[0].enabled ? 'none' : 'block';
            sendSignal('video-status', { video_enabled: videoTracks[0].enabled });
        });
    })
    .catch(error => {
        console.error('Ошибка доступа к устройствам:', error);
        localVideo.style.display = 'none';
        localAvatar.style.display = 'block';
        const leftBlock = document.querySelector('#left-background-block');
        leftBlock.appendChild(localVideoContainer);
    });

var btnSendMsg = document.querySelector('#btn-send-msg');
var messageList = document.querySelector('#message-list');
var messageInput = document.querySelector('#msg');
btnSendMsg.addEventListener('click', sendMsgOnClick);

function sendMsgOnClick() {
    var message = messageInput.value;
    if (!message) return;

    var li = document.createElement('li');
    li.classList.add('message-sent');
    li.appendChild(document.createTextNode('Я: ' + message));
    messageList.appendChild(li);

    var dataChannels = getDataChannels();
    message = username + ': ' + message;

    for (let index in dataChannels) {
        try {
            dataChannels[index].send(message);
        } catch (error) {
            console.error('Ошибка при отправке сообщения:', error);
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

    var remoteVideoContainer = createVideo(peerUsername);
    setOnTrack(peer, remoteVideoContainer.querySelector('video'));

    mapPeers[peerUsername] = [peer, dc, receiver_channel_name];

    peer.addEventListener('iceconnectionstatechange', () => {
        var iceConnectionState = peer.iceConnectionState;
        if (iceConnectionState === 'failed' || iceConnectionState === 'disconnected' || iceConnectionState === 'closed') {
            delete mapPeers[peerUsername];
            if (iceConnectionState != 'closed') {
                peer.close();
            }
            removeVideo(remoteVideoContainer);
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

    var remoteVideoContainer = createVideo(peerUsername);
    setOnTrack(peer, remoteVideoContainer.querySelector('video'));

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
            removeVideo(remoteVideoContainer);
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


    if (!mapScreenSharePeers[peerUsername]) {
        mapScreenSharePeers[peerUsername] = {
            senderPeer: null,
            receiverPeer: null,
            receiver_channel_name: receiver_channel_name
        };
    }
    mapScreenSharePeers[peerUsername].senderPeer = peer;

    peer.addEventListener('iceconnectionstatechange', () => {
        var iceConnectionState = peer.iceConnectionState;
        if (iceConnectionState === 'failed' || iceConnectionState === 'disconnected' || iceConnectionState === 'closed') {
            if (mapScreenSharePeers[peerUsername]) {
                mapScreenSharePeers[peerUsername].senderPeer = null;
                if (!mapScreenSharePeers[peerUsername].receiverPeer) {
                    delete mapScreenSharePeers[peerUsername];
                }
            }
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

    let remoteScreenVideo = document.getElementById(peerUsername + '-screen-video');
    if (!remoteScreenVideo) {
        remoteScreenVideo = createScreenVideo(peerUsername);
    }

    var peer = new RTCPeerConnection(null);

    const audioTrack = localStream.getAudioTracks()[0];
    if (audioTrack) {
        peer.addTrack(audioTrack, localStream);
    }
    peer.addTransceiver('video', { direction: 'recvonly' });

    setScreenShareOnTrack(peer, remoteScreenVideo);


    if (!mapScreenSharePeers[peerUsername]) {
        mapScreenSharePeers[peerUsername] = {
            senderPeer: null,
            receiverPeer: null,
            receiver_channel_name: receiver_channel_name
        };
    }
    mapScreenSharePeers[peerUsername].receiverPeer = peer;

    peer.addEventListener('iceconnectionstatechange', () => {
        var iceConnectionState = peer.iceConnectionState;
        if (iceConnectionState === 'failed' || iceConnectionState === 'disconnected' || iceConnectionState === 'closed') {
            if (mapScreenSharePeers[peerUsername]) {
                mapScreenSharePeers[peerUsername].receiverPeer = null;
                if (!mapScreenSharePeers[peerUsername].senderPeer) {
                    delete mapScreenSharePeers[peerUsername];
                }
            }
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
    li.classList.add('message-received');
    li.appendChild(document.createTextNode(message));
    messageList.appendChild(li);
}

function createVideo(peerUsername) {
    var leftBlock = document.querySelector('#left-background-block');
    var videoContainer = document.createElement('div');
    videoContainer.id = peerUsername + '-video-container';
    videoContainer.className = 'video-container';
    var remoteVideo = document.createElement('video');
    remoteVideo.id = peerUsername + '-video';
    remoteVideo.autoplay = true;
    remoteVideo.playsInline = true;
    var remoteAvatar = document.createElement('img');
    remoteAvatar.id = peerUsername + '-avatar';
    remoteAvatar.className = 'avatar';
    remoteAvatar.src = mapAvatars[peerUsername] || '/static/main/img/noimageavatar.svg';

    remoteVideo.style.display = 'none';
    remoteAvatar.style.display = 'block';
    videoContainer.appendChild(remoteVideo);
    videoContainer.appendChild(remoteAvatar);
    leftBlock.appendChild(videoContainer);


    videoContainer.addEventListener('click', (e) => {
        if (remoteVideo.style.display !== 'none') {
            moveToCenter(videoContainer);
        }
    });

    return videoContainer;
}

function createScreenVideo(peerUsername) {
    var leftBlock = document.querySelector('#left-background-block');
    var remoteScreenVideo = document.createElement('video');
    remoteScreenVideo.id = peerUsername + '-screen-video';
    remoteScreenVideo.autoplay = true;
    remoteScreenVideo.playsInline = true;
    leftBlock.appendChild(remoteScreenVideo);

    remoteScreenVideo.addEventListener('click', () => {
        moveToCenter(remoteScreenVideo);
    });

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


            if (track.kind === 'video' && remoteVideo.id.endsWith('-video')) {
                const videoContainer = remoteVideo.parentElement;
                const avatar = videoContainer ? videoContainer.querySelector('img.avatar') : null;
                if (videoContainer && avatar) {
                    remoteVideo.style.display = track.enabled ? 'block' : 'none';
                    avatar.style.display = track.enabled ? 'none' : 'block';
                    track.addEventListener('enabledchange', () => {
                        remoteVideo.style.display = track.enabled ? 'block' : 'none';
                        avatar.style.display = track.enabled ? 'none' : 'block';
                        console.log(`Video track for ${remoteVideo.id} enabled: ${track.enabled}`);
                    });
                }
            }
            remoteVideo.play().catch(e => console.warn(`Failed to play video ${remoteVideo.id}:`, e));
        }
    });
}

function setScreenShareOnTrack(peer, remoteVideo) {
    let remoteStream = new MediaStream();
    remoteVideo.srcObject = remoteStream;

    peer.addEventListener('track', (event) => {
        const track = event.track;
        if (!remoteStream.getTracks().includes(track)) {
            remoteStream.addTrack(track);
            console.log(`Added screen share track ${track.kind} to ${remoteVideo.id}`);
            remoteVideo.srcObject = remoteStream;
            remoteVideo.play().catch(e => console.warn(`Failed to play screen video ${remoteVideo.id}:`, e));
        }
    });
}

function removeVideo(element) {
    if (!element) {
        return;
    }

    if (element.parentNode && element.id !== 'local-video-container') {
        if (element === currentCenterVideo) {
            currentCenterVideo = null;
        }
        element.parentNode.removeChild(element);
    } else if (element === currentCenterVideo) {

        currentCenterVideo = null;
    }
}

function moveToCenter(videoContainer) {
    const centerBlock = document.querySelector('#center-background-block');
    const leftBlock = document.querySelector('#left-background-block');

    if (currentCenterVideo && currentCenterVideo !== videoContainer) {

        leftBlock.appendChild(currentCenterVideo);
        currentCenterVideo.classList.remove('video-entering');
    }


    while (centerBlock.firstChild) {
        centerBlock.removeChild(centerBlock.firstChild);
    }
    videoContainer.classList.add('video-entering');
    centerBlock.appendChild(videoContainer);
    currentCenterVideo = videoContainer;

    setTimeout(() => {
        videoContainer.classList.remove('video-entering');
    }, 50);
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
            localScreenStream = screenStream;
            const screenTrack = screenStream.getVideoTracks()[0];

            for (let peerUsername in mapPeers) {
                const receiver_channel_name = mapPeers[peerUsername][2];
                createScreenShareOfferer(peerUsername, receiver_channel_name, screenStream);
            }

            const localScreenVideo = createScreenVideo('local');
            const localScreenMediaStream = new MediaStream([screenTrack]);
            localScreenVideo.srcObject = localScreenMediaStream;
            localScreenVideo.play().catch(e => console.warn(`Failed to play local screen video:`, e));

            isScreenSharing = true;
            btnShareScreen.classList.add('sharing');

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
        const peerEntry = mapScreenSharePeers[peerUsername];
        if (peerEntry && peerEntry.senderPeer) {
            peerEntry.senderPeer.close();
            peerEntry.senderPeer = null;
            sendSignal('screen-share-stopped', { 'receiver_channel_name': peerEntry.receiver_channel_name });
            if (!peerEntry.receiverPeer) {
                delete mapScreenSharePeers[peerUsername];
            }
        }
    }

    const localScreenVideo = document.getElementById('local-screen-video');
    if (localScreenVideo) {
        removeVideo(localScreenVideo);
    }


    if (localScreenStream) {
        localScreenStream.getTracks().forEach(track => {
            console.log(`Stopping screen share track: ${track.kind}, id: ${track.id}`);
            track.stop();
        });
        localScreenStream = null;
    }

    isScreenSharing = false;
    btnShareScreen.classList.remove('sharing');
}

function stopScreenShareReceiver(peerUsername) {
    if (mapScreenSharePeers[peerUsername]) {
        const peerEntry = mapScreenSharePeers[peerUsername];
        if (peerEntry.receiverPeer) {
            peerEntry.receiverPeer.close();
            peerEntry.receiverPeer = null;

            if (currentCenterVideo && currentCenterVideo.id === peerUsername + '-screen-video') {
                removeVideo(currentCenterVideo);

                moveNextScreenShareToCenter();
            } else {

                const remoteScreenVideo = document.getElementById(peerUsername + '-screen-video');
                if (remoteScreenVideo) {
                    removeVideo(remoteScreenVideo);
                }
            }
            if (!peerEntry.senderPeer) {
                delete mapScreenSharePeers[peerUsername];
            }
        }
    }
}

function moveNextScreenShareToCenter() {
    if (!currentCenterVideo) {
        const leftBlock = document.querySelector('#left-background-block');
        const screenVideos = leftBlock.querySelectorAll('video[id$="-screen-video"]');
        if (screenVideos.length > 0) {
            const nextVideo = screenVideos[0];
            moveToCenter(nextVideo);
        }
    }
}

const btnToggleFullscreen = document.querySelector('#btnToggleFullscreen');
btnToggleFullscreen.addEventListener('click', () => {
    const centerBlock = document.querySelector('#center-background-block');
    const video = centerBlock.querySelector('video');

    if (!video) {
        console.warn('No video in center block to toggle fullscreen.');
        return;
    }

    if (!document.fullscreenElement) {
        video.requestFullscreen().then(() => {
            btnToggleFullscreen.classList.add('fullscreen');
        }).catch(error => {
            console.error('Failed to enter fullscreen:', error);
        });
    } else {
        document.exitFullscreen().then(() => {
            btnToggleFullscreen.classList.remove('fullscreen');
        }).catch(error => {
            console.error('Failed to exit fullscreen:', error);
        });
    }
});

document.addEventListener('fullscreenchange', () => {
    if (!document.fullscreenElement) {
        btnToggleFullscreen.classList.remove('fullscreen');
    } else {
        btnToggleFullscreen.classList.add('fullscreen');
    }
});