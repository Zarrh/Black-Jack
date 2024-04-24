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
  const [players, setPlayers] = useState([{cards: ['As', 'Ks', '3c'], position: "2", pot: 500}, {cards: ['Qs', 'Qh'], position: "3", pot: 1000}, {cards: ['7h', '8s', '2c'], position: "1", pot: 200}]); // TODO: put empty array
  const [dealer, setDealer] = useState({cards: ['Kh', '2s', '3s']}); // TODO: put empty object
  const [deck, setDeck] = useState([
    'Ac', 'Kc', 'Qc', 'Jc', '10c', '9c', '8c', '7c', '6c', '5c', '4c', '3c', '2c', 
    'Ad', 'Kd', 'Qd', 'Jd', '10d', '9d', '8d', '7d', '6d', '5d', '4d', '3d', '2d', 
    'Ah', 'Kh', 'Qh', 'Jh', '10h', '9h', '8h', '7h', '6h', '5h', '4h', '3h', '2h', 
    'As', 'Ks', 'Qs', 'Js', '10s', '9s', '8s', '7s', '6s', '5s', '4s', '3s', '2s', 
  ]); // Todo: remove //

  const cardMap = {
    "Ac": CAc, "Kc": CKc, "Qc": CQc, "Jc": CJc, "10c": C10c, "9c": C9c, "8c": C8c, "7c": C7c, "6c": C6c, "5c": C5c, "4c": C4c, "3c": C3c, "2c": C2c,
    "Ad": CAd, "Kd": CKd, "Qd": CQd, "Jd": CJd, "10d": C10d, "9d": C9d, "8d": C8d, "7d": C7d, "6d": C6d, "5d": C5d, "4d": C4d, "3d": C3d, "2d": C2d,
    "Ah": CAh, "Kh": CKh, "Qh": CQh, "Jh": CJh, "10h": C10h, "9h": C9h, "8h": C8h, "7h": C7h, "6h": C6h, "5h": C5h, "4h": C4h, "3h": C3h, "2h": C2h,
    "As": CAs, "Ks": CKs, "Qs": CQs, "Js": CJs, "10s": C10s, "9s": C9s, "8s": C8s, "7s": C7s, "6s": C6s, "5s": C5s, "4s": C4s, "3s": C3s, "2s": C2s
  };

  const cardPositions = {
    "Dealer": [["50%", "5%"], ["40%", "5%"], ["60%", "5%"]], // Dealer's positions
    "1": [["15%", "50%"], ["19%", "43%"], ["24%", "34%"]], // 1
    //"2": [["30%", "77%"], ["33%", "65%"], ["36%", "53%"]], // 2
    "2": [["50%", "87%"], ["50%", "74%"], ["50%", "61%"]], // 3
    //"4": [["70%", "77%"], ["67%", "65%"], ["64%", "53%"]], // 4
    "3": [["85%", "50%"], ["81%", "43%"], ["76%", "34%"]], // 5
  }; // Positions of the cards //

  const potPositions = {
    "1": ["5%", "79%"],
    "2": ["50%", "125%"],
    "3": ["95%", "79%"],
  }; // Positions of the pots //

  const cardAngles = {
    "Dealer": "0", // Dealer's angle
    "1": "51", // 1
    //"2": "27", // 2
    "2": "0", // 3
    //"4": "-27", // 4
    "3": "-51", // 5
  }; // Angles of the positions //

  useEffect(() => {

    const fetchPlayers = async () => {
      try {
        const response = await fetch('/send-players-app');
        const data = await response.json();
        setPlayers(data.players);
        setDealer(data.dealer);
      } catch (error) {
        console.error('Error fetching players:', error);
      }
    };

    fetchPlayers();
    const interval = setInterval(fetchPlayers, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <h1><span style={{color: "#303030"}}>&#9824;</span><span style={{color: "#e60000"}}>&#9830;</span> Black Jack <span style={{color: "#303030"}}>&#9827;</span><span style={{color: "#e60000"}}>&#9829;</span></h1>

      <h1 className="subtitle">Fagaraz Luca, Viezzer Tommaso, Zanco Simone</h1>

      <div className="table-container">
        <Table />
        {dealer["cards"].map((card, i) => (
          <Card key={i} image={cardMap[card]} zIndex={i} position={[cardPositions["Dealer"][i % dealer["cards"].length][0], cardPositions["Dealer"][i % dealer["cards"].length][1]]} angle={cardAngles["Dealer"]} />
        ))}
         
        {players.map((player, index) => (
          <div key={index}>
            {player.cards.map((card, i) => (
              <Card key={i} image={cardMap[card]} zIndex={i} position={[cardPositions[player.position][i % player.cards.length][0], cardPositions[player.position][i % player.cards.length][1]]} angle={cardAngles[player.position]} />
            ))}
            <div style={{
              position: "absolute", 
              left: potPositions[player.position][0], 
              top: potPositions[player.position][1], 
              zIndex: 100, 
              transform: `translate(-50%, +25%) rotate(${cardAngles[player.position]}deg)`,
              fontSize: 50,
              fontWeight: "bold"
            }}>
              {player["pot"]}$
            </div>
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
