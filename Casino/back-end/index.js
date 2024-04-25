import express from 'express';
import bodyParser from 'body-parser';
import { PORT } from './config.js';
import path from 'path';

const __dirname = path.resolve(); // Root

const app = express();

let dealer = {
    cards: [],
};

let players = [
    {name: "John", pot: 0, cards: [], position: "1"}, 
    {name: "Ben", pot: 0, cards: [], position: "2"}, 
    {name: "Tim", pot: 0, cards: [], position: "3"}, 
]; // Players list

app.use(bodyParser.json())
app.use(express.static(path.join(__dirname, '../front-end/dist'))); // UI files

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../front-end', 'dist', 'index.html'));
}); // Sending default UI

app.get('/send-players-app', (req, res) => {
    res.json({ players: players, dealer: dealer });
}); // Sending players and dealer to app

app.post('/get-cards-cam', (req, res) => {
    const { data } = req.body;
    if (!data) {
        return res.status(400);
    }

    data.forEach(({ card, position }) => {
        const isCardAlreadyPresent = dealer.cards.includes(card) || players.some(player => player.cards.includes(card));
        if (!isCardAlreadyPresent) {
            if (position === "Dealer") {
                dealer.cards.push(card);
            }
            else {
                const player = players.find(player => player.position == position);
                if (player) {
                    player.cards.push(card);
                }
            }
        }
    });
    return res.status(200).json({ players });
}); // Receive and save the cards

app.post('/get-pots-py', (req, res) => {
    const { pots } = req.body;
    if (!pots) {
        return res.status(400).json({ error: { message: 'Pots are required' } });
    }
    players.forEach((player, index) => (
        player["pot"] = pots[index + 1]
    ));
    return res.status(200).json({ pots });
}); // Receive and save the pots

app.use((req, res, next) => {
    const error = new Error('Resource not found');
    error.status = 404;
    next(error);
}); // Error get requests routing

app.use((err, req, res, next) => {
    res.status(err.status || 500);
    res.json({
      error: {
        message: err.message
      }
    });
}); // Error handling

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});