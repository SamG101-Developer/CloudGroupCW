var socket = null;

//Prepare game
var app = new Vue({
    el: '#game',
    data: {
        connected: false,
        messages: [],
        queriedQuestions: [
            {
                questionType: "Multiple Choice",
                questionText: "How many people are in this group?",
                answer: "6",
                options: ["2", "5", "6", "10"]
            },
            {
                questionType: "Numeric",
                questionText: "How many people are in this group?",
                answer: "6",
                options: []
            },
            {
                questionType: "Pick the Letter",
                questionText: "Who wrote this question?",
                answer: "(B)en",
                options: []
            },
            {
                questionType: "Full Answer",
                questionText: "Who wrote this question?",
                answer: "Ben",
                options: []
            }
        ], // These are the questions that are loaded using the player_question_groups_get function
        questionSearchUsernameField: "",
        loginInput: { username: "", password: "" }, // Different to user since it is connected to the UI
        user: { username: null, password: null, state: null },
        // These variables are for during a quiz
        room: { roomID: null, adminUsername: null, players: [], questions: [], isAdultOnly: null, state: null}
    },
    mounted: function() {
        connect();
    },
    methods: {
        searchDatabaseForQuestions(){
            //TODO: This will use 'questionSearchUsernameField' and return all the questions of that username into
            socket.emit('get_player_questions', this.questionSearchUsernameField);
        },
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
            socket.emit('chat',this.chatmessage);
            this.chatmessage = '';
        },
        register() {
            socket.emit('register', this.loginInput);
        },
        login() {
            socket.emit('login', this.loginInput);
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
        createRoom() {
            socket.emit('create_room');
        },
        joinRoom() {
            socket.emit('join_room');
        },
        leaveRoom() {
            socket.emit('leave_room');
        },
        usePowerUp() {
            socket.emit('use_power_up')
        },
        createQuiz() {
            // TODO: On the server end this will create a new question set and any questions that are new will be added to the database
            socket.emit('create_quiz')
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


}
