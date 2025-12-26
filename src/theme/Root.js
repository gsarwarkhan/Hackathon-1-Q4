import React, { useState, useRef, useEffect } from 'react';
import styles from './chat.module.css';
import { chatWithAI } from '../api'; // Import the new API client

// The initial message to display in the chat
const initialMessage = { 
  sender: 'system', 
  text: "Ask me anything about the textbook..." 
};

export default function Root({children}) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([initialMessage]); 
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null); 
  const messagesEndRef = useRef(null);

  // Function to scroll to the latest message
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Scroll to bottom whenever messages update
  useEffect(() => {
    scrollToBottom();
  }, [messages]); // Only scroll when messages array changes

  const askAI = async () => {
    if (!input.trim()) return;

    const newUserMessage = { sender: 'user', text: input };
    setMessages(prev => [...prev, newUserMessage]);
    
    const currentInput = input; 
    setInput(""); 
    setLoading(true);

    try {
      const { response: aiResponseText, session_id: newSessionId } = await chatWithAI(currentInput, sessionId);
      setSessionId(newSessionId); 
      setMessages(prev => [...prev, { sender: 'ai', text: aiResponseText }]);
    } catch (error) {
      console.error("Frontend API call failed:", error); // Log detailed error
      setMessages(prev => [...prev, { sender: 'system', text: `Error: ${error.message || 'Network error'}. Please try again.` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {children}
      <div className={styles.chatContainer}>
        <div className={styles.chatBox}>
          <div className={styles.messageContainer}>
            {messages.map((msg, index) => (
              <div key={index} className={`${styles.message} ${styles[msg.sender]}`}>
                <p>{msg.text}</p>
              </div>
            ))}
            {loading && (
              <div className={`${styles.message} ${styles.ai}`}>
                <p><span className={styles.thinkingIndicator}>Thinking...</span></p>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          <input 
            value={input} 
            onChange={(e) => setInput(e.target.value)} 
            onKeyPress={(e) => e.key === 'Enter' && askAI()}
            placeholder="Type your message..."
          />
          <button onClick={askAI} disabled={loading}>
            {loading ? "..." : "Ask"}
          </button>
        </div>
      </div>
    </>
  );
}