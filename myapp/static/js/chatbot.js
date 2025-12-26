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
        setTimeout(() => chatInput.focus(), 300);
    });

    closeChat.addEventListener('click', () => {
        chatWindow.classList.remove('active');
    });

    // Send message on Enter key
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    sendBtn.addEventListener('click', sendMessage);

    // Quick action buttons
    document.querySelectorAll('.quick-action').forEach(btn => {
        btn.addEventListener('click', () => {
            chatInput.value = btn.dataset.prompt;
            sendMessage();
        });
    });

    function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        // Add user message
        addMessage(message, 'user');
        chatInput.value = '';
        
        // Show typing indicator
        typingIndicator.style.display = 'block';
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // Disable input while waiting
        chatInput.disabled = true;
        sendBtn.disabled = true;

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
            chatInput.disabled = false;
            sendBtn.disabled = false;
            chatInput.focus();
            
            if (data.error) {
                addMessage('Error: ' + data.error, 'bot');
            } else {
                addMessage(data.response, 'bot');
            }
        })
        .catch(error => {
            typingIndicator.style.display = 'none';
            chatInput.disabled = false;
            sendBtn.disabled = false;
            addMessage('Sorry, something went wrong. Please try again.', 'bot');
            console.error('Error:', error);
        });
    }

    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        
        if (sender === 'bot') {
            // Parse markdown-style formatting
            let formattedText = formatBotMessage(text);
            messageDiv.innerHTML = formattedText;
            
            // Add copy buttons to code blocks after rendering
            setTimeout(() => {
                messageDiv.querySelectorAll('.code-block').forEach(block => {
                    addCopyButton(block);
                });
            }, 0);
        } else {
            messageDiv.textContent = text;
        }
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function formatBotMessage(text) {
        // Handle code blocks with language tags ```python ... ```
        text = text.replace(/```(\w+)?\n?([\s\S]*?)```/g, (match, lang, code) => {
            const language = lang || 'code';
            const escapedCode = escapeHtml(code.trim());
            return `<div class="code-block" data-lang="${language}">
                <div class="code-header">
                    <span class="code-lang">${language}</span>
                </div>
                <pre><code>${escapedCode}</code></pre>
            </div>`;
        });
        
        // Handle inline code `code`
        text = text.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');
        
        // Handle bold **text**
        text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        
        // Handle italic *text*
        text = text.replace(/\*([^*]+)\*/g, '<em>$1</em>');
        
        // Handle headers
        text = text.replace(/^### (.+)$/gm, '<h4 class="chat-heading">$1</h4>');
        text = text.replace(/^## (.+)$/gm, '<h3 class="chat-heading">$1</h3>');
        
        // Handle bullet points
        text = text.replace(/^[-•] (.+)$/gm, '<li>$1</li>');
        text = text.replace(/(<li>.*<\/li>\n?)+/g, '<ul class="chat-list">$&</ul>');
        
        // Handle numbered lists
        text = text.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');
        
        // Handle line breaks
        text = text.replace(/\n/g, '<br>');
        
        // Clean up extra breaks around block elements
        text = text.replace(/<br>\s*(<div|<ul|<h[34])/g, '$1');
        text = text.replace(/(<\/div>|<\/ul>|<\/h[34]>)\s*<br>/g, '$1');
        
        return text;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function addCopyButton(block) {
        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-code-btn';
        copyBtn.innerHTML = '📋 Copy';
        copyBtn.onclick = () => {
            const code = block.querySelector('code').textContent;
            navigator.clipboard.writeText(code).then(() => {
                copyBtn.innerHTML = '✓ Copied!';
                setTimeout(() => {
                    copyBtn.innerHTML = '📋 Copy';
                }, 2000);
            });
        };
        block.querySelector('.code-header').appendChild(copyBtn);
    }
});
