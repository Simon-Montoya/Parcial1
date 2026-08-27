import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  assignEmergency,
  broadcastNotification,
  getZoneAggregation,
} from "../services/api";

import {
  useRealtimeNotifications,
} from "../hooks/useRealtimeNotifications";

import EmergencyMap from "../components/EmergencyMap";


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

  const [dispatchResults, setDispatchResults] =
    useState({});

  const [lastNotification, setLastNotification] =
    useState(null);


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

        setLastNotification(notification);

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
        err.message ||
          "Unable to assign response unit."
      );

    } finally {
      setAssigningId(null);
    }
  };


  // --------------------------------------------------
  // UI
  // --------------------------------------------------

  return (
    <main>
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
        type="button"
        onClick={loadZone}
        disabled={loading}
      >
        {loading
          ? "Loading..."
          : "Refresh"}
      </button>


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


      {/* -------------------------------------------- */}
      {/* Realtime feedback */}
      {/* -------------------------------------------- */}

      {lastNotification && (
        <section className="realtime-message">
          <strong>
            Realtime update received
          </strong>

          <p>
            {
              lastNotification.message
            }
          </p>

          <p>
            Emergency:{" "}
            {
              lastNotification
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
                            <code>
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
                                  {Math.round(
                                    dispatchResults[
                                      emergencyId
                                    ]
                                      .distance_meters
                                  )}{" "}
                                  m
                                </p>
                              </div>
                            )}
                          </div>
                        )
                      )}
                  </div>
                </article>
              )
            )}
          </section>


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
                          {Math.round(
                            dispatchResults[
                              emergency.id
                            ]
                              .distance_meters
                          )}{" "}
                          m
                        </p>
                      </div>
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