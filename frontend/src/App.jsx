import {
  BrowserRouter,
  Link,
  Route,
  Routes,
} from "react-router-dom";

import CitizenPage from "./pages/CitizenPage";
import OperatorDashboard from "./pages/OperatorDashboard";

export default function App() {
  return (
    <BrowserRouter>
      <nav className="navigation">
        <strong>
          Emergency Platform
        </strong>

        <div>
          <Link to="/">
            Report Emergency
          </Link>

          <Link to="/operator">
            Operator Dashboard
          </Link>
        </div>
      </nav>

      <Routes>
        <Route
          path="/"
          element={<CitizenPage />}
        />

        <Route
          path="/operator"
          element={<OperatorDashboard />}
        />
      </Routes>
    </BrowserRouter>
  );
}