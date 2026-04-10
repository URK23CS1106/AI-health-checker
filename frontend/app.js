document.addEventListener('DOMContentLoaded', () => {

    // --- Authentication Logic ---
    const authModal = document.getElementById('auth-modal');
    const authForm = document.getElementById('auth-form');
    const authTitle = document.getElementById('auth-title');
    const authToggle = document.getElementById('auth-toggle');
    const authError = document.getElementById('auth-error');
    const authUsername = document.getElementById('auth-username');
    const authPassword = document.getElementById('auth-password');
    const logoutBtn = document.getElementById('logout-btn');

    let isLoginMode = true;
    let token = localStorage.getItem('pulse_token');

    // Check auth on load
    if (token) {
        authModal.classList.add('hidden');
        logoutBtn.classList.remove('hidden');
    }

    authToggle.addEventListener('click', () => {
        isLoginMode = !isLoginMode;
        if(isLoginMode) {
            authTitle.innerText = "Welcome to Pulse AI";
            authToggle.innerText = "Register";
            authToggle.parentElement.innerHTML = `Don't have an account? <span id="auth-toggle">Register</span>`;
        } else {
            authTitle.innerText = "Create an Account";
            authToggle.innerText = "Login";
            authToggle.parentElement.innerHTML = `Already have an account? <span id="auth-toggle">Login</span>`;
        }
        // reattach listener dynamically
        document.getElementById('auth-toggle').addEventListener('click', authToggle.click);
    });

    authForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = authUsername.value.trim();
        const password = authPassword.value;
        authError.innerText = "";

        if(isLoginMode) {
            // LOGIN
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            try {
                const res = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: formData.toString()
                });
                const data = await res.json();
                if(res.ok) {
                    token = data.access_token;
                    localStorage.setItem('pulse_token', token);
                    authModal.classList.add('hidden');
                    logoutBtn.classList.remove('hidden');
                    authUsername.value = '';
                    authPassword.value = '';
                } else {
                    authError.innerText = data.detail || "Login failed.";
                }
            } catch (err) {
                authError.innerText = "Connection error.";
            }
        } else {
            // REGISTER
            try {
                const res = await fetch('/api/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                const data = await res.json();
                if(res.ok) {
                    authError.style.color = "#34d399";
                    authError.innerText = "Registration successful! Please login.";
                    setTimeout(() => document.getElementById('auth-toggle').click(), 1500);
                } else {
                    authError.style.color = "#ef4444";
                    authError.innerText = data.detail || "Registration failed.";
                }
            } catch (err) {
                authError.innerText = "Connection error.";
            }
        }
    });

    logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('pulse_token');
        token = null;
        logoutBtn.classList.add('hidden');
        authModal.classList.remove('hidden');
        switchTab(navChat, chatSection, navHistory, historySection);
    });

    function getAuthHeaders() {
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };
    }

    // --- Navigation Logic ---
    const navChat = document.getElementById('nav-chat');
    const navHistory = document.getElementById('nav-history');
    const chatSection = document.getElementById('chat-section');
    const historySection = document.getElementById('history-section');

    function switchTab(activeNav, activeSec, hiddenNav, hiddenSec) {
        activeNav.classList.add('active');
        hiddenNav.classList.remove('active');
        
        hiddenSec.classList.remove('active-section');
        hiddenSec.classList.add('hidden-section');
        
        activeSec.classList.remove('hidden-section');
        activeSec.classList.add('active-section');
    }

    navChat.addEventListener('click', () => switchTab(navChat, chatSection, navHistory, historySection));
    navHistory.addEventListener('click', () => {
        switchTab(navHistory, historySection, navChat, chatSection);
        loadHistory();
    });

    // --- Chat functionality ---
    const chatBox = document.getElementById('chat-box');
    const symptomInput = document.getElementById('symptom-input');
    const sendBtn = document.getElementById('send-btn');

    function appendUserMessage(text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message user-message';
        msgDiv.innerHTML = `
            <div class="avatar"><i class="fa-solid fa-user"></i></div>
            <div class="message-content"><p>${text}</p></div>
        `;
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function appendBotMessage(responseObj) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message bot-message';
        
        let contentHTML = `<p>${responseObj.bot_response || 'No response.'}</p>`;
        
        if (responseObj.predictions && responseObj.predictions.length > 0) {
            responseObj.predictions.forEach(pred => {
                const probPercent = (pred.probability * 100).toFixed(1);
                contentHTML += `
                    <div class="prediction-card">
                        <span class="prob">${probPercent}%</span>
                        <h4>${pred.disease}</h4>
                        <p>${pred.description}</p>
                        <ul class="suggestion-list">
                            <li><strong>Precautions:</strong> ${pred.precautions}</li>
                            <li><strong>Medications:</strong> ${pred.medications}</li>
                            <li><strong>Doctor says:</strong> ${pred.doctor_recommendation}</li>
                        </ul>
                    </div>
                `;
            });
        }

        msgDiv.innerHTML = `
            <div class="avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="message-content">${contentHTML}</div>
        `;
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    async function handleSend() {
        if(!token) return;
        const text = symptomInput.value.trim();
        if (!text) return;

        appendUserMessage(text);
        symptomInput.value = '';

        try {
            const botTyping = document.createElement('div');
            botTyping.className = 'message bot-message';
            botTyping.id = 'typing-indicator';
            botTyping.innerHTML = `<div class="avatar"><i class="fa-solid fa-robot"></i></div><div class="message-content"><p>...</p></div>`;
            chatBox.appendChild(botTyping);
            chatBox.scrollTop = chatBox.scrollHeight;

            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify({ symptoms: text })
            });

            if (res.status === 401) {
                logoutBtn.click();
                return;
            }

            const data = await res.json();
            
            chatBox.removeChild(botTyping);

            if (res.ok) {
                appendBotMessage(data);
            } else {
                appendBotMessage({ bot_response: "Error: " + (data.detail || "Something went wrong.") });
            }
        } catch (err) {
            const typingInd = document.getElementById('typing-indicator');
            if(typingInd) chatBox.removeChild(typingInd);
            appendBotMessage({ bot_response: "Could not connect to the server." });
        }
    }

    sendBtn.addEventListener('click', handleSend);
    symptomInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSend();
    });

    // --- Voice Input Logic ---
    const micBtn = document.getElementById('mic-btn');
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;
    let isListening = false;

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onstart = function() {
            isListening = true;
            micBtn.classList.remove('mic-idle');
            micBtn.classList.add('mic-listening');
            symptomInput.placeholder = "Listening...";
        };

        recognition.onresult = function(event) {
            let final_transcript = '';
            let interim_transcript = '';

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    final_transcript += event.results[i][0].transcript;
                } else {
                    interim_transcript += event.results[i][0].transcript;
                }
            }
            symptomInput.value = final_transcript + interim_transcript;
        };

        recognition.onerror = function(event) {
            console.error(event);
            resetMic();
        };

        recognition.onend = function() {
            resetMic();
            // Optional auto-send when speech ends
            // if (symptomInput.value.trim().length > 0) {
            //     handleSend();
            // }
        };

        micBtn.addEventListener('click', () => {
            if (isListening) {
                recognition.stop();
            } else {
                symptomInput.value = '';
                recognition.start();
            }
        });
    } else {
        // Browser does not support SpeechRecognition
        micBtn.style.display = 'none';
        console.warn("Speech API not supported in this browser.");
    }

    function resetMic() {
        isListening = false;
        micBtn.classList.remove('mic-listening');
        micBtn.classList.add('mic-idle');
        symptomInput.placeholder = "E.g., I have a severe headache, fever...";
    }

    // --- History functionality ---
    const historyList = document.getElementById('history-list');
    const refreshHistoryBtn = document.getElementById('refresh-history');

    refreshHistoryBtn.addEventListener('click', loadHistory);

    async function loadHistory() {
        if(!token) return;
        historyList.innerHTML = '<p>Loading history...</p>';
        try {
            const res = await fetch('/api/history', { headers: getAuthHeaders() });
            
            if (res.status === 401) {
                logoutBtn.click();
                return;
            }

            const data = await res.json();
            
            if (res.ok) {
                historyList.innerHTML = '';
                if (data.history.length === 0) {
                    historyList.innerHTML = '<p>No history found.</p>';
                    return;
                }
                
                data.history.forEach(item => {
                    const d = new Date(item.timestamp + 'Z');
                    const dateStr = d.toLocaleString();
                    
                    let predsHtml = '';
                    item.predictions.forEach(p => {
                        predsHtml += `<li><strong>${p.disease}</strong> (${(p.probability*100).toFixed(1)}%)</li>`;
                    });

                    const itemDiv = document.createElement('div');
                    itemDiv.className = 'history-item';
                    itemDiv.innerHTML = `
                        <span class="date">${dateStr}</span>
                        <div class="entered-symptoms">" ${item.symptoms_text} "</div>
                        <ul>${predsHtml}</ul>
                    `;
                    historyList.appendChild(itemDiv);
                });
            } else {
                historyList.innerHTML = `<p>Error loading history.</p>`;
            }
        } catch (err) {
            historyList.innerHTML = `<p>Cannot connect to server.</p>`;
        }
    }
});
