import { useState } from "react";
import "./App.css";
import CoolNavbar from "./components/CoolNavbar/CoolNavbar";

function App() {
  return (
    <>
      <CoolNavbar></CoolNavbar>
      <section className="search-section mt-5">
        <h1>Rascolitorul Web</h1>
        <div className="input-row">
          <img
            src="/search.svg"
            alt="search glass image"
            className="medium-icon"
          />
          <input
            type="text"
            name="searchbar"
            id="searchbar"
            placeholder="search something!"
            className="search-input"
          />
        </div>
      </section>
    </>
  );
}

export default App;
