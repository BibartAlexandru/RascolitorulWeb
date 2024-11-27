import { useState } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import Login from "./components/Login/Login";
import CoolNavbar from "./components/CoolNavbar/CoolNavbar";
import Signup from "./components/Signup/Signup";
import "./App.css";
import SearchSection from "./components/SearchSection/SearchSection";

export const py_backend_uri = "http://localhost:5000/prajitura";
function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(
    localStorage.getItem("isAuthenticated") === "true"
  );

  return (
    <Router>
      <Routes>
        <Route
          path="/login"
          element={<Login setIsAuthenticated={setIsAuthenticated} />}
        />
        <Route
          path="/signup"
          element={<Signup setIsAuthenticated={setIsAuthenticated} />}
        />
        <Route
          path="/index"
          element={
            isAuthenticated ? (
              <>
                <CoolNavbar />
                <SearchSection />
              </>
            ) : (
              <Navigate to="/login" />
            )
          }
        />
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </Router>
  );
}

export default App;
