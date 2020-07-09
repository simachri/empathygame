class EmpathyGame {
    constructor(socket ) {
      this.socket = socket;
    }

    getSocket(){
        return this.socket;
    }

    createGame(gameScenario, userName) {
       this.socket.emit('new_game', {"game_scenario": gameScenario, "user_name": userName });  		
    }
  
    joinGame(gameId, gamePwd, userName, userId) {
        this.socket.emit('join_game', {"game_id": gameId, "game_pwd": gamePwd, "user_name": userName, "user_id": userId });
    }
  }
  
  function getEmpathyGame(socket){
      return new EmpathyGame(socket);
  }