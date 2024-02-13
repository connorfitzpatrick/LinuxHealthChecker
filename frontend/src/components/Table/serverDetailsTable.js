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
          {serverInfo.map((server) => {
            const overallState = server.status.overall_state;
            const pingState = server.status.ping_status;
            const filesystemStatus =
              server.status.filesystem_info.filesystem_health_status;
            const inodeStatus = server.status.inode_info.inode_health_status;
            const cpuUseStatus =
              server.status.cpu_use_info.cpu_use_health_status;

            const rowClass = (() => {
              if (pingState === "Healthy") return "row-healthy";
              if (overallState === "Healthy") return "row-healthy";
              if (overallState === "Error") return "row-error";
              return "";
            })();

            const overallWarning = overallState === "Warning";
            const filesystemWarning = filesystemStatus === "Warning";
            const inodeWarning = inodeStatus === "Warning";
            const cpuUseWarning = cpuUseStatus == "Warning";

            return (
              <tr key={server.serverName} className={rowClass}>
                <td className={overallWarning ? "cell-warning" : ""}>
                  {server.serverName}
                </td>
                <td>{server.status.os_info.operating_system_name}</td>
                <td>{server.status.ping_status}</td>
                <td className={inodeWarning ? "cell-warning" : ""}>
                  {inodeStatus}
                </td>
                <td className={filesystemWarning ? "cell-warning" : ""}>
                  {filesystemStatus}
                </td>
                <td className={cpuUseWarning ? "cell-warning" : ""}>
                  {cpuUseStatus}
                </td>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default ServerDetailsTable;
