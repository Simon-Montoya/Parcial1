import StatusBadge from "./StatusBadge";


function compactId(id) {
  if (!id || id.length < 17) return id;
  return `${id.slice(0, 8)}…${id.slice(-5)}`;
}


function formatTime(timestamp) {
  if (!timestamp) return "Just now";

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(timestamp));
}


export default function NotificationPanel({ notifications }) {
  return (
    <section className="panel notification-panel" aria-live="polite">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Live activity</span>
          <h2>Recent Notifications</h2>
        </div>
        <span className="live-indicator">Live</span>
      </div>

      {notifications.length === 0 ? (
        <div className="empty-state">
          <strong>No recent notifications</strong>
          <p>New operational updates will appear here automatically.</p>
        </div>
      ) : (
        <ol className="notification-list">
          {notifications.map((notification) => {
            const operationalStatus =
              notification.payload?.status ?? notification.status;

            return (
              <li key={notification.id}>
                <div className="notification-list__top">
                  <strong>
                    {notification.event_type
                      ?.replaceAll("_", " ") ?? "Emergency update"}
                  </strong>
                  <time dateTime={notification.created_at}>
                    {formatTime(notification.created_at)}
                  </time>
                </div>
                <p>{notification.message}</p>
                <div className="notification-list__meta">
                  {notification.emergency_id && (
                    <code title={notification.emergency_id}>
                      Emergency {compactId(notification.emergency_id)}
                    </code>
                  )}
                  <StatusBadge status={operationalStatus} />
                </div>
              </li>
            );
          })}
        </ol>
      )}
    </section>
  );
}
