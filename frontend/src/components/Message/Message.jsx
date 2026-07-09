import styles from "./Message.module.css";

export default function Message({ role, content }) {
  const isUser = role === "user";
  return (
    <div className={`${styles.row} ${isUser ? styles.rowUser : styles.rowAssistant}`}>
      <div className={`${styles.bubble} ${isUser ? styles.userBubble : styles.assistantBubble}`}>
        {content}
      </div>
    </div>
  );
}
