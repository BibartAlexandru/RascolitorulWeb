import { useEffect, useState } from "react";
import "./SearchSection.css";
import { ai_web_service_uri, py_backend_uri } from "../../App";
import CloseButton from "react-bootstrap/CloseButton";
import clsx from "clsx";

enum SearchState {
  ERROR,
  IDLE,
  GETTING_KEYWORDS,
  SEARCHING_WEB,
  CRAWLING_SITE,
  PARSING_SITE_DATA,
}

const SearchSection = () => {
  async function onFormSubmission(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (searchText.length == 0) return;
    await resetSearch();
    setSearchState(SearchState.GETTING_KEYWORDS);
    return;
  }

  const [searchText, setSearchText] = useState("");
  const [searchState, setSearchState] = useState(SearchState.IDLE);
  const [currCrawlSiteIndex, setcurrCrawlSiteIndex] = useState<number>(0);
  const [keywords, setKeyWords] = useState<string[]>([]);
  const [searchSites, setSearchSites] = useState<[string, string][]>([]);
  const [searchSitesVisible, setSearchSitesVisible] = useState(false);

  async function resetSearch() {
    // await setcurrCrawlSiteIndex("");
    // await setKeyWords([]);
    await setSearchSites([]);
  }

  async function getAndSetKeywords() {
    const resp = await fetch(`${ai_web_service_uri}/extract_search_keywords`, {
      method: "POST",
      headers: {
        "Content-Type": "text/plain",
      },
      body: searchText,
    });
    if (resp.status !== 200) {
      console.error("Extracting keywords failed!");
      await setSearchState(SearchState.ERROR);
      return;
    }
    const keywords: string[] = await resp.json();
    keywords.push(searchText);
    searchText.split(" ").forEach((word) => keywords.push(word));
    await setKeyWords(keywords);
    console.log(keywords);
  }

  async function getAndSetSearchSites() {
    const resp = await fetch(`${py_backend_uri}/google_search_websites`, {
      method: "POST",
      body: searchText,
    });
    if (resp.status !== 200) {
      console.error("Google Search API failed!");
      setSearchState(SearchState.ERROR);
      return;
    }
    const googleSearchWebsites: [string, string][] = await resp.json();
    setSearchSites(googleSearchWebsites);
  }

  async function crawlSite(subPageUri: string, siteUri: string) {
    const crawlResult = await fetch(`${py_backend_uri}/crawl`, {
      method: "POST",
      body: JSON.stringify({
        site_uri: siteUri,
        sub_page_uri: subPageUri,
        query_keywords: keywords,
      }),
      headers: {
        "Content-Type": "application/json",
      },
    });
    if (crawlResult.status !== 200) {
      console.error(`Crawling ${subPageUri} failed.`);
      return;
    }
    console.log(await crawlResult.json());
  }

  useEffect(() => {
    switch (searchState) {
      case SearchState.GETTING_KEYWORDS:
        (async () => {
          await getAndSetKeywords();
          setSearchState(SearchState.SEARCHING_WEB);
        })();
        break;
      case SearchState.SEARCHING_WEB:
        (async () => {
          await getAndSetSearchSites();
          await setcurrCrawlSiteIndex(0);
          setSearchState(SearchState.CRAWLING_SITE);
        })();
        break;
      case SearchState.CRAWLING_SITE:
        (async () => {
          for (let i = 0; i < searchSites.length; i++) {
            const [subPageUri, siteUri] = searchSites[i];
            await setcurrCrawlSiteIndex(i);
            await crawlSite(subPageUri, siteUri);
          }
          setSearchState(SearchState.PARSING_SITE_DATA);
        })();
        break;
      case SearchState.PARSING_SITE_DATA:
        break;
    }
  }, [searchState]);

  function searchStateToString(s: SearchState): string {
    switch (s) {
      case SearchState.GETTING_KEYWORDS:
        return "Extracting keywords from query...";
      case SearchState.SEARCHING_WEB:
        return "Searching the web...";
      case SearchState.CRAWLING_SITE:
        return "Crawling ";
      case SearchState.PARSING_SITE_DATA:
        return "Parsing the data...";
    }
    return "Unknown State";
  }

  const currentActivityClass: string = clsx({
    "current-activity": true,
    hidden: searchState === SearchState.IDLE,
    displayed: searchState !== SearchState.IDLE,
  });

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
          <CloseButton
            onClick={() => {
              setSearchState(SearchState.IDLE);
            }}
          />
          {searchState !== SearchState.IDLE && (
            <img className="large-icon" src="/loading-anim.gif" />
          )}
        </div>
      </form>

      <div className={currentActivityClass}>
        {searchState === SearchState.CRAWLING_SITE ? (
          <h4 className="state-text">
            Crawling
            <b>
              <a href={searchSites[currCrawlSiteIndex][0]} target="_blank">
                {searchSites[currCrawlSiteIndex][0]}
              </a>
            </b>
          </h4>
        ) : (
          <h4 className="state-text">{searchStateToString(searchState)}</h4>
        )}
        <div className="google-websites-col">
          <button
            className="no-btn"
            onClick={() => {
              setSearchSitesVisible(!searchSitesVisible);
            }}
          >
            <h4>Websites Found</h4>
          </button>
          {searchSitesVisible && (
            <div className="uris-col">
              <hr />
              {searchSites.map(([subPageUri, siteUri], index) => (
                <a
                  href={subPageUri}
                  key={`uri${index}`}
                  className="shortened-link"
                  target="_blank"
                >
                  {subPageUri}
                </a>
              ))}
            </div>
          )}
        </div>
      </div>

      {searchState === SearchState.ERROR && (
        <div>
          <h3>Something went wrong. Please try again.</h3>
        </div>
      )}
    </section>
  );
};

export default SearchSection;
