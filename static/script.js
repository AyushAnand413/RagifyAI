const chatBox = document.getElementById("chat-box");
const inputField = document.getElementById("query");
const loadingIndicator = document.getElementById("loading-indicator");
const sendBtn = document.getElementById("send-btn");

// Handle Enter Key
inputField.addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        sendQuery();
    }
});

async function sendQuery() {
    const query = inputField.value.trim();
    if (!query) return;

    // 1. Remove Welcome Message if it exists
    const welcome = document.querySelector(".welcome-message");
    if (welcome) welcome.remove();

    // 2. Add User Message
    addMessage(query, "user");
    inputField.value = "";
    inputField.disabled = true; // Disable input while processing

    // 3. Show Loading
    loadingIndicator.classList.remove("hidden");
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query })
        });

        const data = await response.json();

        // 4. Hide Loading
        loadingIndicator.classList.add("hidden");

        // 5. Render Response
        if (data.action) {
            addActionCard(data);
        } else {
            addMessage(data.answer, "bot", data.page);
        }

    } catch (error) {
        loadingIndicator.classList.add("hidden");
        addMessage("Error: Could not connect to the agent.", "bot");
    } finally {
        inputField.disabled = false;
        inputField.focus();
    }
}

function addMessage(text, sender, page = null) {
    const isUser = sender === "user";
    const avatarIcon = isUser ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-robot"></i>';
    const rowClass = isUser ? "user-row" : "bot-row";
    const bubbleClass = isUser ? "user-bubble" : "bot-bubble";

    let content = text;
    // Add citation if available
    if (page) {
        content += `<br><span class="source-tag"><i class="fa-regular fa-file-pdf"></i> Page ${page}</span>`;
    }

    const html = `
    <div class="message-row ${rowClass}">
        <div class="avatar ${sender}-avatar">${avatarIcon}</div>
        <div class="message-bubble ${bubbleClass}">${content}</div>
    </div>`;

    chatBox.insertAdjacentHTML('beforeend', html);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function addActionCard(data) {
    // Pretty print JSON
    const jsonStr = JSON.stringify(data, null, 2);
    
    const html = `
    <div class="message-row bot-row">
        <div class="avatar bot-avatar"><i class="fa-solid fa-bolt"></i></div>
        <div class="message-bubble bot-bubble" style="width: 100%;">
            <b>⚡ Action Triggered</b>
            <div class="action-card">
                <div class="action-header">
                    <span>${data.action}</span>
                    <i class="fa-solid fa-check-circle"></i>
                </div>
                <div class="action-body">${jsonStr}</div>
            </div>
        </div>
    </div>`;

    chatBox.insertAdjacentHTML('beforeend', html);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function clearChat() {
    chatBox.innerHTML = `
        <div class="welcome-message">
            <div class="welcome-icon"><i class="fa-solid fa-layer-group"></i></div>
            <h2>Enterprise Agent Ready</h2>
            <p>Chat history cleared.</p>
        </div>`;
}