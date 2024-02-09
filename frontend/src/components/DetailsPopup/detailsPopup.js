// ServerDetailsPopup.js
import React, { useState } from "react";
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

  const renderContent = () => {
    // Placeholder for content rendering based on serverInfo
    // You need to adjust this logic based on how serverInfo is structured
    return <div>{serverInfo[selectedMenuItem.toLowerCase()]}</div>;
  };

  return (
    <div className="popup-overlay" onClick={onClose}>
      <div className="popup-container" onClick={(e) => e.stopPropagation()}>
        <div className="side-menu">
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
        <div className="content-area">{renderContent()}</div>
      </div>
    </div>
  );
};

export default DetailsPopup;
