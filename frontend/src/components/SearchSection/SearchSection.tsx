import { useEffect, useState } from "react";
import "./SearchSection.css";
import { ai_web_service_uri, py_backend_uri } from "../../App";
import CloseButton from "react-bootstrap/CloseButton";
import clsx from "clsx";
import { sha256 } from "js-sha256";
import { Idea as IdeaC } from "../../classes/MainIdeas";
import Idea from "../Idea/Idea";

//Perhaps display Sites and their ideas instead of ideas and which sites agree
//TODO: Add bottom bar
enum SearchState {
  ERROR,
  IDLE,
  GETTING_KEYWORDS,
  SEARCHING_WEB,
  CRAWLING_SITE,
  PARSING_SITE_DATA,
  FINISHED,
}

enum ResultsDisplayMode {
  IDEAS,
  SITES,
}

const SearchSection = () => {
  async function onFormSubmission(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (searchText.length == 0) return;
    await resetSearch();
    const hasher = sha256.create();
    hasher.update(searchText);
    const newSearchToken = Date.now().toString() + hasher.hex();
    await setSearchToken(newSearchToken);
    console.log(`Search Token is : ${newSearchToken}`);
    setSearchState(SearchState.GETTING_KEYWORDS);
    return;
  }

  const [searchText, setSearchText] = useState("");
  const [searchState, setSearchState] = useState(SearchState.IDLE);
  const [currCrawlSiteIndex, setcurrCrawlSiteIndex] = useState<number>(0);
  const [keywords, setKeyWords] = useState<string[]>([]);
  const [searchSites, setSearchSites] = useState<[string, string][]>([]);
  const [searchSitesVisible, setSearchSitesVisible] = useState(false);
  const [sitesDataArray, setSitesDataArray] = useState<any>([]);
  const [nrUrisPerCrawl, setNrUrisPerCrawl] = useState(1);
  const [nrGoogleSearchResults, setNrGoogleSearchResults] = useState(5);
  const [resultsDisplayMode, setResultsDisplayMode] = useState(
    ResultsDisplayMode.SITES
  );

  const [mainIdeas, setMainIdeas] = useState<IdeaC[]>(
    //   {
    //   ideas: [
    //     {
    //       text: "The sky is blue",
    //       origin_sub_page_uris: [
    //         "www.google.com/subpage1",
    //         "www.google.com/subpage1",
    //         "www.google.com/subpage1",
    //         "www.reddit.com/hi",
    //       ],
    //       origin_site_uris: ["www.google.com", "www.reddit.com"],
    //     },
    //     {
    //       text: "The sky is blue",
    //       origin_sub_page_uris: [
    //         "www.reddit.com/subpage1",
    //         "www.reddit.com/subpage1",
    //         "www.reddit.com/subpage1",
    //       ],
    //       origin_site_uris: ["www.reddit.com"],
    //     },
    //     {
    //       text: "The sky is blue loremasdajgdlaskfk;sf ksadkfasklfasklfashfasjdfahflahs fasdk fajskfashflasdfadfdhlasdfjldsfjlkdsf",
    //       origin_sub_page_uris: [
    //         "www.wikipedia.com/subpage1",
    //         "www.wikipedia.com/subpage1",
    //         "www.wikipedia.com/subpage1",
    //       ],
    //       origin_site_uris: ["www.wikipedia.com"],
    //     },
    //   ],
    // }
    []
  );
  /**
   * An identifier for the search.
   */
  const [searchToken, setSearchToken] = useState("");

  function onResultDisplayModeChange(e: React.ChangeEvent<HTMLInputElement>) {
    switch (e.currentTarget.value) {
      case "sites":
        setResultsDisplayMode(ResultsDisplayMode.SITES);
        break;
      case "ideas":
        setResultsDisplayMode(ResultsDisplayMode.IDEAS);
        break;
      default:
        break;
    }
  }

  async function resetSearch() {
    // await setcurrCrawlSiteIndex("");
    // await setKeyWords([]);
    await setSearchSites([]);
    await setMainIdeas([]);
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
      throw new Error("Extracting keywords failed!");
      return;
    }
    const keywords: string[] = await resp.json();
    keywords.push(searchText);
    searchText.split(" ").forEach((word) => keywords.push(word));
    await setKeyWords(keywords);
    console.log(keywords);
  }

  async function getAndSetSearchSites() {
    const resp = await fetch(
      `${py_backend_uri}/google_search_websites/${nrGoogleSearchResults}`,
      {
        method: "POST",
        body: searchText,
      }
    );
    if (resp.status !== 200) {
      throw new Error("Google Search API failed!");
    }
    const googleSearchWebsites: [string, string][] = await resp.json();
    setSearchSites(googleSearchWebsites);
  }

  /**
   * Crawls subPageUri. Puts SiteData Object inside sitesDataArray
   */
  async function crawlSite(subPageUri: string, siteUri: string) {
    const crawlResult = await fetch(
      `${py_backend_uri}/crawl/${nrUrisPerCrawl}`,
      {
        method: "POST",
        body: JSON.stringify({
          site_uri: siteUri,
          sub_page_uri: subPageUri,
          query_keywords: keywords,
        }),
        headers: {
          "Content-Type": "application/json",
        },
      }
    );
    if (crawlResult.status !== 200) {
      console.error(`Crawling ${subPageUri} failed.`);
      return;
    }
    const siteData = await crawlResult.json();
    console.log(siteData);
    await setSitesDataArray((prevSites) => [...prevSites, ...siteData]);
  }

  async function getAndSetMainIdeas() {
    console.log(
      JSON.stringify({
        array: sitesDataArray,
      })
    );
    const resp = await fetch(
      `${ai_web_service_uri}/main_ideas/${searchToken}`,
      {
        method: "POST",
        body: JSON.stringify({
          array: sitesDataArray,
        }),
      }
    );
    const mainIdeas: IdeaC[] = await resp.json();
    await setMainIdeas(mainIdeas);
    console.log("NAIN IDEAS: " + mainIdeas);
  }

  useEffect(() => {
    switch (searchState) {
      case SearchState.GETTING_KEYWORDS:
        (async () => {
          try {
            await getAndSetKeywords();
            setSearchState(SearchState.SEARCHING_WEB);
          } catch (e) {
            setSearchState(SearchState.ERROR);
            console.error(e);
          }
        })();
        break;
      case SearchState.SEARCHING_WEB:
        (async () => {
          try {
            await getAndSetSearchSites();
            await setcurrCrawlSiteIndex(0);
            setSearchState(SearchState.CRAWLING_SITE);
          } catch (e) {
            setSearchState(SearchState.ERROR);
            console.error(e);
          }
        })();
        break;
      case SearchState.CRAWLING_SITE:
        (async () => {
          for (let i = 0; i < searchSites.length; i++) {
            const [subPageUri, siteUri] = searchSites[i];
            await setcurrCrawlSiteIndex(i);
            try {
              await crawlSite(subPageUri, siteUri);
            } catch (e) {
              console.error(e);
            }
          }
          setSearchState(SearchState.PARSING_SITE_DATA);
        })();
        break;
      case SearchState.PARSING_SITE_DATA:
        (async () => {
          try {
            await getAndSetMainIdeas();
            setSearchState(SearchState.FINISHED);
          } catch (e) {
            console.error(e);
          }
        })();
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
      case SearchState.FINISHED:
        return "Finished!";
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
          {searchState !== SearchState.IDLE &&
            searchState != SearchState.FINISHED && (
              <img className="large-icon" src="/loading-anim.gif" />
            )}
        </div>
      </form>
      <div className="settings-col">
        <div className="input-row">
          <h5>No. of Google Results</h5>
          <input
            min={1}
            max={10}
            name="nr-google-results"
            type="number"
            value={nrGoogleSearchResults}
            onChange={(event) => {
              setNrGoogleSearchResults(Number(event.currentTarget.value));
            }}
          />
        </div>
        <div className="input-row">
          <h5>No. of URIs per site</h5>
          <input
            min={1}
            max={100}
            name="nr-uris-input"
            type="number"
            value={nrUrisPerCrawl}
            onChange={(event) => {
              setNrUrisPerCrawl(Number(event.currentTarget.value));
            }}
          />
        </div>
        <div className="input-row">
          <h5>Results Display Mode</h5>
          <fieldset>
            <div className="form-check">
              <input
                className="form-check-input"
                type="checkbox"
                value="sites"
                name="results-display-mode"
                id="sites"
                onChange={onResultDisplayModeChange}
                checked={resultsDisplayMode === ResultsDisplayMode.SITES}
              />
              <label htmlFor="sites" className="form-check-label">
                Sites
              </label>
            </div>
            <div className="form-check">
              <input
                className="form-check-input"
                type="checkbox"
                value="ideas"
                id="ideas"
                name="results-display-mode"
                onChange={onResultDisplayModeChange}
                checked={resultsDisplayMode === ResultsDisplayMode.IDEAS}
              />
              <label htmlFor="ideas" className="form-check-label">
                Ideas
              </label>
            </div>
          </fieldset>
        </div>
      </div>

      {searchState === SearchState.ERROR && (
        <button className="error-container btn btn-danger" disabled={true}>
          <h3>Something went wrong. Please try again.</h3>
        </button>
      )}

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
            disabled={searchSites.length === 0}
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

      <hr />
      <div
        className={clsx({
          "main-ideas": true,
          "main-ideas-hidden": mainIdeas.length === 0,
          "main-ideas-visible": mainIdeas.length !== 0,
        })}
      >
        {mainIdeas.map((idea, index) => (
          <Idea idea={idea} key={`idea${index}`} />
        ))}
      </div>
    </section>
  );
};

export default SearchSection;
