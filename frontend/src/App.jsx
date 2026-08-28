import { BrowserRouter, Route, Routes } from "react-router-dom";

import AppHeader from "./components/AppHeader";
import OperatorAccess from "./components/OperatorAccess";
import CitizenPage from "./pages/CitizenPage";

export default function App() {
  return (
    <BrowserRouter>
      <AppHeader />

      <Routes>
        <Route
          path="/"
          element={<CitizenPage />}
        />

        <Route
          path="/operator"
          element={<OperatorAccess />}
        />
      </Routes>
    </BrowserRouter>
  );
}
