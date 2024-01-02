var socket = null;

//Prepare game
var app = new Vue({
    el: '#game',
    data: {
        connected: false,
        messages: [],
        questionSearchUsernameField: "",
        loginInput: { username: "", password: "" }, // Different to user since it is connected to the UI
        user: { username: "Guest1", password: null, state: null },
        // These variables are for during a quiz
        room: { roomID: null, adminUsername: null, players: [], questions: [], isAdultOnly: null, state: null},
        rooms: [],
        page: "home",
    },
    mounted: function() {
        connect();
    },
    methods: {
        setPage(page) {
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
        register() {
            socket.emit('register', this.loginInput);
        },
        login() {
            socket.emit('login', this.loginInput);
        },
        roomList() {
            socket.emit('get_room_list');
        },
        deleteUser() {
            socket.emit('delete', this.loginInput.username);
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
            socket.emit('create_room', {questionSetID: questionSetID, adultOnly: adultOnly, password: password});
        },
        joinRoom(room) {
            socket.emit('join_room', {id: room.id, player: this.user.username});
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
        app.rooms = rooms;
    });
    socket.on("room_list_add", function(room) {
        app.rooms.push(room);
    });
    socket.on("room_list_del", function(roomID) {
        app.rooms = app.rooms.filter(room => room.roomID !== roomID);
    });
}
