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

let all_players_sockets = {};

// URL of the backend API
// TODO: Add the URL of the function app
const BACKEND_ENDPOINT = process.env.BACKEND || 'http://localhost:7071';
console.log(process.env.BACKEND);
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
    io.emit('chat', message);
}

//User Deletion
function handleDeleteUser(delUserJSON) {
    console.log(`Deleting user '${delUserJSON.username}'`);

    let url = "/api/playerDel?code=" + process.env.FUNCTION_APP_KEY;
    backendDELETE(url, delUserJSON).then(
        function(response) {
            console.log("Success:");
            console.log(response);
        },
        function (error) {
            console.error("Error:");
            console.error(error);
        }
    );
}

//Player Login
function handleLogin(socket, loginJSON){
    console.log(`Logging in with username '${loginJSON.username}' and password '${loginJSON.password}'`);

    let url = "/api/playerLogin?code=" + process.env.FUNCTION_APP_KEY;
    backendGET(url, loginJSON).then(
        function(response) {
            console.log("Success:");
            console.log(response);

            if (response["result"]) {
                all_players_sockets[loginJSON.username] = socket;
                socket.emit("confirm_login", loginJSON)
            }
            else {
                socket.emit("error", response["msg"])
            }
        },
        function (error) {
            console.error("Error:");
            console.error(error);
        }
    );
}

function handleLogout(info) {
    console.log(`Logging out user '${info.username}'`);

    delete all_players_sockets[info.username];
}

//Player Register
function handleRegister(socket, registerJSON){
    console.log(`Registering with username '${registerJSON.username}' and password '${registerJSON.password}'`);

    let url = "/api/playerAdd?code=" + process.env.FUNCTION_APP_KEY;
    backendPOST(url, registerJSON).then(
        function(response) {
            console.log("Success:");
            console.log(response);
            if (response["result"]) {
                socket.emit("confirm_register", registerJSON)
            }
            else {
                socket.emit("error", response["msg"])
            }

        },
        function (error) {
            console.error("Error:");
            console.error(error);
        }
    );
}

//Player Add Friend
function handleAddFriend(addFriendJSON){
    console.log(`Adding friend '${addFriendJSON.friendUsername}' for user '${addFriendJSON.username}'`);

    let url = "/api/playerFriendAdd?code=" + process.env.FUNCTION_APP_KEY;
    backendPUT(url, addFriendJSON).then(
        function(response) {
            console.log("Success:");
            console.log(response);
            handleUpdateFriends(all_players_sockets[addFriendJSON.username], addFriendJSON);
        },
        function (error) {
            console.error("Error:");
            console.error(error);
        }
    );
}

//Player Delete Friend
function handleDeleteFriend(delFriendJSON){
    console.log(`Deleting friend '${delFriendJSON.friendUsername}' for user '${delFriendJSON.username}'`);

    let url = "/api/playerFriendDel?code=" + process.env.FUNCTION_APP_KEY;
    backendPUT(url, delFriendJSON).then(
        function(response) {
            console.log("Success:");
            console.log(response);
            handleUpdateFriends(all_players_sockets[delFriendJSON.username], delFriendJSON);
        },
        function (error) {
            console.error("Error:");
            console.error(error);
        }
    );
}

//Player update friends
function handleUpdateFriends(socket, info) {
    const username = info["username"];
    console.log('Updating friends list for user ' + username);

    backendGET("/api/playerInfoGet", info).then(
        function(response) {
            console.log("Success:");
            console.log(response);

            socket.emit("update_friends", response.body.friends);
        },
        function (error) {
            console.error("Error:");
            console.error(error);
        }
    );
}

