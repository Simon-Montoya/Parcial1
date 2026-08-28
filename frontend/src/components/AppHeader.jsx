import { NavLink } from "react-router-dom";


export default function AppHeader() {
  return (
    <header className="app-header">
      <div className="app-header__inner">
        <NavLink className="brand" to="/">
          <span className="brand__mark" aria-hidden="true">
            ER
          </span>
          <span>
            <strong>Emergency Response</strong>
            <small>Regional coordination platform</small>
          </span>
        </NavLink>

        <nav className="primary-nav" aria-label="Main navigation">
          <NavLink to="/" end>
            Report Emergency
          </NavLink>
          <NavLink to="/operator">
            Operator Dashboard
          </NavLink>
        </nav>
      </div>
    </header>
  );
}
