import { useEffect } from "react";

import {
  Circle,
  MapContainer,
  Marker,
  Popup,
  TileLayer,
  useMap,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";

import L from "leaflet";

import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";


delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});


const cityCenters = {
  CALI: [3.4516, -76.532],
  PEREIRA: [4.8133, -75.6961],
  MANIZALES: [5.0703, -75.5138],
  CHOCO: [5.6919, -76.6583],
};

function MapViewport({ center }) {
  const map = useMap();

  useEffect(() => {
    map.setView(center, map.getZoom());
  }, [center, map]);

  return null;
}


export default function EmergencyMap({
  city,
  zone,
}) {
  const center =
    cityCenters[city] ??
    cityCenters.CALI;

  return (
    <section className="map-section">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Live geographic overview</span>
          <h2>Emergency Map — {city.charAt(0) + city.slice(1).toLowerCase()}</h2>
        </div>
        <span className="map-legend"><i /> Hotspot radius</span>
      </div>

      <MapContainer
        center={center}
        zoom={12}
        className="emergency-map"
      >
        <MapViewport center={center} />
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Hotspots */}
        {zone?.hotspots?.map(
          (hotspot) => {
            const latitude =
              Number(
                hotspot.center_latitude
              );

            const longitude =
              Number(
                hotspot.center_longitude
              );

            return (
              <Circle
                key={
                  hotspot.cluster_id
                }
                center={[
                  latitude,
                  longitude,
                ]}
                radius={
                  zone.radius_meters
                }
              >
                <Popup>
                  <strong>
                    Hotspot #
                    {
                      hotspot.cluster_id +
                      1
                    }
                  </strong>

                  <br />

                  Emergencies:{" "}
                  {
                    hotspot.emergency_count
                  }

                  <br />

                  Highest priority:{" "}
                  {
                    hotspot.highest_priority
                  }
                </Popup>
              </Circle>
            );
          }
        )}

        {/* Isolated emergencies */}
        {zone?.isolated_emergencies?.map(
          (emergency) => (
            <Marker
              key={emergency.id}
              position={[
                Number(
                  emergency.latitude
                ),
                Number(
                  emergency.longitude
                ),
              ]}
            >
              <Popup>
                <strong>
                  {emergency.priority}
                  {" — "}
                  {emergency.type}
                </strong>

                <br />

                {emergency.description}

                <br />

                Status:{" "}
                {emergency.status}
              </Popup>
            </Marker>
          )
        )}
      </MapContainer>
    </section>
  );
}
