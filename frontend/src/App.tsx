import { useState, useRef } from 'react';
import './App.css';

type Message = {
  sender: 'user' | 'llm';
  text: string;
};

function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const sendMessage = async () => {
    const prompt = input.trim();
    if (!prompt) return;
    setMessages((msgs) => [...msgs, { sender: 'user', text: prompt }]);
    setInput('');
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
      });
      const data = await res.json();
      setMessages((msgs) => [...msgs, { sender: 'llm', text: data.response }]);
    } catch (e) {
      setMessages((msgs) => [...msgs, { sender: 'llm', text: '[Error: Could not reach backend]' }]);
    }
    setLoading(false);
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !loading) {
      sendMessage();
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: '0 auto', padding: 24 }}>
      <h1>LLM Chat (MVP)</h1>
      <div style={{
        border: '1px solid #444',
        borderRadius: 8,
        minHeight: 300,
        padding: 16,
        marginBottom: 16,
        background: '#181818',
        overflowY: 'auto',
        maxHeight: 400
      }}>
        {messages.length === 0 && <div style={{ color: '#888' }}>Start the conversation...</div>}
        {messages.map((msg, i) => (
          <div key={i} style={{
            textAlign: msg.sender === 'user' ? 'right' : 'left',
            margin: '8px 0'
          }}>
            <span style={{
              display: 'inline-block',
              background: msg.sender === 'user' ? '#646cff22' : '#222',
              color: msg.sender === 'user' ? '#fff' : '#b3e5fc',
              borderRadius: 8,
              padding: '8px 12px',
              maxWidth: '80%',
              wordBreak: 'break-word'
            }}>
              <b>{msg.sender === 'user' ? 'You' : 'Agent'}:</b> {msg.text}
            </span>
          </div>
        ))}
        {loading && (
          <div style={{ color: '#888', margin: '8px 0' }}>LLM is typing...</div>
        )}
      </div>
      <div style={{ display: 'flex', gap: 8 }}>
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          style={{ flex: 1, padding: 8, borderRadius: 4, border: '1px solid #444', background: '#222', color: '#fff' }}
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading || !input.trim()} style={{ padding: '8px 16px' }}>
          Send
        </button>
      </div>
    </div>
  );
}

export default App;
