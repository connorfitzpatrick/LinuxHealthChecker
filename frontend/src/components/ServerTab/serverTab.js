// ServerTab.js
import React, { useState } from "react";
import "./serverTab.css";
import DetailsPopup from "../DetailsPopup/detailsPopup";

const ServerTab = ({ serverName, serverInfo }) => {
  const [expanded, setExpanded] = useState(false);
  const [showPopup, setShowPopup] = useState(false);

  const toggleExpand = () => {
    setExpanded(!expanded);
  };

  const handleDetailsButtonClick = () => {
    setShowPopup(true);
  };

  const closePopup = () => {
    setShowPopup(false);
  };

  const renderServerDetails = () => {
    switch (serverInfo.overall_state) {
      case "Error":
        return <p>Could not connect to {serverName}</p>;
      case "Loading":
        return <p>The health check for {serverName} is currently running</p>;
      case "Warning":
        return (
          <>
            {Object.keys(serverInfo.server_issues).map((issueType, index) => (
              <div key={index} className="problem-type">
                <h3>{issueType}:</h3>
                {serverInfo.server_issues[issueType].map(
                  (issue, innerIndex) => (
                    <div key={innerIndex} className="problem-detail">
                      {issue}
                    </div>
                  )
                )}
              </div>
            ))}
            <div className="problem-type">
              <h3>Logs:</h3>
              {serverInfo.logs.map((issue, index) => (
                <div key={index} className="problem-detail">
                  {issue}
                </div>
              ))}
            </div>
            <button
              className="details-button warning"
              onClick={handleDetailsButtonClick}
            >
              See Details
            </button>
          </>
        );
      case "Healthy":
        return (
          <>
            <p>{serverName} is Healthy!</p>
            <button
              className="details-button"
              onClick={handleDetailsButtonClick}
            >
              See Details
            </button>
          </>
        );
      default:
        return <p>Unknown server state. Issue with UI logic</p>;
    }
  };

  return (
    <div className={`server-tab ${serverInfo.overall_state}`}>
      <div className="tab-header" onClick={toggleExpand}>
        <div className="server-info">
          <span className="server-name">{serverName}</span>
          <span className="server-state">{serverInfo.overall_state}</span>
        </div>
        <span className="expand-icon">{expanded ? "▼" : "►"}</span>
      </div>
      {expanded && (
        <div
          className={`tab-details ${serverInfo.overall_state.toLowerCase()}`}
        >
          {renderServerDetails()}
        </div>
      )}
      {showPopup && (
        <DetailsPopup
          serverName={serverName}
          serverInfo={serverInfo}
          onClose={closePopup}
        />
      )}
    </div>
  );
};

export default ServerTab;
