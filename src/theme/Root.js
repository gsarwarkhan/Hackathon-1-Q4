import React, { useState } from 'react';
import styles from './chat.module.css';

export default function Root({children}) {
  const [input, setInput] = useState("");
  const [answer, setAnswer] = useState("");

  const askAI = async () => {
    try {
      const fetchUrl = "http://localhost:8000/ask"; // Absolute URL
      console.log(`[Frontend] Attempting to fetch from: ${fetchUrl}`);

      const res = await fetch(fetchUrl, {
        method: "POST", // Correct method
        headers: { 
          "Content-Type": "application/json" // Correct header
        },
        body: JSON.stringify({ question: input, user_context: "" }) // Correct JSON body
      });

      console.log(`[Frontend] Fetch response status: ${res.status}`); // Log status BEFORE json()

      if (!res.ok) { // Check if response status is 2xx
        // Attempt to parse error as JSON, fallback to statusText
        const errorData = await res.json().catch(() => ({ message: res.statusText || 'Unknown error during JSON parse' }));
        console.error(`[Frontend] Fetch failed with status ${res.status}:`, errorData);
        setAnswer(`Error: ${errorData.detail || errorData.message || 'Unknown error'}`);
        return;
      }

      const data = await res.json(); // Correct JSON handling
      console.log("[Frontend] Received data:", data);
      setAnswer(data.answer); // Set answer
    } catch (error) {
      console.error("[Frontend] Uncaught fetch error:", error); // Proper error handling
      setAnswer(`Failed to connect to backend: ${error.message || 'Network error'}. Check console for details.`);
    }
  };

  return (
    <>
      {children}
      <div className={styles.chatContainer}>
        <div className={styles.chatBox}>
          <p>{answer || "Ask me anything about the textbook..."}</p>
          <input value={input} onChange={(e) => setInput(e.target.value)} />
          <button onClick={askAI}>Ask AI</button>
        </div>
      </div>
    </>
  );
}