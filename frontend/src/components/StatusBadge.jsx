export default function StatusBadge({ status }) {
  if (!status) return null;

  const className = status.toLowerCase().replaceAll("_", "-");

  return (
    <span className={`badge status-badge status-${className}`}>
      {status.replaceAll("_", " ")}
    </span>
  );
}
