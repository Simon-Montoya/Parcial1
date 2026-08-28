import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  assignEmergency,
  broadcastNotification,
  getZoneAggregation,
  updateDispatchStatus,
} from "../services/api";

import {
  useRealtimeNotifications,
} from "../hooks/useRealtimeNotifications";

import EmergencyMap from "../components/EmergencyMap";
import MetricCard from "../components/MetricCard";
import NotificationPanel from "../components/NotificationPanel";
import PriorityBadge from "../components/PriorityBadge";
import StatusBadge from "../components/StatusBadge";


const cities = [
  "CALI",
  "PEREIRA",
  "MANIZALES",
  "CHOCO",
];


export default function OperatorDashboard() {
  // --------------------------------------------------
  // State
  // --------------------------------------------------

  const [city, setCity] = useState("CALI");

  const [zone, setZone] = useState(null);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const [actionError, setActionError] = useState("");

  const [assigningId, setAssigningId] = useState(null);
  const [updatingId, setUpdatingId] = useState(null);
  const [actionSuccess, setActionSuccess] = useState("");

  const [dispatchResults, setDispatchResults] =
    useState({});

  const [notifications, setNotifications] = useState([]);


  // --------------------------------------------------
  // Load zone information
  // --------------------------------------------------

  const loadZone = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const data = await getZoneAggregation(city);

      setZone(data);

    } catch (err) {
      console.error(
        "Error loading zone:",
        err
      );

      setError(
        err.message ||
          "Unable to load zone information."
      );

    } finally {
      setLoading(false);
    }
  }, [city]);


  // --------------------------------------------------
  // Initial load / city change
  // --------------------------------------------------

  useEffect(() => {
    loadZone();
  }, [loadZone]);


  // --------------------------------------------------
  // Realtime callback
  // --------------------------------------------------

  const handleRealtimeNotification =
    useCallback(
      (notification) => {
        console.log(
          "Realtime notification received:",
          notification
        );

        setNotifications((previous) => {
          const withoutDuplicate = previous.filter(
            (item) => item.id !== notification.id
          );
          return [notification, ...withoutDuplicate].slice(0, 10);
        });

        // Reload geographical data whenever
        // a new notification is inserted.
        loadZone();
      },
      [loadZone]
    );


  // --------------------------------------------------
  // Supabase Realtime subscription
  // --------------------------------------------------

  useRealtimeNotifications(
    handleRealtimeNotification
  );


  // --------------------------------------------------
  // Assign response unit
  // --------------------------------------------------

  const handleAssign = async (
    emergencyId
  ) => {
    setAssigningId(emergencyId);
    setActionError("");
    setActionSuccess("");

    try {
      // 1. Dispatch
      const dispatch =
        await assignEmergency(
          emergencyId
        );

      setDispatchResults(
        (previous) => ({
          ...previous,
          [emergencyId]: dispatch,
        })
      );


      // 2. Notification
      await broadcastNotification(
        emergencyId,
        "ASSIGNED",
        `Response unit ${dispatch.response_unit_name} assigned to emergency.`
      );


      // 3. Refresh dashboard
      await loadZone();

    } catch (err) {
      console.error(
        "Assignment error:",
        err
      );

      setActionError(
        /no available|not available for assignment/i.test(err.message)
          ? "No available response unit can be assigned to this emergency."
          : err.message || "Unable to assign response unit."
      );

    } finally {
      setAssigningId(null);
    }
  };

  const handleDispatchStatus = async (emergencyId, status) => {
    const dispatch = dispatchResults[emergencyId];
    if (!dispatch?.dispatch_id) return;

    setUpdatingId(emergencyId);
    setActionError("");
    setActionSuccess("");

    try {
      const updated = await updateDispatchStatus(
        dispatch.dispatch_id,
        status
      );

      setDispatchResults((previous) => ({
        ...previous,
        [emergencyId]: { ...previous[emergencyId], ...updated },
      }));

      const message = status === "RESOLVED"
        ? "Emergency resolved successfully."
        : "Emergency response is now in progress.";

      try {
        await broadcastNotification(emergencyId, status, message);
      } catch {
        setActionError(
          "The status was updated, but its notification could not be sent."
        );
      }

      setActionSuccess(
        status === "RESOLVED"
          ? `Emergency resolved. ${updated.response_unit_name} is now available.`
          : "Emergency response started."
      );
      await loadZone();
    } catch (statusError) {
      setActionError(
        statusError.status === 409
          ? "This dispatch cannot move to the requested status."
          : statusError.message || "Unable to update the dispatch."
      );
    } finally {
      setUpdatingId(null);
    }
  };


  // --------------------------------------------------
  // UI
  // --------------------------------------------------

  return (
    <main className="page page--operator">
      <h1>
        Emergency Operations Dashboard
      </h1>

      <p>
        Monitor active emergencies and
        geographical hotspots.
      </p>


      {/* -------------------------------------------- */}
      {/* City selector */}
      {/* -------------------------------------------- */}

      <section className="dashboard-toolbar panel" aria-label="Dashboard filters">
      <label>
        City

        <select
          value={city}
          onChange={(event) =>
            setCity(event.target.value)
          }
        >
          {cities.map((item) => (
            <option
              key={item}
              value={item}
            >
              {item}
            </option>
          ))}
        </select>
      </label>


      {/* Manual refresh can remain as backup */}
      <button
        className="button button--secondary"
        type="button"
        onClick={loadZone}
        disabled={loading}
      >
        {loading
          ? "Loading..."
          : "Refresh"}
      </button>
      </section>


      {/* -------------------------------------------- */}
      {/* Errors */}
      {/* -------------------------------------------- */}

      {error && (
        <p className="action-error">
          Error loading dashboard: {error}
        </p>
      )}


      {actionError && (
        <p className="action-error">
          Action error: {actionError}
        </p>
      )}

      {actionSuccess && (
        <p className="action-success" role="status">
          {actionSuccess}
        </p>
      )}


      {/* -------------------------------------------- */}
      {/* Realtime feedback */}
      {/* -------------------------------------------- */}

      {notifications[0] && (
        <section className="realtime-message">
          <strong>
            Realtime update received
          </strong>

          <p>
            {
              notifications[0].message
            }
          </p>

          <p>
            Emergency:{" "}
            {
              notifications[0]
                .emergency_id
            }
          </p>
        </section>
      )}


      {/* -------------------------------------------- */}
      {/* Dashboard data */}
      {/* -------------------------------------------- */}

      {zone && (
        <>
          {/* ---------------------------------------- */}
          {/* Summary */}
          {/* ---------------------------------------- */}

          <section className="dashboard-summary">
            <article className="metric-card">
              <h2>
                {
                  zone.total_active_emergencies
                }
              </h2>

              <p>
                Active emergencies
              </p>
            </article>
            <MetricCard label="Selected city" value={city} tone="city" />


            <article className="metric-card">
              <h2>
                {zone.hotspot_count}
              </h2>

              <p>
                Hotspots detected
              </p>
            </article>


            <article className="metric-card">
              <h2>
                {
                  zone
                    .isolated_emergencies
                    ?.length ?? 0
                }
              </h2>

              <p>
                Isolated emergencies
              </p>
            </article>
          </section>

          <EmergencyMap
            city={city}
            zone={zone}
            />


          {/* ---------------------------------------- */}
          {/* Hotspots */}
          {/* ---------------------------------------- */}

          <section>
            <h2>
              Hotspots
            </h2>


            {zone.hotspots?.length ===
              0 && (
              <p>
                No hotspots detected.
              </p>
            )}


            {zone.hotspots?.map(
              (hotspot) => (
                <article
                  className="hotspot-card"
                  key={
                    hotspot.cluster_id
                  }
                >
                  <h3>
                    Hotspot #
                    {
                      hotspot.cluster_id +
                      1
                    }
                  </h3>


                  <p>
                    Emergencies:{" "}
                    {
                      hotspot.emergency_count
                    }
                  </p>


                  <p>
                    Highest priority:{" "}
                    {
                      hotspot.highest_priority
                    }
                  </p>


                  <p>
                    Center:{" "}
                    {Number(
                      hotspot.center_latitude
                    ).toFixed(4)}
                    ,{" "}
                    {Number(
                      hotspot.center_longitude
                    ).toFixed(4)}
                  </p>


                  <p>
                    Radius:{" "}
                    {zone.radius_meters} m
                  </p>


                  {/* ------------------------------ */}
                  {/* Emergency IDs in hotspot */}
                  {/* ------------------------------ */}

                  <div className="hotspot-emergencies">
                    <h4>
                      Emergencies
                    </h4>


                    {hotspot
                      .emergency_ids
                      ?.length === 0 && (
                      <p>
                        No emergencies in
                        this hotspot.
                      </p>
                    )}


                    {hotspot
                      .emergency_ids
                      ?.map(
                        (
                          emergencyId
                        ) => (
                          <div
                            key={
                              emergencyId
                            }
                            className="hotspot-emergency-row"
                          >
                            <code title={emergencyId}>
                              {
                                emergencyId
                              }
                            </code>


                            <button
                              type="button"
                              onClick={() =>
                                handleAssign(
                                  emergencyId
                                )
                              }
                              disabled={
                                assigningId ===
                                emergencyId
                              }
                            >
                              {
                                assigningId ===
                                emergencyId
                                  ? "Assigning..."
                                  : "Assign response unit"
                              }
                            </button>


                            {dispatchResults[
                              emergencyId
                            ] && (
                              <div className="dispatch-success">
                                <strong>
                                  Unit assigned
                                </strong>

                                <p>
                                  {
                                    dispatchResults[
                                      emergencyId
                                    ]
                                      .response_unit_name
                                  }
                                </p>

                                <p>
                                  Distance:{" "}
                                  {(
                                    dispatchResults[
                                      emergencyId
                                    ]
                                      .distance_meters
                                    / 1000
                                  ).toFixed(2)}{" "}
                                  km
                                </p>
                              </div>
                            )}
                            {dispatchResults[emergencyId] && (
                              <LifecycleActions
                                dispatch={dispatchResults[emergencyId]}
                                loading={updatingId === emergencyId}
                                onUpdate={(status) =>
                                  handleDispatchStatus(emergencyId, status)
                                }
                              />
                            )}
                          </div>
                        )
                      )}
                  </div>
                </article>
              )
            )}
          </section>

          {zone.total_active_emergencies === 0 && (
            <div className="empty-state">
              <strong>No active emergencies in {city}.</strong>
              <p>The dashboard will refresh when new reports arrive.</p>
            </div>
          )}
          <NotificationPanel notifications={notifications} />


          {/* ---------------------------------------- */}
          {/* Isolated emergencies */}
          {/* ---------------------------------------- */}

          <section>
            <h2>
              Isolated emergencies
            </h2>


            {zone
              .isolated_emergencies
              ?.length === 0 && (
              <p>
                No isolated emergencies.
              </p>
            )}


            {zone
              .isolated_emergencies
              ?.map(
                (emergency) => (
                  <article
                    className="emergency-card"
                    key={
                      emergency.id
                    }
                  >
                    <code className="emergency-id" title={emergency.id}>
                      Emergency {emergency.id}
                    </code>
                    <div className="badge-row">
                      <PriorityBadge priority={emergency.priority} />
                      <StatusBadge status={emergency.status} />
                      <span className="badge badge--neutral">
                        {emergency.type?.replaceAll("_", " ")}
                      </span>
                    </div>
                    <strong>
                      {
                        emergency.priority
                      }
                      {" — "}
                      {emergency.type}
                    </strong>


                    <p>
                      {
                        emergency.description
                      }
                    </p>


                    <p>
                      Status:{" "}
                      {emergency.status}
                    </p>


                    <p>
                      Coordinates:{" "}
                      {
                        emergency.latitude
                      }
                      ,{" "}
                      {
                        emergency.longitude
                      }
                    </p>


                    <button
                      type="button"
                      onClick={() =>
                        handleAssign(
                          emergency.id
                        )
                      }
                      disabled={
                        assigningId ===
                        emergency.id
                      }
                    >
                      {
                        assigningId ===
                        emergency.id
                          ? "Assigning..."
                          : "Assign response unit"
                      }
                    </button>


                    {dispatchResults[
                      emergency.id
                    ] && (
                      <div className="dispatch-success">
                        <strong>
                          Unit assigned
                        </strong>

                        <p>
                          {
                            dispatchResults[
                              emergency.id
                            ]
                              .response_unit_name
                          }
                        </p>

                        <p>
                          Distance:{" "}
                          {(
                            dispatchResults[
                              emergency.id
                            ]
                              .distance_meters
                            / 1000
                          ).toFixed(2)}{" "}
                          km
                        </p>
                      </div>
                    )}
                    {dispatchResults[emergency.id] && (
                      <LifecycleActions
                        dispatch={dispatchResults[emergency.id]}
                        loading={updatingId === emergency.id}
                        onUpdate={(status) =>
                          handleDispatchStatus(emergency.id, status)
                        }
                      />
                    )}
                  </article>
                )
              )}
          </section>
        </>
      )}
    </main>
  );
}


function LifecycleActions({ dispatch, loading, onUpdate }) {
  const status = dispatch.status ?? "ASSIGNED";

  if (status === "RESOLVED") return null;

  return (
    <div className="lifecycle-actions" aria-label="Dispatch lifecycle actions">
      {status === "ASSIGNED" && (
        <button
          className="button button--secondary"
          type="button"
          disabled={loading}
          onClick={() => onUpdate("IN_PROGRESS")}
        >
          {loading ? "Updating..." : "Start response"}
        </button>
      )}
      <button
        className="button button--danger"
        type="button"
        disabled={loading}
        onClick={() => onUpdate("RESOLVED")}
      >
        {loading ? "Completing..." : "Complete Emergency"}
      </button>
    </div>
  );
}
