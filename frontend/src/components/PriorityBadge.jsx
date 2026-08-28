export default function PriorityBadge({ priority }) {
  if (!priority) return null;

  return (
    <span className={`badge priority-badge priority-${priority.toLowerCase()}`}>
      Priority {priority}
    </span>
  );
}
