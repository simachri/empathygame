sap.ui.define([
	"sap/ui/Device",
	"sap/ui/core/mvc/Controller",
	'sap/m/MessageBox',
    "sap/ui/model/json/JSONModel",
    "empathygame/libs/socketio"
], function(Device, Controller, MessageBox, JSONModel, socketiojs) {
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
        getGameIdPwd: function(gameScenario){

            var that = this;

            that.getView().getModel().setProperty("loading", true);

			var socket = io.connect( {
                'path': '/api/ws/socket.io'
            });

            //--Register to connect event and sent "new_game" afterwards
			socket.on('connect', () => {
                that.getView().getModel().setProperty("loading", false);
                //--Send "new_game" event
                socket.emit('new_game', {"game_scenario": gameScenario }, function(response){
                    that.getView().getModel().setProperty("loading", true);
                });
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
                that.getView().getModel().setProperty("store>/gameId", data.game_id);
                that.getView().getModel().setProperty("store>/gamePwd", data.game_pwd);
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
            //--Get selected game
            var selectedGame = this.getView().byId('gameList').getSelectedItem().getText();

            if(selectedGame !== null && selectedGame !== undefined && selectedGame !== ""){
                that.getView().getModel().setProperty("/gameName", selectedGame);
                that.getGameIdPwd();                
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
