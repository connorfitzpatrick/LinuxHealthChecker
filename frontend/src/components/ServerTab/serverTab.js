// ServerTab.js
import React, { useState } from "react";
import "./serverTab.css";

const ServerTab = ({ serverName, serverInfo }) => {
  const [expanded, setExpanded] = useState(false);

  const toggleExpand = () => {
    setExpanded(!expanded);
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
            {serverInfo.server_problems.map((problem, index) => (
              <div key={index} className="problem-detail">
                {problem}
              </div>
            ))}
            <button className="details-button">See Details</button>
          </>
        );
      case "Healthy":
        return (
          <>
            <p>{serverName} appears healthy</p>
            <button className="details-button">See Details</button>
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
        <span className="expand-icon">{expanded ? "▼ " : "► "}</span>
      </div>
      {expanded && <div className="tab-details">{renderServerDetails()}</div>}
    </div>
  );
};

export default ServerTab;

/* <table>
            <thead>
              <tr>
                <th>Filesystem</th>
                <th>Size</th>
                <th>Used</th>
                <th>Avail</th>
                <th>Use%</th>
                <th>Mounted on</th>
              </tr>
            </thead>
            <tbody>
              {serverInfo.filesystem_info.filesystem_data.map((fs, index) => (
                <tr key={index}>
                  <td>{fs.Filesystem}</td>
                  <td>{fs.Size}</td>
                  <td>{fs.Used}</td>
                  <td>{fs.Avail}</td>
                  <td>{fs["Use%"]}</td>
                  <td>{fs.MountedOn}</td>
                </tr>
              ))}
            </tbody>
          </table> */
