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
        // loginInput: { username: "", password: "" }, // Different to user since it is connected to the UI
        user: { username: null, password: null, state: null },
        // These variables are for during a quiz
        room: { id: null, adminUsername: null, players: [], questions: [], isAdultOnly: null, state: null},
        rooms: [],
        page: "home",
        game_state: "lobby",
        is_host: false,
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
            this.user.username = username;
            this.user.password = password;

            // TODO: check username & password are correct
            this.setPage("join");
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
            this.is_host = true;  // TODO: remember to set this to false when the game ends
            this.page = "game";
        },
        joinRoom(room) {
            this.page = "game"
            socket.emit('join_room', {adminUsername: room.adminUsername, usernameToAdd: this.user.username});
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
        incrementGameState(state) {
            // Advance the state of the game for all players.
            socket.emit('increment_game_state', {adminUsername: this.room.adminUsername, gameState: state});
        },
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
        app.game_state = state;
    })

    //Handle incoming room player list for the current room this client is in
    socket.on('room_player_list', function(players) {
        app.room.players = players;
    });
}
