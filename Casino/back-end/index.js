import express from 'express';
import { PORT } from './config.js';
import path from 'path';

const __dirname = path.resolve(); // Root

const app = express();
let image = null;
let previousNumber = 0; // Just for testing purposes
let players = [
    {name: "John", pot: 100, cards: [], position: 1}, 
    {name: "Ben", pot: 100, cards: [], position: 2}, 
    {name: "Tim", pot: 100, cards: [], position: 3}, 
    {name: "Ian", pot: 100, cards: [], position: 4}, 
    {name: "Luke", pot: 100, cards: [], position: 5}
]; // Players list
let isDeckPresent = false; // Deck's presence

app.use(express.static(path.join(__dirname, '../front-end/dist'))); // UI files

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../front-end', 'dist', 'index.html'));
}); // Sending default UI

// === Just for testing purposes === //

app.get('/send-number-app', (req, res) => {
    res.json({ number: previousNumber });
});

app.post('/get-number-py', (req, res) => {
    const { number } = req.query;
    if (!number) {
        return res.status(400).json({ error: { message: 'Number is required' } });
    }
    previousNumber = number;
    return res.status(200).json({ number });
});

// === === //

app.get('/send-players-app', (req, res) => {
    res.json({ players: players });
}); // Sending players to app

app.get('/send-deckPresent-app', (req, res) => {
    res.json({ presence: isDeckPresent });
}); // Sending deck's presence to app

app.post('/get-deckPresent', (req, res) => {
    const { payload } = req.query;
    if (!payload) {
        return res.status(400).json({ error: { message: 'No data received' } });
    }
    isDeckPresent = payload;
    return res.status(200);
}); // Receiving the deck's presence

app.post('/get-image', (req, res) => {
    const { payload } = req.query;
    if (!payload) {
        return res.status(400).json({ error: { message: 'No image received' } });
    }
    image = payload;
    return res.status(200);
}); // Receiving the image

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