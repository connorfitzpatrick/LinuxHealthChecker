// ServerDetailsTable.js
import React from "react";
import "./serverDetailsTable.css";

const ServerDetailsTable = ({ serverInfo }) => {
  return (
    <div className="table-holder">
      <table>
        <thead>
          <tr>
            <th>Hostname</th>
            <th>OS Version</th>
            <th>Ping Status</th>
            <th>Inode Usage</th>
            <th>Filesystems</th>
            <th>CPU Usage</th>
            <th>NTP Service</th>
            <th>Users Logged In</th>
            <th>Process Health</th>
          </tr>
        </thead>
        <tbody>
          {Object.keys(serverInfo).map((serverName) => (
            <tr key={serverName}>
              <td>{serverName}</td>
              {/* Add more cells with server information */}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ServerDetailsTable;