//Player Get Questions
function handleGetPlayerQuestions(socket, getQuestionsJSON){
    console.log(`Getting questions for user '${getQuestionsJSON.username}'`);

    // First get a list of all the id's for the user
    // Next get all question data for each question ID
    //Finally, send it to the client
    let url = "/api/playerQuestionGroupsGet?code=" + process.env.FUNCTION_APP_KEY;
    backendGET(url, getQuestionsJSON).then(
        async function(response) {
            console.log("Success:");
            console.log(response);
            let questionIds = response['body'];
            let questionsRetrieved = [];
            // For each ID get all the question data and save it to an array
            for (let id of questionIds){
                let url = "/api/questionGet?code=" + process.env.FUNCTION_APP_KEY;
                await backendGET(url, id).then(
                    function(response) {
                        console.log("Success:");
                        console.log(response);
                        let questionData = response["body"];
                        questionsRetrieved.push({
                            questionType: questionData["question_type"],//"Multiple Choice",
                            questionText: questionData["question"],
                            answer: questionData["correct_answer"],
                            options: questionData["answers"]
                        })
                    },
                    function (error) {
                        console.error("Error:");
                        console.error(error);
                    }
                );
            }
            console.log(questionsRetrieved);
            socket.emit('queried_questions', questionsRetrieved);
        },
        function (error) {
            console.error("Error:");
            console.error(error);
        }
    );
}

function handleQuizCreate(socket, quizJSON){
    console.log(`Creating a quiz using the JSON '${quizJSON}'`);
    let url = "/api/questionSetAdd?code=" + process.env.FUNCTION_APP_KEY;
    backendPOST(url, quizJSON).then(
        function(response) {
            console.log("Success:");
            console.log(response);
            socket.emit("quiz_create_success");
        },
        function (error) {
            console.error("Error:");
            console.error(error);
            socket.emit("quiz_create_error");
        }
    );
}

//Get Room List
function handleGetRoomList(socket) {
    console.log(`Getting a list of all rooms`);
    let url = "/api/roomAllGet?code=" + process.env.FUNCTION_APP_KEY;
    backendGET(url, {}).then(
        function(response) {
            console.log("Success:");
            console.log(response);
            socket.emit('room_list_all', response["rooms"] || []);
        },
        function (error) {
            console.error("Error:");
            console.error(error);
        }
    );
}

// Get Question Set IDs
function handleGetQuestionSetIDs(socket) {
    console.log(`Getting a list of all question set IDs`);
    let url = "/api/questionsetallget?code=" + process.env.FUNCTION_APP_KEY;
    backendGET(url, {}).then(
        function(response) {
            console.log("Success:");
            console.log(response);
            socket.emit('receive_question_IDs', response["questionSetIDs"] || []);
        },
        function (error) {
            console.error("Error:");
            console.error(error);
        }
    );
}

//Increment Room State
function handleIncrementGameState(socket, info) {
    console.log(`Incrementing the state of the room`);

    const adminUsername = info["adminUsername"];
    const gameState = info["gameState"];

    // Get all the players in the room
    let url = "/api/roomInfoGet?code=" + process.env.FUNCTION_APP_KEY;
    backendGET(url, {adminUsername: adminUsername}).then(
        function(response) {
            console.log("Success:");
            console.log(response);
            let players = response["players"];

            // For each player in the room, send them an increment state message
            all_players_sockets[adminUsername].emit("increment_game_state", gameState);
            for (let player of players) {
                const player_socket = all_players_sockets[player];
                player_socket.emit('increment_game_state', gameState);
            }
        },
        function (error) {
            console.error("Error:");
            console.error(error);
        }
    );
}

function handlePlayerScoreUpdate(socket, info) {
    console.log(`Updating the scores of the players in the room`);

    const adminUsername = info["adminUsername"];

    // Get all the players in the room
    let url = "/api/roomInfoGet?code=" + process.env.FUNCTION_APP_KEY;
    backendGET(url, {adminUsername: adminUsername}).then(
        function(response) {
            console.log("Success:");
            console.log(response);
            let players = response["players"];

            // For each player in the room, send them an increment state message
            all_players_sockets[adminUsername].emit("player_score_update", info);
            for (let player of players) {
                const player_socket = all_players_sockets[player];
                player_socket.emit('player_score_update', info);
            }
        },
        function (error) {
            console.error("Error:");
            console.error(error);
        }
    );
}

// Delete Room
function handleDeleteRoom(socket) {
    console.log(`Deleting a room`);

    let username = "";
    for (let [key, value] of Object.entries(all_players_sockets)) {
        if (value === socket) {
            username = key;
            break;
        }
    }
    if (!username) {
        return;
    }

    let url = "/api/roomSessionDel?code=" + process.env.FUNCTION_APP_KEY;
    backendDELETE(url, {username: username}).then(
        function(response) {
            console.log("Success:");
            console.log(response);
            const players = response["players"];

            if (response["result"]) {
                for (let player of players) {
                    const player_socket = all_players_sockets[player];
                    player_socket.emit('kick_from_room');
                }
            }
            else {
                socket.emit("error", response["msg"])
            }
        },
        function (error) {
            console.error("Error:");
            console.error(error);
        }
    );
}

