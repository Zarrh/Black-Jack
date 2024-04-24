import express from 'express';
import { PORT } from './config.js';
import path from 'path';

const __dirname = path.resolve(); // Root

const app = express();
let image = null;
let dealer = {
    cards: ["Ks", "As"],
};
let players = [
    {name: "John", pot: 500, cards: [], position: "1"}, 
    {name: "Ben", pot: 500, cards: [], position: "2"}, 
    {name: "Tim", pot: 500, cards: [], position: "3"}, 
]; // Players list

app.use(express.static(path.join(__dirname, '../front-end/dist'))); // UI files

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../front-end', 'dist', 'index.html'));
}); // Sending default UI

app.get('/send-players-app', (req, res) => {
    res.json({ players: players, dealer: dealer });
}); // Sending players and dealer to app

app.post('/get-pots-py', (req, res) => {
    const { pots } = req.query;
    if (!pots) {
        return res.status(400).json({ error: { message: 'Pots are required' } });
    }
    players.forEach((player, index) => (
        player["pot"] = pots[index]
    ));
    return res.status(200).json({ pots });
}); // Receive and save the pots

app.post('/get-image-py', (req, res) => {
    const { payload } = req.query;
    if (!payload) {
        return res.status(400).json({ error: { message: 'No image received' } });
    }
    image = payload;
    return res.status(200);
}); // Receive the image

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