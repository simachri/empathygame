sap.ui.define([
	"sap/ui/Device",
	"sap/ui/core/mvc/Controller",
	'sap/m/MessageBox',
    "sap/ui/model/json/JSONModel",
    "empathygame/libs/socketio",
    "empathygame/libs/empathygame"
], function(Device, Controller, MessageBox, JSONModel, socketiojs, empathygamejs) {
	"use strict";


	return Controller.extend("empathygame.controller.CreateGame", {

		onInit: function() {

			this.getView().setModel(new JSONModel({
                isMobile: Device.browser.mobile,
                loading: false,
                gameCollection: [
                    {
                        "key": "schoolInclusion",
                        "text": "School Inclusion"
                    },
                    {
                        "key": "dummy",
                        "text": "Dummy Entry"
                    }
                ] 
			}));	

        },
        
        /**
         * 
         * Get game id and game pwd
         */
        getGameIdPwd: function(gameScenario, userName){

            var that = this;

            that.getView().getModel().setProperty("loading", true);

			var socket = io.connect( {
                'path': '/api/ws/socket.io'
            });

            var eg = getEmpathyGame(socket);
            that.getView().getModel("store").setProperty("/eg", eg);

            //--Register to connect event and sent "new_game" afterwards
			socket.on('connect', () => {
                that.getView().getModel().setProperty("loading", false);
                //--Send "new_game" event
                /*socket.emit('new_game', {"game_scenario": gameScenario, "user_name": userName }, function(response){
                    that.getView().getModel().setProperty("loading", true);
                });*/
                eg.createGame(gameScenario, userName);
            });		

            socket.on('disconnect', () => {
                that.getView().getModel().setProperty("loading", false);
            });	
            socket.on('error', (error) => {
                MessageBox.error(JSON.stringify(error));
              });
                            
            //--Process event "new_game" reached
			socket.on('new_game', data => {
                that.getView().getModel().setProperty("loading", false);
                that.getView().getModel("store").setProperty("/gameId", data.game_id);
                that.getView().getModel("store").setProperty("/gamePwd", data.game_pwd);
                //--Redirect to lobby
                that.navToLobby();
            });	
        },

		/**
		 * 
		 * Creates a new game
		 */
		createGame: function(oEvent){
            var that = this;
            //--Get selected game and user name
            var selectedGame = this.getView().byId('gameList').getSelectedItem().getText();
            var userName = this.getView().getModel("store").getProperty("/userName")

            if(selectedGame !== null && selectedGame !== undefined && selectedGame !== ""){
                that.getView().getModel().setProperty("/gameName", selectedGame);
                that.getGameIdPwd(selectedGame, userName);                
            }
            else{
                MessageBox.error("Please select a game you want to play");
            }
		},


		/**
		 * Navigation
		 */
		navToLobby: function() {
        	sap.ui.core.UIComponent.getRouterFor(this).navTo("lobby");
		}
	});

});
