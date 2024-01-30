// App.js
import "./App.css";
import TextBox from "./components/TextBox/textbox";
import React, { useEffect, useState } from "react";
import ServerTab from "./components/ServerTab/serverTab";
import ServerDetailsTable from "./components/Table/serverDetailsTable";

const App = () => {
  const [results, setResults] = useState([]);

  useEffect(() => {
    // Establish a connection to the SSE endpoint when the component mounts
    const eventSource = new EventSource(
      "http://localhost:8000/myApp/process_servers/"
    );

    eventSource.onmessage = (event) => {
      const eventData = JSON.parse(event.data);
      setResults((prevResults) => [...prevResults, eventData]);
    };

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
      // eventSource.close();
    };

    // Clean up event source when the component unmounts
    // return () => {
    //   console.log("Closing");
    //   eventSource.close();
    // };
  }, []);

  const handleSubmit = async (serverList) => {
    const serverNames = serverList.split(/\r?\n/);
    const serverResults = {};
    console.log(serverNames);
    console.log(JSON.stringify({ serverNames }));

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

      const responseData = await response.json();

      serverNames.forEach((server) => {
        serverResults[server] = responseData[server] || {
          state: "checking",
          details: `Checking ${server}...`,
        };
      });

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
      {results && (
        <>
          <div className="output-container">
            {Object.keys(results).map((server) => (
              <ServerTab
                key={server}
                serverName={server}
                serverInfo={results[server]}
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
