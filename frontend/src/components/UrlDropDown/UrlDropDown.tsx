import React, { useState } from "react";
import "./UrlDropDown.css";

interface Props {
  url: string;
  urls: string[];
}

const UrlDropDown = ({ url, urls }: Props) => {
  const [subPagesVisible, setSubPagesVisibile] = useState(false);
  return (
    <div className="url-dropdown">
      <div className="input-row">
        <a href={url} target="_blank">
          {url}
        </a>
        <img
          className="medium-icon"
          src={subPagesVisible ? "/up-arrow.svg" : "/down-arrow.svg"}
          alt="arrow"
          style={{ cursor: "pointer" }}
          onClick={() => setSubPagesVisibile(!subPagesVisible)}
        />
      </div>
      {subPagesVisible && (
        <div>
          <hr />
          <div className="sub-urls-col">
            {urls.map((subPageUri, index) => (
              <a
                href={subPageUri}
                key={`${subPageUri}${index}`}
                target="_blank"
              >
                {subPageUri}
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default UrlDropDown;
