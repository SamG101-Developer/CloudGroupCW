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
        timers: [],
        queriedQuestions: [],

        user: {
            username: null,
            password: null,
            state: null,
            firstName: null,
            lastName: null,
            currency:null,
            premiumCurrency:null,
            overallScore:null,
        },

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
            if (["create", "host", "join", "profile"].includes(page) && !this.user.username) {
                alert("You must be logged in to do that.");
                return;
            }
            if (["login"].includes(page) && this.user.username) {
                alert("You are already logged in. Log out first.");
                return;
            }
            if (page === "join") {
                this.roomList();
            }
            else if (page==="profile"){
                socket.emit('get_player_info');
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
        register(username, password, confirmPassword, firstName, lastName) {
            if (password !== confirmPassword) {
                alert("Passwords do not match");
                return;
            }
            this.showLoading();
            socket.emit('register', {"username": username, "password": password, "firstname": firstName, "lastname": lastName});
        },
        login(username, password) {
            this.showLoading();
            socket.emit('login', {"username": username, "password": password});
            // document.getElementById("login-password").value = "";
            // document.getElementById("register-password").value = "";
        },
        logout() {
            if (!this.user.username) {
                alert("You must be logged in to do that.");
                return;
            }
            socket.emit('logout', {"username": this.user.username});
            document.getElementById("nav-profile-button").innerText = "Profile";
            this.user.username = null;
            this.user.password = null;
            this.user.state = null;
            this.user.firstName = null;
            this.user.lastName = null;
            this.user.currency = null;
            this.user.premiumCurrency = null;
            this.user.overallScore = null;
            this.setPage("login");
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
            if (room.password) {
                const password = prompt("Enter the password for this room");
                if (password !== room.password) {
                    alert("Incorrect password");
                    return;
                }
            }

            this.page = "game"
            this.room.adminUsername = room.adminUsername;
            this.showLoading();
            socket.emit('join_room', {adminUsername: room.adminUsername, usernameToAdd: this.user.username});
        },
        leaveRoom() {
            socket.emit('leave_room');
        },
        usePowerUp() {
            socket.emit('use_power_up')
        },
        createQuiz(quizJSON) {
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
            const answer_buttons = document.getElementsByClassName("answer-box");
            Array.from(answer_buttons).forEach(button => button.disabled = true);
            this.timers.push(setTimeout(() => Array.from(answer_buttons).forEach(button => button.disabled = false), 10000 - (this.room.whenLastQuestionAnswered - this.room.whenLastQuestionAsked)));

        },
        selectLetterAnswer(number){
            this.room.currentAnswer = number;
            this.room.whenLastQuestionAnswered = Date.now();
            const answer_buttons = document.getElementsByClassName("letter-box");
            Array.from(answer_buttons).forEach(button => button.disabled = true);
            this.timers.push(setTimeout(() => Array.from(answer_buttons).forEach(button => button.disabled = false), 10000 - (this.room.whenLastQuestionAnswered - this.room.whenLastQuestionAsked)));
        },
        flowGameRound() {
            // Only run from the admin.
            const num_questions_this_round = this.room.questions[this.room.currentRound].length;
            for (const i in this.room.questions[this.room.currentRound]) {
                this.timers.push(setTimeout(() => {
                    socket.emit('increment_game_state', {
                        adminUsername: this.user.username,
                        gameState: "question"
                    });

                    this.timers.push(setTimeout(() => {
                        socket.emit('increment_game_state', {
                            adminUsername: this.user.username,
                            gameState: "answer"
                        });
                    }, 5000));
                }, 5000 + (i * 10000)));
            }

            this.timers.push(setTimeout(() => {
                socket.emit('increment_game_state', {
                    adminUsername: this.user.username,
                    gameState: "round_score"
                });

                if (this.room.currentRound + 1 < this.room.questions.length) {
                    this.timers.push(setTimeout(() => {
                        socket.emit('increment_game_state', {
                            adminUsername: this.user.username,
                            gameState: "round_splash"
                        });
                    }, 5000));
                }
                else {
                    this.timers.push(setTimeout(() => {
                        socket.emit('increment_game_state', {
                            adminUsername: this.user.username,
                            gameState: "end_game"
                        });
                    }, 5000));
                }
            }, 5000 + (num_questions_this_round * 10000)));
        },

        showLoading() {
            document.getElementById("loading").style.display = "block";
        },
        hideLoading() {
            document.getElementById("loading").style.display = "none";
        },

        handleAnswerPage() {
            this.$nextTick(() => {
                let answerBoxes = document.getElementById("answer-container-2").children[0].children;
                let correctAnswer = this.room.questions[this.room.currentRound][this.room.currentQuestion]["correct_answer"];
                if ( this.room.questions[this.room.currentRound][this.room.currentQuestion]["question_type"] === "Pick the Letter"){
                    correctAnswer = correctAnswer.slice(0, 1).toUpperCase();
                    console.log(correctAnswer);
                    answerBoxes = document.getElementById("answer-container-2").children[0].children;
                }
                const correctAnswerBox = Array.from(answerBoxes).find(box => box.innerText === correctAnswer);

                // Make the selected answer box red, and the correct answer box green (green will override red).
                if (this.room.currentAnswer) {
                    answerBoxes[this.room.currentAnswer].style.backgroundColor = "crimson";
                }
                else {
                    Array.from(answerBoxes).forEach(box => box.style.backgroundColor = "crimson");
                }

                correctAnswerBox.style.backgroundColor = "#47ff6d";

                if (answerBoxes[this.room.currentAnswer].innerText === correctAnswer) {
                    this.room.score += 5000 - (this.room.whenLastQuestionAnswered - this.room.whenLastQuestionAsked);
                    this.room.whenLastQuestionAnswered = null;
                    this.room.whenLastQuestionAsked = null;
                }
            });
        },

        handlePlayerScoreUpdate(info) {
            this.room.leaderboard[info["username"]] = info["score"];

            const leaderboard = document.getElementById("leaderboard");
            const new_player = document.createElement("h2");
            new_player.innerHTML = info["username"] + ": " + info["score"];
            leaderboard.appendChild(new_player);

            // sort all leaderboard entries by score
            const leaderboard_entries = Array.from(leaderboard.children);
            leaderboard_entries.sort((a, b) => {
                const score_a = parseInt(a.innerText.split(": ")[1]);
                const score_b = parseInt(b.innerText.split(": ")[1]);
                return score_b - score_a;
            });
            leaderboard_entries.forEach(entry => leaderboard.appendChild(entry));
        },

        handleProfileInfoReceived(info){
            this.user.firstName = info['firstname']
            this.user.lastName = info['lastname']
            this.user.currency = info['currency']
            this.user.premiumCurrency = info['premium_currency']
            this.user.overallScore = info['overall_score']
        },

        updateProfileInfo(firstname, lastname, newPassword){
            document.getElementById('firstname').value = '';
            document.getElementById('lastname').value = '';
            document.getElementById('newPassword').value = '';
            socket.emit('update_profile_info',{'firstname':firstname, 'lastname':lastname, 'password':newPassword});
        },
        handleProfileInfoUpdated(){
            alert("Profile information updated successfully!")
            this.setPage("profile")
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
    });
    socket.on('confirm_login', function(info) {
        app.hideLoading();
        document.getElementById("nav-profile-button").innerText += " (" + info["username"] + ")";
        app.user.username = info["username"];
        app.user.password = info["password"] || "";
        app.setPage("join");
    })
    socket.on('confirm_register', function(info) {
        app.hideLoading();
        app.login(info["username"], info["password"]);
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
        app.rooms = [];
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
            app.room.leaderboard = {};
            app.room.whenLastQuestionAsked = Date.now();

            if (app.room.is_host) {
                const answer_buttons = document.getElementsByClassName("answer-box");
                Array.from(answer_buttons).forEach(button => button.disabled = true);
            }
        }

        if (app.room.state === "answer") {
            app.handleAnswerPage();
        }

        if (app.room.state === "round_score") {
            socket.emit('player_score_update', {adminUsername: app.room.adminUsername, username: app.user.username, score: app.room.score});
        }

        if (app.room.state === "end_game") {
            if (app.room.is_host) {
                socket.emit('delete_room', {adminUsername: app.user.username});
            }
            app.room.state = "lobby";
            app.room.currentRound = -1;
            app.room.currentQuestion = -1;
            app.room.is_host = false;
            app.room.currentAnswer = null;
            app.room.score = 0;
            app.room.whenLastQuestionAsked = null;
            app.room.whenLastQuestionAnswered = null;
            app.room.leaderboard = {};
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
        alert(error);
        app.hideLoading();
    })

    //Handle receiving the scores of each player in the game
    socket.on('player_score_update', function(info) {
        app.handlePlayerScoreUpdate(info);
    });

    //Handle receiving player info
    socket.on('profileInfoReceived', function (info) {
        app.handleProfileInfoReceived(info);
    });

    //Handle profile info updated
    socket.on('profileInfoUpdated', function () {
        app.handleProfileInfoUpdated();
    });

    //Handle being kicked from the room
    socket.on("kick_from_room", function() {
        for (const timer of app.timers) { clearTimeout(timer); }
        app.setPage("join");
        alert("You have been kicked from the room.");
    });

    //Handle quiz create success
    socket.on("quiz_create_success", function() {
        alert("Your quiz has been created successfully");
    });

    //Handle quiz create incomplete
    socket.on("quiz_create_error", function() {
        alert("There was an error generating your quiz.");
    });
}
