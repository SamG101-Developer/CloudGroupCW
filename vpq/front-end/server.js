'use strict';

//Set up express
const express = require('express');
const app = express();

//Setup socket.io
const server = require('http').Server(app);
const io = require('socket.io')(server);

//Setup static page handling
app.set('view engine', 'ejs');
app.use('/static', express.static('public'));

//Handle client interface on /
app.get('/', (req, res) => {
    res.render('client');
});
//Handle display interface on /display
// app.get('/display', (req, res) => {
//     res.render('display');
// });

// URL of the backend API
// TODO: Add the URL of the function app
const BACKEND_ENDPOINT = process.env.BACKEND || 'http://localhost:8181';

//Start the server
function startServer() {
    const PORT = process.env.PORT || 8080;
    server.listen(PORT, () => {
        console.log(`Server listening on port ${PORT}`);
    });
}

//Chat message
function handleChat(message) {
    console.log('Handling chat: ' + message);
    io.emit('chat',message);
}

//Handle new connection
io.on('connection', socket => {
    console.log('New connection');

    //Handle on chat message received
    socket.on('chat', message => {
        handleChat(message);
    });

    //Handle disconnection
    socket.on('disconnect', () => {
        console.log('Dropped connection');
    });

    //Handle register
    socket.on('register', () => {
        console.log('Registering');
    });

    //Handle login
    socket.on('login', () => {
        console.log('Logging in');
    });

    //Handle add friend
    socket.on('add_friend', () => {
        console.log('Adding a friend');
    });

    //Handle delete friend
    socket.on('del_friend', () => {
        console.log('Deleting a friend');
    });

    //Handle add favourite quiz
    socket.on('add_favourite_quiz', () => {
        console.log('Adding a favourite quiz');
    });

    //Handle delete favourite quiz
    socket.on('del_favourite_quiz', () => {
        console.log('Deleting a favourite quiz');
    });

    //Handle create room
    socket.on('create_room', () => {
        console.log('Creating a room');
    });

    //Handle join room
    socket.on('join_room', () => {
        console.log('Joining a room');
    });

    //Handle leave room
    socket.on('leave_room', () => {
        console.log('Leaving a room');
    });

    //Handle use power up
    socket.on('use_power_up', () => {
        console.log('Using a power up');
    });

    //Handle create quiz
    socket.on('create_quiz', () => {
        console.log('Creating a quiz');
    });

    //Handle delete quiz
    socket.on('delete_quiz', () => {
        console.log('Deleting a quiz');
    });

    //Handle update quiz
    socket.on('update_quiz', () => {
        console.log('Updating a quiz');
    });
});

//Start server
if (module === require.main) {
    startServer();
}

module.exports = server;
