//import { useState } from "react";
import "./App.css";
import CoolNavbar from "./components/CoolNavbar/CoolNavbar";

function App() {
  return (
    <>
      <CoolNavbar></CoolNavbar>
      <section className="search-section mt-5">
        <h1>Web Crawler</h1>
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
            placeholder="Type what would you like to search!"
            className="search-input"
          />
        </div>
      </section>
    </>
  );
}

export default App;
