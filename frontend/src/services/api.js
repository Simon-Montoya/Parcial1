const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

if (!API_BASE_URL) {
  throw new Error("VITE_API_BASE_URL is not configured");
}


// ------------------------------------------------------
// Intake & Triage
// ------------------------------------------------------

export async function createEmergency(payload) {
  const response = await fetch(
    `${API_BASE_URL}/v1/emergencias`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data?.detail
        ? JSON.stringify(data.detail)
        : "Error creating emergency"
    );
  }

  return data;
}


// ------------------------------------------------------
// Geospatial
// ------------------------------------------------------

export async function getZoneAggregation(city) {
  const response = await fetch(
    `${API_BASE_URL}/v1/emergencias/zona/${city}`
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data?.detail
        ? JSON.stringify(data.detail)
        : "Error loading zone information"
    );
  }

  return data;
}


// ------------------------------------------------------
// Dispatch
// ------------------------------------------------------

export async function assignEmergency(emergencyId) {
  const response = await fetch(
    `${API_BASE_URL}/v1/despachos/asignar`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        emergency_id: emergencyId,
      }),
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data?.detail
        ? JSON.stringify(data.detail)
        : "Error assigning response unit"
    );
  }

  return data;
}


export async function updateDispatchStatus(dispatchId, status) {
  const response = await fetch(
    `${API_BASE_URL}/v1/despachos/${dispatchId}`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ status }),
    }
  );

  const data = await response.json();

  if (!response.ok) {
    const error = new Error(
      data?.detail
        ? JSON.stringify(data.detail)
        : "Unable to update dispatch status"
    );
    error.status = response.status;
    throw error;
  }

  return data;
}


// ------------------------------------------------------
// Notifications
// ------------------------------------------------------

export async function broadcastNotification(
  emergencyId,
  status,
  message
) {
  const response = await fetch(
    `${API_BASE_URL}/v1/notificaciones/broadcast`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        emergency_id: emergencyId,
        status,
        message,
      }),
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data?.detail
        ? JSON.stringify(data.detail)
        : "Error broadcasting notification"
    );
  }

  return data;
}
