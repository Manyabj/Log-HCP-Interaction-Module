import { useSelector } from "react-redux";
import styles from "./InteractionForm.module.css";

function ReadOnlyField({ label, value, badge }) {
  const isEmpty = value === null || value === undefined || value === "" ||
    (Array.isArray(value) && value.length === 0);

  return (
    <div className={styles.field}>
      <label className={styles.label}>{label}</label>
      <div className={`${styles.value} ${isEmpty ? styles.empty : ""}`}>
        {isEmpty ? (
          "Not captured yet"
        ) : Array.isArray(value) ? (
          <div className={styles.chipRow}>
            {value.map((item, idx) => (
              <span key={idx} className={styles.chip}>{item}</span>
            ))}
          </div>
        ) : (
          value
        )}
        {badge && !isEmpty && (
          <span className={`${styles.sentimentBadge} ${styles[badge.toLowerCase()] || ""}`}>
            {badge}
          </span>
        )}
      </div>
    </div>
  );
}

export default function InteractionForm() {
  const { fields, isValidForSave, missingFields, saved } = useSelector((s) => s.interaction);

  return (
    <div className={styles.formContainer}>
      <div className={styles.formHeader}>
        <h2>Interaction Details</h2>
        <span className={`${styles.statusPill} ${styles[fields.status] || ""}`}>
          {saved ? "Saved" : fields.status === "validated" ? "Ready to save" : "Draft"}
        </span>
      </div>

      <p className={styles.helperText}>
        This form is populated automatically by the AI Assistant. Describe the interaction
        in the chat on the right — nothing here is manually editable.
      </p>

      <div className={styles.grid}>
        <ReadOnlyField label="HCP Name" value={fields.hcp_name} />
        <ReadOnlyField label="Interaction Type" value={fields.interaction_type} />
        <ReadOnlyField label="Date" value={fields.interaction_date} />
        <ReadOnlyField label="Time" value={fields.interaction_time} />
        <ReadOnlyField label="Attendees" value={fields.attendees} />
        <ReadOnlyField label="Product" value={fields.product} />
        <ReadOnlyField label="Topics Discussed" value={fields.topics} />
        <ReadOnlyField label="Sentiment" value={fields.sentiment} badge={fields.sentiment} />
        <ReadOnlyField label="Materials Shared" value={fields.materials} />
        <ReadOnlyField label="Notes" value={fields.notes} />
        <ReadOnlyField label="AI Summary" value={fields.summary} />
      </div>

      {missingFields.length > 0 && !saved && (
        <div className={styles.missingBanner}>
          Missing before saving: {missingFields.join(", ")}
        </div>
      )}

      {saved && <div className={styles.savedBanner}>Interaction saved successfully.</div>}
    </div>
  );
}
