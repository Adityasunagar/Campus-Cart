// Initialize Socket.IO connection
const socket = io();

let currentRecipientId = null;
let currentUserId = null;

// On page load, join the chat room and get current user ID
document.addEventListener('DOMContentLoaded', function () {
    const recipientInput = document.getElementById('recipientId');
    const userIdInput = document.getElementById('currentUserId');
    
    if (userIdInput && userIdInput.value) {
        currentUserId = parseInt(userIdInput.value);
    }
    
    if (recipientInput && recipientInput.value) {
        currentRecipientId = parseInt(recipientInput.value);
        
        // Join the chat room
        socket.emit('join_chat', { recipient_id: currentRecipientId });
    }

    // Auto scroll to bottom
    const container = document.getElementById("chat-messages-container");
    if (container) {
        container.scrollTop = container.scrollHeight;
    }

    // Auto resize textarea
    const tx = document.getElementsByTagName("textarea");
    for (let i = 0; i < tx.length; i++) {
        tx[i].setAttribute("style", tx[i].getAttribute("style") + "overflow-y:hidden;");
        tx[i].addEventListener("input", OnInput, false);
    }
    
    function OnInput() {
        this.style.height = 0;
        this.style.height = (this.scrollHeight) + "px";
    }

    // Search contacts
    const searchInput = document.getElementById('contactSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function () {
            const q = this.value.toLowerCase();
            document.querySelectorAll('.chat-partner').forEach(li => {
                const name = li.textContent.toLowerCase();
                li.style.display = name.includes(q) ? '' : 'none';
            });
        });
    }
});

// Prevent form reload and send via WebSocket
document.addEventListener('DOMContentLoaded', function () {
    const chatForm = document.getElementById("chatForm");
    if (chatForm) {
        chatForm.addEventListener("submit", function (e) {
            e.preventDefault();
            sendMessage();
        });
    }
});

function sendMessage() {
    let input = document.getElementById("msgInput");
    let msg = input.value.trim();

    if (msg === "" || !currentRecipientId) return;

    // Send via WebSocket
    socket.emit("send_message", { 
        content: msg,
        recipient_id: currentRecipientId
    });

    input.value = "";
    input.style.height = "auto"; // Reset textarea height
}

// Receive message from WebSocket
socket.on("receive_message", function (data) {
    const box = document.getElementById("chat-messages-container");
    if (!box) return;

    // Only display if message is for current conversation
    if (data.recipient_id !== currentRecipientId && data.sender_id !== currentRecipientId) {
        return;
    }

    // Create message element
    const div = document.createElement("div");
    // Determine if message is from current user (sent) or from recipient (received)
    const isFromCurrentUser = data.sender_id === currentUserId;
    
    div.className = isFromCurrentUser ? "message-bubble sent" : "message-bubble received";
    
    const timeStr = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
    const checkIcon = isFromCurrentUser ? '<i class="fas fa-check-double" style="font-size: 0.65rem;"></i>' : '';
    
    div.innerHTML = `
        ${data.content}
        <div class="time" style="font-size: 0.7rem; margin-top: 0.4rem; text-align: right; opacity: 0.6; display: flex; justify-content: flex-end; align-items: center; gap: 4px;">
            ${timeStr}
            ${checkIcon}
        </div>
    `;

    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
});

// Handle connection events
socket.on("connect", function () {
    console.log("Connected to chat server");
});

socket.on("disconnect", function () {
    console.log("Disconnected from chat server");
});

socket.on("error", function (data) {
    console.error("Chat error:", data);
});

socket.on("status", function (data) {
    console.log("Status:", data.message);
});