// App.js
import "./App.css";
import TextBox from "./components/TextBox/textbox";
import React, { useState } from "react";
import ServerTab from "./components/ServerTab/serverTab";
import ServerDetailsTable from "./components/Table/serverDetailsTable";

const App = () => {
  const [results, setResults] = useState(null);

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
