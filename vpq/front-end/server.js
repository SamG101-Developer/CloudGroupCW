'use strict';

//Set up express
const express = require('express');
const app = express();

// Setup request
const request = require("request");

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
const BACKEND_ENDPOINT = process.env.BACKEND || 'http://localhost:7071';
console.log(BACKEND_ENDPOINT); 

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

/*
All backend requests work using promises.
A backend request can be done by providing:
- A path ("playerAdd", "playerDel", etc)
- A body ({username: "user", password: "pass"}, etc)

Here is a use example:
backendGET("/api/playerAdd", {}).then(
    function(response) {
        console.log("Success:", response);
    },
    function (error) {
        console.error("Error:", error);
    }
);
*/

function backendGET(path, body) {
    console.log(BACKEND_ENDPOINT + path);
	return new Promise((success, failure) => {
		request.get(BACKEND_ENDPOINT + path, {
			json: true,
			body: body
		}, function(err, response, body) {
            if (err) {
                failure(err);
            } else {
			    success(body);
            }
		});
	});
}

function backendPOST(path, body) {
	return new Promise((success, failure) => {
		request.post(BACKEND_ENDPOINT + path, {
			json: true,
			body: body
		}, function(err, response, body) {
            if (err) {
                failure(err);
            } else {
			    success(body);
            }
		});
	});
}

/*
Alternatively, backend requests could work with a callback function (which is called when a response is recieved)
If you would like to use a callback based function, this is the code:

function backendGETCallback(path, body, callback) {
	request.get(BACKEND_ENDPOINT + path, {
		json: true,
		body: body
  	}, function(err, response, body) {
		callback(body);
  	});
}

This can be used as per this example: 
backendGET("/api/playerAdd", json, function(response) {
    console.log(response);
});
*/

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
    socket.on('register', (registerJSON) => {
        console.log(`Registering with username '${registerJSON.username}' and password '${registerJSON.password}'`);

        backendPOST("/api/playerAdd", registerJSON).then(
            function(response) {
                console.log("Success:");
                console.log(response);
            },
            function (error) {
                console.error("Error:");
                console.error(error);
            }
        );
    });

    //Handle login
    socket.on('login', (loginJSON) => {
        console.log(`Logging in with username '${loginJSON.username}' and password '${loginJSON.password}'`);

        backendGET("/api/playerLogin", loginJSON).then(
            function(response) {
                console.log("Success:");
                console.log(response);
            },
            function (error) {
                console.error("Error:");
                console.error(error);
            }
        );
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
