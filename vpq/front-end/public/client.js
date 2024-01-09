function hashUsername(username) {
    for (var h = 0, i = 0; i < username.length; h &= h) {
        h = 31 * h + username.charCodeAt(i++);
    }
    return Math.abs(h);
}


var socket = null;


//Prepare game
var app = new Vue({
    el: '#game',
    data: {
        connected: false,
        messages: [],
        questionSearchUsernameField: "",

        user: { username: null, password: null, state: null },

        room: {
            id: null,
            adminUsername: null,
            players: [],
            questions: [],  // [[..], [..]]
            isAdultOnly: null,
            state: "lobby",
            currentRound: -1,
            currentQuestion: -1,
            is_host: false,
            currentAnswer: null,
            score: 0,
            whenLastQuestionAsked: null,
            whenLastQuestionAnswered: null,
            leaderboard: {},
        },

        rooms: [],
        page: "home",
    },
    mounted: function() {
        connect();
    },
    methods: {
        setPage(page) {
            if (["create", "host", "join"].includes(page) && !this.user.username) {
                alert("You must be logged in to do that.");
                return;
            }
            if (["login"].includes(page) && this.user.username) {
                alert("You are already logged in. Log out first.");
                return;
            }
            this.page = page;
        },

        searchDatabaseForQuestions(){
            socket.emit('get_player_questions', { username: this.questionSearchUsernameField });
        },

        setQueriedQuestions(questionsRetrieved){
            this.queriedQuestions = questionsRetrieved;
        },

        // This function is here so that a vue variable can be passed to an external file
        handleAddSearchedQuestion(question){
          window.addFromSearch(question);
        },

        // TODO: Add correct data to each of the socket.emit() functions
        handleChat(message) {
            if(this.messages.length + 1 > 10) {
                this.messages.pop();
            }
            this.messages.unshift(message);
        },

        chat() {
            socket.emit('chat',this.message);
            this.chatmessage = '';
        },
        register(username, password) {
            socket.emit('register', {"username": username, "password": password});
        },
        login(username, password) {
            socket.emit('login', {"username": username, "password": password});
            this.showLoading();
        },
        roomList() {
            socket.emit('get_room_list');
        },
        deleteUser(username, password) {
            socket.emit('delete', {"username": username, "password": password});
        },
        addFriend() {
            socket.emit('add_friend');
        },
        deleteFriend() {
            socket.emit('del_friend');
        },
        addFavouriteQuiz() {
            socket.emit('add_favourite_quiz');
        },
        deleteFavouriteQuiz() {
            socket.emit('del_favourite_quiz');
        },
        createRoom(questionSetID, adultOnly, password) {
            if (!adultOnly) { adultOnly = false; }
            if (!password) { password = ""; }
            socket.emit('create_room', {username: this.user.username, questionSetID: questionSetID, adultOnly: adultOnly, password: password});
            this.showLoading();
        },
        joinRoom(room) {
            this.page = "game"
            this.room.adminUsername = room.adminUsername;
            socket.emit('join_room', {adminUsername: room.adminUsername, usernameToAdd: this.user.username});
            this.showLoading();
        },
        leaveRoom() {
            socket.emit('leave_room');
        },
        usePowerUp() {
            socket.emit('use_power_up')
        },
        createQuiz(quizJSON) {
            // TODO: On the server end this will create a new question set and any questions that are new will be added to the database
            socket.emit('create_quiz', quizJSON);
        },
        deleteQuiz() {
            socket.emit('delete_quiz')
        },
        updateQuiz() {
            socket.emit('update_quiz')
        },
        startGame() {
            // First thing is to move to the first round
            socket.emit('increment_game_state', {adminUsername: this.user.username, gameState: "round_splash"});
            this.showLoading();
        },
        selectMultiChoiceAnswer(number) {
            this.room.currentAnswer = number;
            this.room.whenLastQuestionAnswered = Date.now();

            // Disable all the buttons
            // const grid = document.getElementById("answer-container").children[0];
            // Array.from(grid.children).forEach(button => button.disabled = true);

        },
        flowGameRound() {
            // Only run from the admin.
            const num_questions_this_round = this.room.questions[this.room.currentRound].length;
            for (const i in this.room.questions[this.room.currentRound]) {
                setTimeout(() => {
                    socket.emit('increment_game_state', {
                        adminUsername: this.user.username,
                        gameState: "question"
                    });

                    setTimeout(() => {
                        socket.emit('increment_game_state', {
                            adminUsername: this.user.username,
                            gameState: "answer"
                        });
                    }, 5000);
                }, 5000 + (i * 10000));
            }

            setTimeout(() => {
                socket.emit('increment_game_state', {
                    adminUsername: this.user.username,
                    gameState: "round_score"
                });

                setTimeout(() => {
                    socket.emit('increment_game_state', {
                        adminUsername: this.user.username,
                        gameState: "round_splash"
                    });
                }, 5000);
            }, 5000 + (num_questions_this_round * 10000));
        },

        showLoading() {
            document.getElementById("loading").style.display = "block";
        },
        hideLoading() {
            document.getElementById("loading").style.display = "none";
        },

        handleAnswerPage() {
            this.$nextTick(() => {
                const answerBoxes = document.getElementById("answer-container-2").children[0].children;
                const correctAnswer = this.room.questions[this.room.currentRound][this.room.currentQuestion]["correct_answer"];
                const correctAnswerBox = Array.from(answerBoxes).find(box => box.innerText === correctAnswer);

                // Make the selected answer box red, and the correct answer box green (green will override red).
                if (this.room.currentAnswer) {
                    answerBoxes[this.room.currentAnswer].style.backgroundColor = "crimson";
                }
                else {
                    Array.from(answerBoxes).forEach(box => box.style.backgroundColor = "crimson");
                }

                correctAnswerBox.style.backgroundColor = "#47ff6d";

                if (answerBoxes[this.room.currentAnswer].innerText === this.room.questions[this.room.currentRound][this.room.currentQuestion]["correct_answer"]) {
                    this.room.score += 5000 - (this.room.whenLastQuestionAnswered - this.room.whenLastQuestionAsked);
                    this.room.whenLastQuestionAnswered = null;
                    this.room.whenLastQuestionAsked = null;
                }
            });
        },

        handlePlayerScoreUpdate(info) {
            for (const item of info) {
                this.room.leaderboard[item.username] = item.score;
            }
        }
    }
});

