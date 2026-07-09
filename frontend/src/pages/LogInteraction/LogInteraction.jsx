import { useEffect, useMemo } from "react";
import { useDispatch, useSelector } from "react-redux";
import { v4 as uuidv4 } from "uuid";

import InteractionForm from "../../components/InteractionForm/InteractionForm";
import ChatWindow from "../../components/ChatWindow/ChatWindow";
import { loadInteraction, submitInteraction, resetInteraction } from "../../redux/slices/interactionSlice";
import styles from "./LogInteraction.module.css";

function getSessionId() {
  let sessionId = sessionStorage.getItem("hcp_session_id");
  if (!sessionId) {
    sessionId = uuidv4();
    sessionStorage.setItem("hcp_session_id", sessionId);
  }
  return sessionId;
}

export default function LogInteraction() {
  const dispatch = useDispatch();
  const sessionId = useMemo(getSessionId, []);
  const { fields, isValidForSave, saving, saved, error } = useSelector((s) => s.interaction);

  useEffect(() => {
    dispatch(loadInteraction(sessionId));
  }, [dispatch, sessionId]);

  const handleSave = () => {
    dispatch(submitInteraction(sessionId));
  };

  const handleNewInteraction = () => {
    sessionStorage.removeItem("hcp_session_id");
    dispatch(resetInteraction());
    window.location.reload();
  };

  return (
    <div className={styles.page}>
      <header className={styles.topBar}>
        <div>
          <h1>Log HCP Interaction</h1>
          <p>AI-first entry — the form on the left is populated entirely by the chat on the right.</p>
        </div>
        <div className={styles.actions}>
          {saved ? (
            <button className={styles.secondaryButton} onClick={handleNewInteraction}>
              Log Another Interaction
            </button>
          ) : (
            <button
              className={styles.primaryButton}
              onClick={handleSave}
              disabled={!isValidForSave || saving}
            >
              {saving ? "Saving..." : "Save Interaction"}
            </button>
          )}
        </div>
      </header>

      {error && <div className={styles.errorBar}>{error}</div>}

      <div className={styles.splitScreen}>
        <div className={styles.leftPanel}>
          <InteractionForm />
        </div>
        <div className={styles.rightPanel}>
          <ChatWindow sessionId={sessionId} />
        </div>
      </div>
    </div>
  );
}
