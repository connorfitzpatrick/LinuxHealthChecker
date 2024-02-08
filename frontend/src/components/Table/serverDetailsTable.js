// ServerDetailsTable.js
import React, { useRef, useState } from "react";
import "./serverDetailsTable.css";

const ServerDetailsTable = ({ serverInfo }) => {
  const tableRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [startX, setStartX] = useState(0);

  const onMouseDown = (e) => {
    setIsDragging(true);
    setStartX(e.pageX - tableRef.current.offsetLeft);
    tableRef.current.style.cursor = "grabbing";
  };

  const onMouseMove = (e) => {
    if (!isDragging) return;
    const x = e.pageX - tableRef.current.offsetLeft;
    const scroll = x - startX;
    tableRef.current.scrollLeft -= scroll;
    setStartX(x);
  };

  const onMouseUpOrLeave = () => {
    setIsDragging(false);
    tableRef.current.style.cursor = "grab";
  };

  return (
    <div
      className="table-holder"
      ref={tableRef}
      onMouseDown={onMouseDown}
      onMouseMove={onMouseMove}
      onMouseUp={onMouseUpOrLeave}
      onMouseLeave={onMouseUpOrLeave}
      style={{ cursor: "grab" }}
    >
      <table>
        <thead>
          <tr>
            <th>Hostname</th>
            <th>Ping Status</th>
            <th>OS Version</th>
            <th>Inode Usage</th>
            <th>Filesystems</th>
            <th>CPU Usage</th>
            <th>NTP Service</th>
            <th>Users Logged In</th>
            <th>Process Health</th>
          </tr>
        </thead>
        <tbody>
          {serverInfo.map((server) => (
            <tr
              key={server.serverName}
              className={
                server.status.overall_state === "Healthy"
                  ? "row-healthy"
                  : server.status.overall_state === "Error"
                  ? "row-error"
                  : ""
              }
            >
              <td>{server.serverName}</td>
              <td>{server.status.overall_state}</td>
              <td>{server.status.os_info.operating_system_name}</td>
              <td>{server.status.inode_info.inode_health_status}</td>
              <td>{server.status.filesystem_info.filesystem_health_status}</td>
              <td>{}</td>
              <td>{}</td>
              <td>{}</td>
              <td>{}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ServerDetailsTable;
