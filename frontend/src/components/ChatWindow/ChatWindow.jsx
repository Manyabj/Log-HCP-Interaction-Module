import { useState, useRef, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";

import { sendMessage, addLocalUserMessage } from "../../redux/slices/chatSlice";
import Message from "../Message/Message";
import styles from "./ChatWindow.module.css";

const SUGGESTIONS = [
  "Today I met Dr. Smith and discussed Product X. He was positive and I shared a brochure.",
  "Actually the doctor was Dr. John and the sentiment was negative.",
  "Remove the brochures.",
  "Summarize this interaction.",
  "Save this interaction.",
];

export default function ChatWindow({ sessionId }) {
  const dispatch = useDispatch();
  const { messages, loading, error } = useSelector((s) => s.chat);
  const [input, setInput] = useState("");
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = (text) => {
    const trimmed = (text ?? input).trim();
    if (!trimmed || loading) return;
    dispatch(addLocalUserMessage(trimmed));
    dispatch(sendMessage({ sessionId, message: trimmed }));
    setInput("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className={styles.chatContainer}>
      <div className={styles.chatHeader}>
        <h2>AI Assistant</h2>
        <p>Describe the interaction in plain English — the form updates automatically.</p>
      </div>

      <div className={styles.messages} ref={scrollRef}>
        {messages.length === 0 && (
          <div className={styles.emptyState}>
            <p>Try one of these to get started:</p>
            <div className={styles.suggestions}>
              {SUGGESTIONS.map((s, i) => (
                <button key={i} className={styles.suggestionChip} onClick={() => handleSend(s)}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, idx) => (
          <Message key={idx} role={m.role} content={m.content} />
        ))}

        {loading && (
          <div className={styles.typingIndicator}>
            <span></span><span></span><span></span>
          </div>
        )}

        {error && <div className={styles.errorBanner}>{error}</div>}
      </div>

      <div className={styles.inputBar}>
        <textarea
          className={styles.textarea}
          placeholder="e.g. Today I met Dr. Smith and discussed Product X..."
          value={input}
          rows={2}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button
          className={styles.sendButton}
          onClick={() => handleSend()}
          disabled={loading || !input.trim()}
        >
          Send
        </button>
      </div>
    </div>
  );
}
