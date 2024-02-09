// ServerDetailsPopup.js
import React, { useState, useEffect } from "react";
import "./detailsPopup.css";

const DetailsPopup = ({ serverName, serverInfo, onClose }) => {
  const [selectedMenuItem, setSelectedMenuItem] = useState("Filesystems");

  const menuItems = [
    "Filesystems",
    "Inodes",
    "CPU Usage",
    "Network",
    "Services",
    "Logs",
  ];

  // useEffect toggles the main page's scrolling ability based on the popups visibility
  useEffect(() => {
    // Disable scrolling on the body
    document.body.style.overflow = "hidden";
    return () => {
      // Re-enable scrolling when the component unmounts
      document.body.style.overflow = "unset";
    };
  }, []);

  const renderContent = () => {
    const issues = serverInfo.server_issues[selectedMenuItem];
    switch (selectedMenuItem) {
      case "Filesystems":
        return (
          <>
            {issues &&
              issues.map((issue, index) => <div key={index}>{issue}</div>)}

            <table>
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
            </table>
          </>
        );
      case "Inodes":
        return (
          <>
            {issues &&
              issues.map((issue, index) => <div key={index}>{issue}</div>)}

            <table>
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
                {serverInfo.inode_info.inode_data.map((inode, index) => (
                  <tr key={index}>
                    <td>{inode.Filesystem}</td>
                    <td>{inode.Size}</td>
                    <td>{inode.Used}</td>
                    <td>{inode.Avail}</td>
                    <td>{inode["Use%"]}</td>
                    <td>{inode.MountedOn}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        );
      case "Logs":
        return (
          <>
            {serverInfo.logs.map((issue, index) => (
              <div key={index}>{issue}</div>
            ))}
          </>
        );
    }
    return <div>{serverInfo[selectedMenuItem.toLowerCase()]}</div>;
  };

  return (
    <div className="popup-overlay" onClick={onClose}>
      <div className="popup-container" onClick={(e) => e.stopPropagation()}>
        <div className="side-menu">
          <div className="server-name-header">{serverName}</div> {}
          {menuItems.map((item) => (
            <div
              key={item}
              className={`menu-item ${
                selectedMenuItem === item ? "active" : ""
              }`}
              onClick={() => setSelectedMenuItem(item)}
            >
              {item}
            </div>
          ))}
        </div>
        <div className="content-container">
          <h1>{selectedMenuItem}</h1>
          <hr></hr>
          <div className="content-area">{renderContent()}</div>
        </div>
      </div>
    </div>
  );
};

export default DetailsPopup;