function connect() {
    //Prepare web socket
    socket = io();

    //Connect
    socket.on('connect', function() {
        //Set connected state to true
        app.connected = true;
        window.app = app;
        app.roomList();
    });
    socket.on('confirm_login', function(info) {
        app.hideLoading();
        app.user.username = info["username"];
        app.user.password = info["password"];
        app.setPage("join");
    })

    //Handle connection error
    socket.on('connect_error', function(message) {
        alert('Unable to connect: ' + message);
    });

    //Handle disconnection
    socket.on('disconnect', function() {
        alert('Disconnected');
        app.connected = false;
    });

    //Handle incoming chat message
    socket.on('chat', function(message) {
        app.handleChat(message);
    });

    //Handle incoming queried questions
    socket.on('queried_questions', function(questionsRetrieved) {
        app.setQueriedQuestions(questionsRetrieved);
    });

    //Handle incoming list of rooms + updates to it
    socket.on('room_list_all', function(rooms) {
        for (let room of rooms) {
            room["id"] = hashUsername(room.adminUsername);
            app.rooms.push(room);
        }
    });
    socket.on("room_list_add", function(room) {
        room["id"] = hashUsername(room.adminUsername);
        app.rooms.push(room);
    });
    socket.on("room_list_del", function(adminUsername) {
        app.rooms = app.rooms.filter(room => room.adminUsername !== adminUsername);
    });

    //Handle incrementing game state
    socket.on("increment_game_state", function(state) {
        app.hideLoading();
        app.room.state = state;

        if (app.room.state === "round_splash") {
            app.room.currentRound += 1;  // todo : name of round instead
            app.room.currentQuestion = -1;
            if (app.room.is_host) {
                app.flowGameRound();
            }
        }

        if (app.room.state === "question") {
            app.room.currentQuestion += 1;
            app.room.currentAnswer = null;
            app.room.whenLastQuestionAsked = Date.now();
        }

        if (app.room.state === "answer") {
            app.handleAnswerPage();
        }

        if (app.room.state === "round_score") {
            socket.emit('player_score_update', {adminUsername: app.room.adminUsername, username: app.user.username, score: app.room.score});
        }
    })

    //Handle incoming room player list for the current room this client is in
    socket.on('room_player_list', function(players) {
        app.room.players = players;
    });
    socket.on("confirm_join_room", function(questions) {
        app.hideLoading();
        app.room.questions = questions;
    })

    //Handle (as admin) a room open request being granted
    socket.on('confirm_admin_room_create', function() {
        app.hideLoading();
        app.room.is_host = true;
        app.room.adminUsername = app.user.username;
        app.page = "game";
    })

    //Handle an error
    socket.on('error', function(error) {
        app.hideLoading();
    })

    //Handle receiving the scores of each player in the game
    socket.on('player_score_update', function(info) {
        app.handlePlayerScoreUpdate(info);
    });
}
