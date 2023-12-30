/*
Handles the relationship between clients and their sockets
Handles the relationship between rooms and their clients
*/

class ClientHandler {
    constructor() {
        /*
        RoomIDs, userIDs (username) and socketIDs (socket.id) are strings
        Stores clients in the form:
        {
            userID: {
                password: password,
                socket: socketID,
                room: null or roomID,
                removeTimeout: null or removeTimeoutID
            },
            userID: {}, ...
        }

        Stores sockets in the form:
        {
            socketID: userID,
            socketID: userID
        }

        Stores rooms in the form:
        {
            roomID: {
                name: roomName,
                admin: userID,
                players: [userID, userID, ...],
                audience: [userID, userID, ...]
            },
            roomID: {}, ...
        }

        
        Feel free to change these formats, but ensure that:
        - You update this comment
        - Adding and removing clients/sockets/rooms follow the above rules
        */

        this.clients = {};
        this.sockets = {};
        this.rooms = {};
    }

    /*
    Add a client with their username
    Ensures the client is not already connected (a client can disconnect and reconnect and be considered an add)

    Returns true on successful add, false if the user has logged in and is connected
    */
    addClient(userID, password, socketID) {
        if (userID in this.clients) { // Has user previously logged in
            if (this.isClientOnline(userID)) {
                console.log(JSON.stringify(this.clients, null, 2));
                return false; // Cannot add, user exists and is connected
            }
    
            this.sockets[socketID] = userID; // Update the users socketID
            this.clients[userID].socket = socketID;
            clearTimeout(this.clients[userID].removeTimeout); // Stop the removal of the client

            console.log(JSON.stringify(this.clients, null, 2));
            return true;
        }
    
        this.clients[userID] = {password: password, socket: socketID, room: null, timeout: null};
        this.sockets[socketID] = userID;
    
        console.log(JSON.stringify(this.clients, null, 2));
        return true;
    }
    
    /*
    Remove a client with their username or socketID
    The second argument decides if removal should be forced
    - If true: 
        - Clients are removed even if they are in a room (in the event of a ban or logout).
        - If the client is an admin of a room, the room is closed.
    - If false:
        - Clients are only removed if they aren't in a room (in the event of a disconnect).
        - There is a timeout before the client is force removed.
    In both instances, the socket is removed

    Returns true if user is successfully removed, false if user isn't found
    */
    removeClientByUsername(userID, force) {
        if (userID in this.clients) { // Has user previously logged in
            let socketID = this.clients[userID].socket;
            let roomID = this.clients[userID].room;

            delete this.sockets[socketID]; // User is no longer at this socket

            if (this.clients[userID].room === null || !(roomID in this.rooms)) { // User can be fully deleted if they aren't in a room
                delete this.clients[userID];
                console.log(JSON.stringify(this.clients, null, 2));
                return true;
            }

            function forceRemove() { // Unsure if correct, handles user deletion if user is in a room
                if (this.rooms[roomID].admin === userID) {
                    this.closeRoom(roomID);

                } else if (this.rooms[roomID].players.includes(userID)) {
                    const index = this.rooms[roomID].players.indexOf(userID);
                    this.rooms[roomID].players.splice(index, 1);

                } else if (this.rooms[roomID].audience.includes(userID)) {
                    const index = this.rooms[roomID].audience.indexOf(userID);
                    this.rooms[roomID].audience.splice(index, 1);

                } else {
                    console.error(`Could not find ${userID} in ${roomID}. Failed to remove`);
                }

                delete this.clients[userID];
            }

            if (force) {
                forceRemove();
            } else {
                this.clients[userID].removeTimeout = setTimeout(function() {
                    forceRemove();
                    console.log("Delayed action after 5 seconds");
                }, 5 * 1000);
            }

            console.log(JSON.stringify(this.clients, null, 2));
            return true;
        } else {
            console.log(JSON.stringify(this.clients, null, 2));
            return false; // User does not exist
        }
    }

    removeClientBySocketID(socketID, force) {
        if (socketID in this.sockets) {
            console.log(JSON.stringify(this.clients, null, 2));
            return this.removeClientByUsername(this.sockets[socketID], force);
        } else {
            console.log(JSON.stringify(this.clients, null, 2));
            return false;
        }
    }

    // Check if a user is currently logged in and connected
    isClientOnline(userID) {
        if (userID in this.clients) {
            console.log(JSON.stringify(this.clients, null, 2));
            return this.clients[userID].socket in this.sockets;
        } else {
            console.log(JSON.stringify(this.clients, null, 2));
            return false;
        }
    }

    getClientData(userID) {
        if (userID in this.clients) {
            console.log(JSON.stringify(this.clients, null, 2));
            return { ... this.clients[userID], username: userID};
        }
    }

    closeRoom(roomID) { // TODO

    }
}

module.exports = ClientHandler;