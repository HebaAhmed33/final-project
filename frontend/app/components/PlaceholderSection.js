export default function PlaceholderSection({ title, description }) {
  return (
    <div
      style={{
        border: "1px dashed var(--border)",
        borderRadius: "8px",
        padding: "1.25rem",
        marginBottom: "1rem",
        background: "var(--bg-card)",
      }}
    >
      <h3
        style={{
          fontSize: "1rem",
          fontWeight: 600,
          marginBottom: "0.35rem",
        }}
      >
        {title}
      </h3>
      <p style={{ color: "var(--text-muted)", fontSize: "0.875rem", margin: 0 }}>
        {description || "Coming soon."}
      </p>
    </div>
  );
}
