import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const App = () => {
  const [userInput, setUserInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (e) => {
    setUserInput(e.target.value);
  };

  const formatBotResponse = (text) => {
    return text.split('\n\n').map((line, index) => ({
      text: line,
      isBot: true,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) return;

    setMessages([...messages, { text: userInput, isBot: false }]);
    setIsLoading(true);
    setUserInput('');

    const modifiedUserInput = `${userInput} in DevOps`;

    try {
      const response = await axios.post(
        'https://chatbot-deployment-e3gg.vercel.app/process',
        { text: modifiedUserInput }
      );

      const botMessage = response.data.generated_text || 'Sorry, I could not understand that.';
      const formattedBotResponse = formatBotResponse(botMessage);

      setMessages([...messages, { text: userInput, isBot: false }, ...formattedBotResponse]);
    } catch (error) {
      console.error('Error while sending request:', error);
      setMessages([...messages, { text: userInput, isBot: false }, { text: 'Error: Could not connect to the server.', isBot: true }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>Welcome To IntelliSwift DevOps Bot</h2>
      </div>
      <div className="chat-box">
        <div className="messages">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`message ${msg.isBot ? 'bot-message' : 'user-message'}`}
            >
              {msg.text}
            </div>
          ))}
        </div>
        {isLoading && <div className="loading">...</div>}
      </div>
      <form onSubmit={handleSubmit} className="chat-input-form">
        <input
          type="text"
          value={userInput}
          onChange={handleInputChange}
          placeholder="Ask something..."
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
};

export default App;
