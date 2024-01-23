// App.js
import "./App.css";
import TextBox from "./components/TextBox/textbox";
import React, { useState } from "react";
import ServerTab from "./components/ServerTab/serverTab";

const App = () => {
  const [results, setResults] = useState(null);

  const handleSubmit = async (serverList) => {
    const serverNames = serverList.split(/\r?\n/);
    const serverResults = {};

    // Implement logic to send serverList to the Python backend
    // and update the serverResults object with the response
    // (You might use the Fetch API or Axios for this)

    // For now, let's simulate a response for each server
    serverNames.forEach((server) => {
      serverResults[server] = {
        state: "checking",
        details: `Checking ${server}...`,
      };
    });

    setResults(serverResults);
  };

  return (
    <div className="App">
      <h1>Linux Server Health Checker</h1>
      <div className="container">
        <TextBox onSubmit={handleSubmit} />
      </div>
      {results && (
        <div className="output-container">
          {Object.keys(results).map((server) => (
            <ServerTab
              key={server}
              serverName={server}
              serverInfo={results[server]}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default App;
