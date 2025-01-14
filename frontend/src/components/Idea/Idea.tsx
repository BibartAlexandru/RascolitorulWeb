import React from "react";
import { Idea as IdeaClass } from "../../classes/MainIdeas";
import "./Idea.css";
import UrlDropDown from "../UrlDropDown/UrlDropDown";
interface Props {
  idea: IdeaClass;
}

const Idea = ({ idea }: Props) => {
  return (
    <div className="idea">
      <h5 className="text">{idea.text}</h5>
      <div className="agreeing-sites-row">
        {idea.origin_site_uris.map((siteUri, index) => (
          <UrlDropDown
            key={`${siteUri}${index}`}
            url={siteUri}
            urls={idea.origin_sub_page_uris.filter((sub) =>
              sub.includes(siteUri)
            )}
          />
        ))}
      </div>
    </div>
  );
};

export default Idea;
