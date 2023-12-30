var socket = null;

//Prepare game
var app = new Vue({
    el: '#game',
    data: {
        connected: false,
        messages: [],
        loginData: { username: "", password: "", errorMsg: "" }, // Different to user since it is connected to the UI
        user: { username: null, password: null, state: null },
        // These variables are for during a quiz
        room: { roomID: null, adminUsername: null, players: [], questions: [], isAdultOnly: null, state: null}
    },
    mounted: function() {
        connect();
    },
    methods: {
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
            socket.emit('register', {username: this.loginData.username, password: this.loginData.password});
        },
        login() {
            socket.emit('login', {username: this.loginData.username, password: this.loginData.password});
        },
        deleteUser() {
            socket.emit('delete', this.loginData.username);
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

function handleLogin(loginJSON) {
    if (loginJSON.result) { // Login/Register successful
        app.loginData.errorMsg = "";
        app.user.username = loginJSON.user.id;
        app.user.password = loginJSON.user.password;
        app.user.state = null; // TODO: Add a state, idk what a state is

        if ("room" in loginJSON) {
            app.room.roomID = loginJSON.room.id;
        }
    } else { // Login/Register failed
        app.loginData.errorMsg = loginJSON.msg;
        app.loginData.password = "";
    }
}

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

    //Handle register/login. Both are sent to one function
    socket.on('login', function(loginJSON) {
        handleLogin(loginJSON);
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
