import express from 'express';
import bodyParser from 'body-parser';
import path from 'path';

const __dirname = path.resolve(); // Root
const PORT = 5555; // Port
const adminKey = "7hAs$"; // Admin reset key

const app = express();

let dealer = {
    cards: [],
    state: null,
};

let players = [
    {name: "John", pot: null, bet: 0, cards: [], position: "1", "state": null}, 
    {name: "Ben", pot: null, bet: 0, cards: [], position: "2", "state": null}, 
    {name: "Tim", pot: null, bet: 0, cards: [], position: "3", "state": null}, 
]; // Players list

let mode = null; // Part of the game

app.use(bodyParser.json())
app.use(express.static(path.join(__dirname, '../front-end/dist'))); // UI files

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../front-end', 'dist', 'index.html'));
}); // Sending default client UI

app.get('/send-players', (req, res) => {
    res.json({ players: players, dealer: dealer });
}); // Sending players and dealer to app and py

app.get('/send-pots', (req, res) => {
    let pots = [];
    players.forEach((player, index) => (
        pots.push(player["pot"])
    ));
    res.json({ pots: pots });
}); // Sending pots to table

app.post('/get-cards', (req, res) => {
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

app.post('/get-pots', (req, res) => {
    const { pots } = req.body;
    if (!pots) {
        return res.status(400).json({ error: { message: 'Pots are required' } });
    }
    players.forEach((player, index) => (
        player["pot"] = pots[index+1]
    ));
    return res.status(200).json({ pots });
}); // Receive and save the pots

app.post('/get-bets', (req, res) => {
    const { bets } = req.body;
    if (!bets) {
        return res.status(400).json({ error: { message: 'Bets are required' } });
    }
    players.forEach((player, index) => (
        player["bet"] = bets[index+1]
    ));
    return res.status(200).json({ bets });
}); // Receive and save the bets

app.post('/get-states', (req, res) => {
    const { states } = req.body;
    if (!states) {
        return res.status(400).json({ error: { message: 'States are required' } });
    }
    players.forEach((player, index) => (
        player["state"] = states[index+1]
    ));
    dealer["state"] = states["Dealer"];
    return res.status(200).json({ states });
}); // Receive and save the states

app.get('/send-mode', (req, res) => {
    res.json({ mode: mode });
}); // Send mode

app.post('/get-mode', (req, res) => {
    const { data } = req.body;
    if (data === null) {
        return res.status(400).json({ error: { message: 'Mode is required' } });
    }
    mode = data;
    return res.status(200).json({ data });
}); // Receiving the mode from the table

app.post('/reset', (req, res) => {
    const { key } = req.body;
    if (!key) {
        return res.status(400).json({ error: { message: 'You are not allowed to perform this action' } });
    }
    if (key === adminKey) {
        players.forEach((player, index) => {
            player["state"] = "playing";
            player["bet"] = 0;
            player["cards"] = [];
        });
        dealer["state"] = "playing";
        dealer["cards"] = [];
    }
    return res.status(200).json({ players });
});

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