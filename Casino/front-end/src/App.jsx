import React, { useState, useEffect } from 'react';
import './App.css';
//import { Table } from './assets';
import Table from './components/Table';

function App() {
  const [number, setNumber] = useState(null);
  const [players, setPlayers] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('/send-number-app');
        const data = await response.json();
        setNumber(data.number);
      } catch (error) {
        console.error('Error fetching number:', error);
      }
    }; // Just for testing purposes

    const fetchPlayers = async () => {
      try {
        const response = await fetch('/send-players-app');
        const data = await response.json();
        setPlayers(data.players);
      } catch (error) {
        console.error('Error fetching players:', error);
      }
    };

    fetchData(); // Just for testing purposes
    fetchPlayers();
    const interval = setInterval(fetchData, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <h1><span style={{color: "#303030"}}>&#9824;</span><span style={{color: "#e60000"}}>&#9830;</span> Black Jack <span style={{color: "#303030"}}>&#9827;</span><span style={{color: "#e60000"}}>&#9829;</span></h1>

      <h1 className="subtitle">Fagaraz Luca, Viezzer Tommaso, Zanco Simone</h1>

      <div className="table-container">
        <Table />
      </div>

      {number !== null ? (
        <p>Number received from server: {number}</p>
      ) : (
        <p>Loading...</p>
      ) // Just for testing purposes
      }

      <div className="players-container">
        {players.map((player, index) => (
          <div key={index}>
            <p>{player.name}</p>
          </div>
        ))}
      </div>

      <div className="footer-container">
        Fagaraz Luca, Viezzer Tommaso, Zanco Simone
      </div>
    </>
  );
}

export default App;
