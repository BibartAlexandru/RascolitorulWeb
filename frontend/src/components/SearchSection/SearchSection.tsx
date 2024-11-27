import { useState } from "react";
import "./SearchSection.css";
import { py_backend_uri } from "../../App";

const SearchSection = () => {
  async function onFormSubmission(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (searchText.length == 0) return;
    const resp = await fetch(`${py_backend_uri}/search`, {
      method: "POST",
      body: searchText,
      headers: {
        "Content-Type": "text/plain",
      },
    });
    if (resp.ok) {
      console.log("OK RESP");
    } else {
      console.log("NOT OK");
    }
  }

  const [searchText, setSearchText] = useState("");

  return (
    <section className="search-section mt-5">
      <h1>Web Crawler</h1>
      <form onSubmit={onFormSubmission}>
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
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
          />
        </div>
      </form>
    </section>
  );
};

export default SearchSection;