//Create Room
function handleCreateRoom(socket, info) {
    console.log(`Creating a room`);

    let url = "/api/roomSessionAdd?code=" + process.env.FUNCTION_APP_KEY;
    backendPOST(url, info).then(
        function(response) {
            console.log("Success:");
            console.log(response);
            if (response["result"]) {
                io.emit('room_list_add', {adminUsername: info['username'], adultOnly: info['adultOnly'], password: info['password']})
                socket.emit('confirm_admin_room_create')
            }
            else {
                socket.emit('error', response["msg"])
            }
        },
        function (error) {
            console.error("Error:");
            console.error(error);
        }
    );
}

//Join Room
function handleJoinRoom(socket, room) {
    console.log(`Joining a room`);
    console.log(room)

    // Send a POST request to the room to add a player to it.
    let url = "/api/roomPlayerAdd?code=" + process.env.FUNCTION_APP_KEY;
    backendPOST(url, room).then(
        function(response) {
            console.log("Success:");
            console.log(response);

            // Get all the players in the room
            let url = "/api/roomInfoGet?code=" + process.env.FUNCTION_APP_KEY;
            backendGET(url, {adminUsername: room['adminUsername']}).then(
                function(response) {
                    console.log("Success:");
                    console.log(response);

                    if (response["result"]) {
                        let room_questions;
                        let players = response["players"];
                        players.push(room['adminUsername']);

                        // Get the questions belonging to the question set for this room.
                        let url = "/api/questionSetQuestionsGet?code=" + process.env.FUNCTION_APP_KEY;
                        backendGET(url, {question_set_id: response['question_set_id']}).then(
                            function(response) {
                                console.log("Success:");
                                console.log(response);
                                room_questions = response["questions"];
                                // shuffle the answers in the questions

                                for (const round of room_questions) {
                                    for (const question of round) {
                                        question["answers"].sort(() => Math.random() - 0.5);
                                    }
                                }

                                // For each player in the room, send them an increment state message
                                for (let player of players) {
                                    const player_socket = all_players_sockets[player];
                                    player_socket.emit('confirm_join_room', room_questions);
                                    player_socket.emit('room_player_list', players);
                                }
                            },
                            function (error) {
                                console.error("Error:");
                                console.error(error);
                            }
                        );

                    }
                    else {
                        socket.emit("error", response["msg"]);
                    }
                },

                function (error) {
                    console.error("Error:");
                    console.error(error);
                }
            );
        },
        function (error) {
            console.error("Error:");
            console.error(error);
        }
    );
}

//Leave Room
function handleLeaveRoom(socket) {
    console.log(`Leaving a room`);
    console.log(room)

    let url = "/api/roomPlayerDel?code=" + process.env.FUNCTION_APP_KEY;
    backendDELETE(url, {}).then(
        function(response) {
            console.log("Success:");
            console.log(response);

            // TODO : Get list of everyone in the room -> Send to everyone on the list
        },
        function (error) {
            console.error("Error:");
            console.error(error);
        }
    );
}

function handleGetPlayerInfo(socket){
    var username = null;
    console.log('Getting player info')
    for (let [key, value] of Object.entries(all_players_sockets)) {
        if (value === socket) {
            username = key;
            break;
        }
    }
    let url = "/api/playerInfoGet?code=" + process.env.FUNCTION_APP_KEY;
    backendGET(url,{'username':username}).then(
        function (response){
            console.log("Success:");
            console.log(response);
            if (response['result']===true){
                console.log("emitting to socket")
                socket.emit('profileInfoReceived',response['body'])
            }
        },
        function (error) {
            console.error("Error:");
            console.error(error);
        }
    )
}

