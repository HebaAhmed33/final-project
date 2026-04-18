export default function PageContainer({ title, subtitle, children }) {
  return (
    <div style={{ padding: "2rem 3rem", width: "100%", maxWidth: "1200px", margin: "0 auto" }}>
      <div style={{ marginBottom: "2rem" }}>
        {title && (
          <h1
            style={{
              fontSize: "1.875rem",
              fontWeight: 700,
              color: "var(--text-main)",
              letterSpacing: "-0.02em",
              marginBottom: "0.25rem",
            }}
          >
            {title}
          </h1>
        )}
        {subtitle && (
          <p style={{ color: "var(--text-muted)", fontSize: "0.95rem" }}>
            {subtitle}
          </p>
        )}
      </div>
      {children}
    </div>
  );
}
