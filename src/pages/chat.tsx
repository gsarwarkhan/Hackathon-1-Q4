import React, { useState, useRef, useEffect } from 'react';
import Layout from '@theme/Layout';
import styles from './chat.module.css';
import { chatWithAI } from '../api';

export default function Chat() {
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState([
        {
            sender: 'system',
            text: 'Welcome to the AI Assistant! Ask me anything about Physical AI & Humanoid Robotics.'
        }
    ]);
    const [loading, setLoading] = useState(false);
    const [sessionId, setSessionId] = useState(null);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const askAI = async () => {
        if (!input.trim() || loading) return;

        const currentInput = input;
        setInput('');
        setMessages(prev => [...prev, { sender: 'user', text: currentInput }]);
        setLoading(true);

        try {
            const { response, session_id } = await chatWithAI(currentInput, sessionId);
            if (session_id) setSessionId(session_id);
            setMessages(prev => [...prev, { sender: 'ai', text: response }]);
        } catch (error) {
            console.error('Chat error:', error);
            setMessages(prev => [...prev, {
                sender: 'system',
                text: `Error: ${error.message}`
            }]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            askAI();
        }
    };

    return (
        <Layout
            title="AI Assistant"
            description="Ask questions about Physical AI & Humanoid Robotics">
            <div className={styles.chatPage}>
                <div className={styles.chatContainer}>
                    <div className={styles.chatHeader}>
                        <h2>AI Assistant</h2>
                        <p>Ask me anything about the textbook content</p>
                    </div>

                    <div className={styles.messagesArea}>
                        {messages.map((msg, index) => (
                            <div
                                key={index}
                                className={`${styles.message} ${styles[msg.sender + 'Message']}`}
                            >
                                {msg.text}
                            </div>
                        ))}
                        {loading && (
                            <div className={`${styles.message} ${styles.aiMessage}`}>
                                <span className={styles.thinkingIndicator}>Thinking...</span>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    <div className={styles.inputArea}>
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyPress={handleKeyPress}
                            placeholder="Type your question here..."
                            disabled={loading}
                            className={styles.input}
                        />
                        <button
                            onClick={askAI}
                            disabled={loading || !input.trim()}
                            className={styles.sendButton}
                        >
                            {loading ? 'Sending...' : 'Send'}
                        </button>
                    </div>
                </div>
            </div>
        </Layout>
    );
}
