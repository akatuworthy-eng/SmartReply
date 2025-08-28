import { useEffect, useState } from "react";
import logo from './logo.svg';
import './App.css';

function App() {
  const [message, setMessage] = useState("Loading...");

  useEffect(() => {
    // Call your backend API when the component loads
    fetch("https://smartreply-production.up.railway.app")
      .then((res) => res.json()) // assume backend sends JSON
      .then((data) => {
        // Example: backend returns { message: "Hello from backend" }
        setMessage(data.message);
      })
      .catch((err) => {
        console.error("Error fetching from backend:", err);
        setMessage("Error connecting to backend");
      });
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>{message}</p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}

export default App;
