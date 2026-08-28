import { useState } from "react";

import PriorityBadge from "./PriorityBadge";
import StatusBadge from "./StatusBadge";


function compactId(id) {
  if (!id || id.length < 17) return id;
  return `${id.slice(0, 8)}…${id.slice(-5)}`;
}


export default function EmergencyCard({
  emergency,
  assigning,
  dispatch,
  onAssign,
}) {
  const [copied, setCopied] = useState(false);
  const emergencyId = emergency.id;

  const copyId = async () => {
    await navigator.clipboard.writeText(emergencyId);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1500);
  };

  return (
    <article className="emergency-card">
      <div className="emergency-card__header">
        <div>
          <span className="eyebrow">Emergency</span>
          <code title={emergencyId}>{compactId(emergencyId)}</code>
        </div>
        <button
          className="button button--icon"
          type="button"
          onClick={copyId}
          aria-label={`Copy emergency ID ${emergencyId}`}
        >
          {copied ? "Copied" : "Copy ID"}
        </button>
      </div>

      <div className="badge-row">
        <PriorityBadge priority={emergency.priority} />
        <StatusBadge status={emergency.status} />
        {emergency.type && (
          <span className="badge badge--neutral">
            {emergency.type.replaceAll("_", " ")}
          </span>
        )}
      </div>

      {emergency.description && <p>{emergency.description}</p>}

      {(emergency.city || emergency.latitude != null) && (
        <dl className="compact-details">
          {emergency.city && (
            <div><dt>City</dt><dd>{emergency.city}</dd></div>
          )}
          {emergency.latitude != null && (
            <div>
              <dt>Coordinates</dt>
              <dd>{emergency.latitude}, {emergency.longitude}</dd>
            </div>
          )}
        </dl>
      )}

      <button
        className="button button--primary button--compact"
        type="button"
        onClick={() => onAssign(emergencyId)}
        disabled={assigning}
      >
        {assigning ? "Assigning..." : "Assign response unit"}
      </button>

      {dispatch && (
        <div className="dispatch-success" role="status">
          <strong>Assigned to {dispatch.response_unit_name}</strong>
          <span>
            Distance: {(dispatch.distance_meters / 1000).toFixed(2)} km
          </span>
        </div>
      )}
    </article>
  );
}
