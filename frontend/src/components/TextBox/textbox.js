import React, { useState } from "react";
import "./textbox.css";

const TextBox = ({ onSubmit }) => {
  const [serverList, setServerList] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(serverList);
  };

  return (
    <div className="form-container">
      <form onSubmit={handleSubmit}>
        <label>
          Server List:
          <textarea
            value={serverList}
            onChange={(e) => setServerList(e.target.value)}
            placeholder="Paste Your Server List Here. One Server Per Line"
          />
        </label>
        <button type="submit">Check Servers</button>
      </form>
    </div>
  );
};

export default TextBox;