function handleUpdateProfileInfo(socket, info){
    console.log('Updating player info')
    var username = null;
    for (let [key, value] of Object.entries(all_players_sockets)) {
            if (value === socket) {
                username = key;
                break;
            }
    }
    info['username'] = username;
    let url = "/api/playerInfoSet?code=" + process.env.FUNCTION_APP_KEY;
    backendPUT(url,info).then(
        function (response){
            console.log("Success:")
            console.log(response)
            if (response['result']===true){
                console.log("emitting to client")
                socket.emit('profileInfoUpdated');}
        },
        function (error){
            console.error("Error.")
            console.error(error)
        }
    )
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
    console.log(BACKEND_ENDPOINT + path)
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
        console.log("url", BACKEND_ENDPOINT + path)
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

function backendPUT(path, body) {
    return new Promise((success, failure) => {
        request.put(BACKEND_ENDPOINT + path, {
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

function backendDELETE(path, body) {
    console.log(BACKEND_ENDPOINT + path);
    return new Promise((success, failure) => {
        request.delete(BACKEND_ENDPOINT + path, {
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

        handleDeleteRoom(socket);

        // Remove the username-socket pair from the list
        for (let [key, value] of Object.entries(all_players_sockets)) {
            if (value === socket) {
                delete all_players_sockets[key];
                break;
            }
        }
    });

    //Handle register
    socket.on('register', (registerJSON) => {
        handleRegister(socket, registerJSON);
    });

    //Handle login
    socket.on('login', (loginJSON) => {
        handleLogin(socket, loginJSON);
    });

    //Handle logout
    socket.on('logout', (info) => {
        handleLogout(info);
    });

    //Handle delete user
    socket.on('delete', (delUserJSON) => {
        handleDeleteUser(delUserJSON);
    });

    //Handle add friend
    socket.on('add_friend', (addFriendJSON) => {
        handleAddFriend(addFriendJSON)
    });

    //Handle delete friend
    socket.on('del_friend', (delFriendJSON) => {
        handleDeleteFriend(delFriendJSON)
    });

    //Handle updating friends
    socket.on('update_friends', (info) => {
        handleUpdateFriends(socket, info);
    });

    //Handle add favourite quiz
    socket.on('add_favourite_quiz', () => {
        console.log('Adding a favourite quiz');
    });

    //Handle get quiz ids
    socket.on('get_question_set_ids', () => {
        console.log('Adding a favourite quiz');
        handleGetQuestionSetIDs(socket);
    });

    //Handle delete favourite quiz
    socket.on('del_favourite_quiz', () => {
        console.log('Deleting a favourite quiz');
    });

    //Handle create room
    socket.on('create_room', (info) => {
        console.log("Creating room with info " + Object.entries(info))
        handleCreateRoom(socket, info);
    });

    //Handle join room
    socket.on('join_room', (room) => {
        handleJoinRoom(socket, room)
    });

    //Handle leave room
    socket.on('leave_room', () => {
        handleLeaveRoom(socket);
    });

    //Handle deleting room
    socket.on('delete_room', (info) => {
        handleDeleteRoom(all_players_sockets[info['username']]);
    })

    //Handle use power up
    socket.on('use_power_up', () => {
        console.log('Using a power up');
    });

    //Handle create quiz
    socket.on('create_quiz', (quizJSON) => {
        handleQuizCreate(socket, quizJSON);
    });

    //Handle delete quiz
    socket.on('delete_quiz', () => {
        console.log('Deleting a quiz');
    });

    //Handle update quiz
    socket.on('update_quiz', () => {
        console.log('Updating a quiz');
    });

    //Handle request to get player questions
    socket.on('get_player_questions', (getQuestionsJSON) => {
        handleGetPlayerQuestions(socket, getQuestionsJSON);
    });

    //Handle request to get a list of all rooms
    socket.on('get_room_list', () => {
        handleGetRoomList(socket);
    });

    //Handle telling all the players in a lobby/game to increment their game state
    socket.on('increment_game_state', (info) => {
        handleIncrementGameState(socket, info);
    });

    //Handle telling all the players in a lobby/game to receive the scores for the round that just happened
    socket.on('player_score_update', (info) => {
        console.log("Received player score update " + Object.entries(info));
        handlePlayerScoreUpdate(socket, info);
    });
    //Handle getting current player info
    socket.on('get_player_info', () => {
        handleGetPlayerInfo(socket);
    });
    socket.on('update_profile_info', (info) => {
        handleUpdateProfileInfo(socket,info);
    })
});

//Start server
if (module === require.main) {
    startServer();
}

module.exports = server;
