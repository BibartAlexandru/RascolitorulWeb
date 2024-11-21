import { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Login from "./components/Login/Login";
import CoolNavbar from "./components/CoolNavbar/CoolNavbar";
import Signup from "./components/Signup/Signup";


function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(
    localStorage.getItem("isAuthenticated") === "true"
  );

  return (
    <Router>
      <Routes>
        <Route path="/prajitura/login" element={<Login setIsAuthenticated={setIsAuthenticated} />} />
        <Route path="/prajitura/signup" element={<Signup setIsAuthenticated={setIsAuthenticated} />} />
        <Route
          path="/prajitura/index"
          element={
            isAuthenticated ? (
              <>
                <CoolNavbar />
                <section className="search-section mt-5">
                  <h1>Web Crawler</h1>
                  <div className="input-row">
                    <img src="/search.svg" alt="search glass image" className="medium-icon" />
                    <input
                      type="text"
                      name="searchbar"
                      id="searchbar"
                      placeholder="Type what would you like to search!"
                      className="search-input"
                    />
                  </div>
                </section>
              </>
            ) : (
              <Navigate to="/prajitura/login" />
            )
          }
        />
        <Route path="*" element={<Navigate to="/prajitura/login" />} />
      </Routes>
    </Router>
  );
}

export default App;
