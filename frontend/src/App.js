// App.js
import "./App.css";
import TextBox from "./components/TextBox/textbox";
import React, { useEffect, useState } from "react";
import ServerTab from "./components/ServerTab/serverTab";
import ServerDetailsTable from "./components/Table/serverDetailsTable";
import { v4 as uuidv4 } from "uuid";

const App = () => {
  const [results, setResults] = useState([]);

  useEffect(() => {
    setResults([]);
    console.log("USE EFFECT RUNNING");
    // Establish a connection to the SSE endpoint when the component mounts
    const connectionId = uuidv4();

    const eventSource = new EventSource(
      `http://localhost:8000/myApp/process_servers/?id=${connectionId}`
    );

    eventSource.onmessage = (event) => {
      const eventData = JSON.parse(event.data);
      setResults((prevResults) => [...prevResults, eventData]);
      console.log(results);
    };
    console.log(results.length);

    console.log(eventSource);
    // Event listener for incoming messages
    eventSource.onopen = () => {
      console.log("SSE connection opened");
    };

    // Event listener for errors
    eventSource.onerror = (error) => {
      console.error("EventSource error:", error);
      console.error("ReadyState:", eventSource.readyState);
      // readyState values: 0-CONNECTING, 1-OPEN, 2-CLOSED
      eventSource.close();
    };

    // Clean up event source when the component unmounts
    return () => {
      console.log("Closing Eventsource");
      eventSource.close();
    };
  }, []);

  const handleSubmit = async (serverList) => {
    const serverNames = serverList.split(/\r?\n/);
    const serverResults = serverNames.map((server) => ({
      serverName: server,
      status: "checking",
      details: `Checking ${server}...`,
    }));
    console.log(serverResults);
    console.log(serverNames);
    console.log(JSON.stringify({ serverNames }));
    console.log(results.length);

    try {
      const response = await fetch(
        "http://localhost:8000/myApp/process_servers/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ serverNames }),
        }
      );
      console.log(response);
      console.log(response.body);

      if (!response.ok) {
        throw new Error("Server error");
      }

      setResults(serverResults);
    } catch (error) {
      console.error("Error sending POST request:", error);
      console.log(error);
    }
  };

  return (
    <div className="App">
      <h1>Linux Server Health Checker</h1>
      <div className="container">
        <TextBox onSubmit={handleSubmit} />
      </div>
      {results.length > 0 && (
        <>
          <div className="output-container">
            {results.map((server) => (
              <ServerTab
                key={server.serverName}
                serverName={server.serverName}
                serverInfo={server}
              />
            ))}
          </div>
          <div className="table-container">
            <ServerDetailsTable serverInfo={results} />
          </div>
        </>
      )}
    </div>
  );
};

export default App;
