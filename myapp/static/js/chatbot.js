document.addEventListener('DOMContentLoaded', function() {
    const chatBtn = document.getElementById('chat-widget-btn');
    const chatWindow = document.getElementById('chat-window');
    const closeChat = document.getElementById('close-chat');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const messagesContainer = document.getElementById('chat-messages');
    const typingIndicator = document.getElementById('typing-indicator');

    // Toggle chat window
    chatBtn.addEventListener('click', () => {
        chatWindow.classList.add('active');
        // Focus input when opened
        setTimeout(() => chatInput.focus(), 300);
    });

    closeChat.addEventListener('click', () => {
        chatWindow.classList.remove('active');
    });

    // Send message on Enter key
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    sendBtn.addEventListener('click', sendMessage);

    function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        // Add user message
        addMessage(message, 'user');
        chatInput.value = '';
        
        // Show typing indicator
        typingIndicator.style.display = 'block';
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // Call API
        fetch('/api/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            typingIndicator.style.display = 'none';
            if (data.error) {
                addMessage('Error: ' + data.error, 'bot');
            } else {
                addMessage(data.response, 'bot');
            }
        })
        .catch(error => {
            typingIndicator.style.display = 'none';
            addMessage('Sorry, something went wrong. Please try again.', 'bot');
            console.error('Error:', error);
        });
    }

    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        
        // Convert newlines to breaks for bot messages
        if (sender === 'bot') {
            // Simple markdown-like parsing for bold text
            let formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            formattedText = formattedText.replace(/\n/g, '<br>');
            messageDiv.innerHTML = formattedText;
        } else {
            messageDiv.textContent = text;
        }
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
});
