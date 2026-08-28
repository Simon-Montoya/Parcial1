import { useState } from "react";
import { createEmergency } from "../services/api";

const initialForm = {
  type: "RESCUE",
  city: "CALI",
  description: "",
  latitude: "3.4516",
  longitude: "-76.532",

  trapped_people: 0,
  injured_people: 0,
  gas_leak: false,
  fire: false,
  imminent_collapse_risk: false,

  adults: 0,
  children: 0,
  elderly: 0,
  accessibility_required: false,
  house_habitable: true,

  supply_category: "WATER",
  quantity: 1,
  notes: "",

  building_type: "",
  cracking_level: "LOW",
  settlement_level: "LOW",
  collapse_risk: false,
  road_risk: false,
  photo_url: "",
};

export default function CitizenPage() {
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const updateField = (event) => {
    const { name, value, type, checked } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const buildPayload = () => {
    const base = {
      type: form.type,
      city: form.city,
      description: form.description,
      latitude: Number(form.latitude),
      longitude: Number(form.longitude),
    };

    switch (form.type) {
      case "RESCUE":
        return {
          ...base,
          trapped_people: Number(form.trapped_people),
          injured_people: Number(form.injured_people),
          gas_leak: form.gas_leak,
          fire: form.fire,
          imminent_collapse_risk:
            form.imminent_collapse_risk,
        };

      case "SHELTER":
        return {
          ...base,
          adults: Number(form.adults),
          children: Number(form.children),
          elderly: Number(form.elderly),
          accessibility_required:
            form.accessibility_required,
          house_habitable: form.house_habitable,
        };

      case "SUPPLY":
        return {
          ...base,
          supply_category: form.supply_category,
          quantity: Number(form.quantity),
          notes: form.notes,
        };

      case "STRUCTURAL_DAMAGE":
        const structuralPayload = {
          ...base,
          building_type: form.building_type.trim(),
          cracking_level: form.cracking_level,
          settlement_level: form.settlement_level,
          collapse_risk: form.collapse_risk,
          road_risk: form.road_risk,
        };

        return form.photo_url.trim()
          ? {
              ...structuralPayload,
              photo_url: form.photo_url.trim(),
            }
          : structuralPayload;

      default:
        return base;
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setResult(null);
    setError("");

    if (
      form.type === "STRUCTURAL_DAMAGE"
      && !form.building_type.trim()
    ) {
      setError("Building type is required for structural damage reports.");
      return;
    }

    setLoading(true);

    try {
      const response = await createEmergency(
        buildPayload()
      );

      setResult(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page page--citizen">
      <header className="page-heading">
      <span className="eyebrow">Public emergency channel</span>
      <h1>Report an Emergency</h1>

      <p>
        Report an emergency to the regional response
        platform.
      </p>
      </header>

      <form className="report-form panel" onSubmit={handleSubmit}>
        <label>
          Emergency type
          <select
            name="type"
            value={form.type}
            onChange={updateField}
          >
            <option value="RESCUE">Rescue</option>
            <option value="SHELTER">Shelter</option>
            <option value="SUPPLY">Supplies</option>
            <option value="STRUCTURAL_DAMAGE">
              Structural damage
            </option>
          </select>
        </label>

        <label>
          City
          <select
            name="city"
            value={form.city}
            onChange={updateField}
          >
            <option value="CALI">Cali</option>
            <option value="PEREIRA">Pereira</option>
            <option value="MANIZALES">
              Manizales
            </option>
            <option value="CHOCO">Chocó</option>
          </select>
        </label>

        <label>
          Description
          <textarea
            name="description"
            value={form.description}
            onChange={updateField}
            required
          />
        </label>

        <label>
          Latitude
          <input
            name="latitude"
            type="number"
            step="any"
            value={form.latitude}
            onChange={updateField}
            required
          />
        </label>

        <label>
          Longitude
          <input
            name="longitude"
            type="number"
            step="any"
            value={form.longitude}
            onChange={updateField}
            required
          />
        </label>

        {form.type === "RESCUE" && (
          <>
            <h2>Rescue information</h2>

            <label>
              Trapped people
              <input
                name="trapped_people"
                type="number"
                min="0"
                value={form.trapped_people}
                onChange={updateField}
              />
            </label>

            <label>
              Injured people
              <input
                name="injured_people"
                type="number"
                min="0"
                value={form.injured_people}
                onChange={updateField}
              />
            </label>

            <label>
              <input
                name="gas_leak"
                type="checkbox"
                checked={form.gas_leak}
                onChange={updateField}
              />
              Gas leak
            </label>

            <label>
              <input
                name="fire"
                type="checkbox"
                checked={form.fire}
                onChange={updateField}
              />
              Fire
            </label>

            <label>
              <input
                name="imminent_collapse_risk"
                type="checkbox"
                checked={
                  form.imminent_collapse_risk
                }
                onChange={updateField}
              />
              Imminent collapse risk
            </label>
          </>
        )}

        {form.type === "SHELTER" && (
          <>
            <h2>Shelter information</h2>

            <input
              name="adults"
              aria-label="Adults"
              type="number"
              min="0"
              placeholder="Adults"
              value={form.adults}
              onChange={updateField}
            />

            <input
              name="children"
              aria-label="Children"
              type="number"
              min="0"
              placeholder="Children"
              value={form.children}
              onChange={updateField}
            />

            <input
              name="elderly"
              aria-label="Older adults"
              type="number"
              min="0"
              placeholder="Elderly"
              value={form.elderly}
              onChange={updateField}
            />

            <label>
              <input
                name="accessibility_required"
                type="checkbox"
                checked={
                  form.accessibility_required
                }
                onChange={updateField}
              />
              Accessibility required
            </label>

            <label>
              <input
                name="house_habitable"
                type="checkbox"
                checked={form.house_habitable}
                onChange={updateField}
              />
              House is habitable
            </label>
          </>
        )}

        {form.type === "SUPPLY" && (
          <>
            <h2>Supply information</h2>

            <select
              name="supply_category"
              aria-label="Supply category"
              value={form.supply_category}
              onChange={updateField}
            >
              <option value="WATER">Water</option>
              <option value="FOOD">Food</option>
              <option value="FIRST_AID">
                First aid
              </option>
              <option value="CHRONIC_MEDICATION">
                Chronic medication
              </option>
            </select>

            <input
              name="quantity"
              aria-label="Quantity"
              type="number"
              min="0"
              value={form.quantity}
              onChange={updateField}
            />

            <textarea
              name="notes"
              aria-label="Supply notes"
              placeholder="Notes"
              value={form.notes}
              onChange={updateField}
            />
          </>
        )}

        {form.type === "STRUCTURAL_DAMAGE" && (
          <>
            <h2>Structural damage</h2>

            <input
              name="building_type"
              aria-label="Building type"
              aria-describedby="building-type-help"
              placeholder="Building type"
              value={form.building_type}
              onChange={updateField}
              onInvalid={(event) => {
                event.preventDefault();
                setError(
                  "Building type is required for structural damage reports."
                );
              }}
              required
            />
            <small id="building-type-help">
              Required. Describe the affected structure.
            </small>

            <input
              name="cracking_level"
              aria-label="Cracking level"
              placeholder="Cracking level"
              value={form.cracking_level}
              onChange={updateField}
            />

            <input
              name="settlement_level"
              aria-label="Settlement level"
              placeholder="Settlement level"
              value={form.settlement_level}
              onChange={updateField}
            />

            <input
              name="photo_url"
              type="url"
              aria-label="Photo URL"
              placeholder="Optional photo URL"
              value={form.photo_url}
              onChange={updateField}
            />

            <label>
              <input
                name="collapse_risk"
                type="checkbox"
                checked={form.collapse_risk}
                onChange={updateField}
              />
              Collapse risk
            </label>

            <label>
              <input
                name="road_risk"
                type="checkbox"
                checked={form.road_risk}
                onChange={updateField}
              />
              Road risk
            </label>
          </>
        )}

        <button className="button button--danger submit-button" type="submit" disabled={loading}>
          {loading
            ? "Submitting..."
            : "Report emergency"}
        </button>
      </form>

      {error && (
        <p className="alert alert--error" role="alert">
          Unable to submit the report: {error}
        </p>
      )}

      {result && (
        <section className="result-card" aria-live="polite">
          <span className="result-card__icon" aria-hidden="true">✓</span>
          <div>
          <span className="eyebrow">Report received</span>
          <h2>Emergency reported successfully</h2>

          <p>
            ID: {result.id}
          </p>

          <p className={`badge priority-badge priority-${result.priority?.toLowerCase()}`}>
            Priority {result.priority}
          </p>

          <p className="badge status-badge">
            {result.status}
          </p>
          <p>
            City: {result.city ?? form.city}
          </p>
          <p>
            Type: {(result.type ?? form.type).replaceAll("_", " ")}
          </p>
          </div>
        </section>
      )}
    </main>
  );
}
