# Placeholder CSS and HTML templates for bot and user messages
css = '''
<style>
body {
    background-color: #f8f9fa;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
header {
    background-color: #ffffff;
    padding: 1rem;
    border-bottom: 1px solid #e0e0e0;
}
.sidebar .sidebar-content {
    background-color: #ffffff;
    padding: 1rem;
    border-right: 1px solid #e0e0e0;
}
.chat-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 1rem;
    background-color: #ffffff;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
.chat-input {
    display: flex;
    align-items: center;
    padding: 0.5rem;
    background-color: #f1f1f1;
    border-radius: 50px;
    margin-top: 1rem;
}
.chat-input input {
    flex-grow: 1;
    border: none;
    outline: none;
    background: transparent;
    padding: 0.5rem;
    font-size: 1rem;
    border-radius: 25px;
}
.chat-input button {
    border: none;
    background: #6200ee;
    color: #ffffff;
    padding: 0.5rem 1rem;
    border-radius: 50px;
    cursor: pointer;
    transition: background 0.3s ease;
    margin-left: 10px;
}
.chat-input button:hover {
    background: #4500b5;
}
.chat-message {
    display: flex;
    align-items: flex-start;
    margin-bottom: 1rem;
}
.chat-message.user {
    justify-content: flex-end;
}
.chat-message.bot {
    justify-content: flex-start;
}
.chat-message .message {
    max-width: 70%;
    padding: 1rem;
    border-radius: 10px;
    color: #ffffff;
}
.chat-message.user .message {
    background-color: #6200ee;
}
.chat-message.bot .message {
    background-color: #e0e0e0;
    color: #000000;
}
.chat-message .avatar {
    margin: 0 1rem;
}
.chat-message.user .avatar {
    order: 2;
}
.chat-message.bot .avatar {
    order: 1;
}
.chat-message .avatar img {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: cover;
}
</style>
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="images/bot-ai.png" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="https://i.ibb.co/rdZC7LZ/Photo-logo-1.png" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;">
    </div>    
    <div class="message">{{MSG}}</div>
</div>
'''