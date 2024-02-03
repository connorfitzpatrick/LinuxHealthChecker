// ServerTab.js
import React, { useState } from "react";
import "./serverTab.css";

const ServerTab = ({ serverName, serverInfo }) => {
  const [expanded, setExpanded] = useState(false);

  const toggleExpand = () => {
    setExpanded(!expanded);
  };

  return (
    <div className={`server-tab ${serverInfo.overall_state}`}>
      <div className="tab-header" onClick={toggleExpand}>
        <div className="server-info">
          <span className="server-name">{serverName}</span>
          <span className="server-state">{serverInfo.overall_state}</span>
        </div>
        <span className="expand-icon">{expanded ? "▼ " : "► "}</span>
      </div>
      {expanded && (
        <div className="tab-details">
          <p>{serverInfo.details}</p>
          {/* Add more detailed information as needed */}
        </div>
      )}
    </div>
  );
};

export default ServerTab;
