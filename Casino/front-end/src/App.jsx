import React, { useState, useEffect } from 'react';
import './App.css';
import Table from './components/Table';
import Card from './components/Card';
import { 
  CAc, CKc, CQc, CJc, C10c, C9c, C8c, C7c, C6c, C5c, C4c, C3c, C2c, 
  CAd, CKd, CQd, CJd, C10d, C9d, C8d, C7d, C6d, C5d, C4d, C3d, C2d, 
  CAh, CKh, CQh, CJh, C10h, C9h, C8h, C7h, C6h, C5h, C4h, C3h, C2h, 
  CAs, CKs, CQs, CJs, C10s, C9s, C8s, C7s, C6s, C5s, C4s, C3s, C2s, 
  back 
} from './assets';

function App() {
  const [number, setNumber] = useState(null);
  const [players, setPlayers] = useState([{cards: ['As', 'Ks']}]); // TODO: put empty array
  const [deck, setDeck] = useState([
    'Ac', 'Kc', 'Qc', 'Jc', '10c', '9c', '8c', '7c', '6c', '5c', '4c', '3c', '2c', 
    'Ad', 'Kd', 'Qd', 'Jd', '10d', '9d', '8d', '7d', '6d', '5d', '4d', '3d', '2d', 
    'Ah', 'Kh', 'Qh', 'Jh', '10h', '9h', '8h', '7h', '6h', '5h', '4h', '3h', '2h', 
    'As', 'Ks', 'Qs', 'Js', '10s', '9s', '8s', '7s', '6s', '5s', '4s', '3s', '2s', 
  ]);
  const [deckPresent, setDeckPresent] = useState(1); // TODO: put 0

  const cardMap = {
    "Ac": CAc, "Kc": CKc, "Qc": CQc, "Jc": CJc, "10c": C10c, "9c": C9c, "8c": C8c, "7c": C7c, "6c": C6c, "5c": C5c, "4c": C4c, "3c": C3c, "2c": C2c,
    "Ad": CAd, "Kd": CKd, "Qd": CQd, "Jd": CJd, "10d": C10d, "9d": C9d, "8d": C8d, "7d": C7d, "6d": C6d, "5d": C5d, "4d": C4d, "3d": C3d, "2d": C2d,
    "Ah": CAh, "Kh": CKh, "Qh": CQh, "Jh": CJh, "10h": C10h, "9h": C9h, "8h": C8h, "7h": C7h, "6h": C6h, "5h": C5h, "4h": C4h, "3h": C3h, "2h": C2h,
    "As": CAs, "Ks": CKs, "Qs": CQs, "Js": CJs, "10s": C10s, "9s": C9s, "8s": C8s, "7s": C7s, "6s": C6s, "5s": C5s, "4s": C4s, "3s": C3s, "2s": C2s
  };

  const cardPositions = {
    "Deck": ["50%", "5%"], // Deck's position
    "1": [["50%", "5%"]], // 1
    "2": [["50%", "5%"]], // 2
    "3": [["50%", "87%"], ["50%", "74%"], ["50%", "61%"]], // 3
    "4": [["50%", "5%"]], // 4
    "5": [["50%", "5%"]], // 5
  };

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

    const fetchDeck = async () => {
      try {
        const response = await fetch('/send-deckPresent-app');
        const data = await response.json();
        setDeckPresent(data.presence);
      } catch (error) {
        console.error('Error fetching presence of deck:', error);
      }
    };

    fetchData(); // Just for testing purposes
    fetchPlayers();
    fetchDeck();
    const interval = setInterval(fetchData, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <h1><span style={{color: "#303030"}}>&#9824;</span><span style={{color: "#e60000"}}>&#9830;</span> Black Jack <span style={{color: "#303030"}}>&#9827;</span><span style={{color: "#e60000"}}>&#9829;</span></h1>

      <h1 className="subtitle">Fagaraz Luca, Viezzer Tommaso, Zanco Simone</h1>

      <div className="table-container">
        <Table />
        {deckPresent && (
          <Card image={back} zIndex={2} x={cardPositions["3"][1][0]} y={cardPositions["3"][1][1]} />
        )}
         
        {players.map((player, index) => (
          <div key={index}>
            {player.cards.map((card, i) => (
              <Card key={i} image={cardMap[card]} zIndex={1} x={cardPositions["Deck"][0]} y={cardPositions["Deck"][1]} />
            ))}
          </div>
        ))}
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
