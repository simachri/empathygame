sap.ui.define([
	"sap/ui/Device",
	"sap/ui/core/mvc/Controller",
	'sap/m/MessageBox',
	"sap/ui/model/json/JSONModel",
	"empathygame/libs/socketio",
	"empathygame/libs/empathygame"
], function(Device, Controller, MessageBox, JSONModel, socketiojs, empathygamejs) {
	"use strict";


	return Controller.extend("empathygame.controller.Router", {

		onInit: function() {

			this.getView().setModel(new JSONModel({
				isMobile: Device.browser.mobile,
				navFrom: "",
			}));	

			var store = this.getOwnerComponent().getModel("store"); 

			switch(this.getView().sViewName) {
				case 'empathygame.view.Router':
					//--Inital screen, check url params
					const queryString = window.location.search;
					const urlParams = new URLSearchParams(queryString);
					var gameId = urlParams.get('game_id');
					var gamePwd = urlParams.get('game_pwd');

					if( (gameId !== null && gameId !== undefined && gameId !== "") &&
						(gamePwd !== null && gamePwd !== undefined && gamePwd !== "") )
					{
						store.setProperty('/gameId', gameId);
						store.setProperty('/gamePwd', gamePwd);
						var baseUrl = location.protocol + '//' + location.host + location.pathname;
						window.history.replaceState({}, "" , baseUrl );
						this.navToUserName('direct');
					}
				break;
			}
		},

		createAccessUrl: function(gameId, gamePwd){
			var accessUrl = location.protocol + '//' + location.host + location.pathname + `?game_id=${gameId}&game_pwd=${gamePwd}`;
			this.getView().getModel("store").setProperty("/accessUrl", accessUrl);
			return accessUrl;
		},


		/**
		 * 
		 * Sets the game Id to store
		 */
		setGameId: function(oEvent){
			var gameId = this.getView().getModel("store").getProperty("/gameId");
			if (gameId === ""){
				MessageBox.error("Please enter the game Id");
			}
			else{
				//--Check if game is existing

				//--Game exists, so check password
				this.navToPassword();
			}			
		},

		/**
		 * 
		 * Sets the user name
		 */
		setUserName: function(){
			var that = this;
			var userName= this.getView().getModel("store").getProperty("/userName");
			if (userName === ""){
				MessageBox.error("Please enter your name");
			}
			else{
				var source = that.getView().getModel("store").getProperty("/commingFrom");
				that.getView().getModel("store").setProperty("/commingFrom", "");
				switch(source) {
					case 'new':
						this.navToCreateGame();
					break;
					case 'login':
						this.navToLogin();
					break;
					case 'direct':
						this.accessGame();
					break;				
				}	
			}		
		},

		/**
		 * Function to access game on backend
		 */
		accessGame: function(oEvent) {
			var that = this;

			//--Check if password was given
			if(this.getView().getModel("store").getProperty("/gamePwd") === ""){
				MessageBox.error("Please enter your password");
			}
			else{
				//--Submit data to get access
				var socket = io.connect( {
					'path': '/api/ws/socket.io'
				});
	
				var eg = getEmpathyGame(socket);
				that.getView().getModel("store").setProperty("/eg", eg);
				var gameId = that.getView().getModel("store").getProperty("/gameId");
				var gamePwd	= that.getView().getModel("store").getProperty("/gamePwd");
				var userName = that.getView().getModel("store").getProperty("/userName");
				var userId = that.getView().getModel("store").getProperty("/userId");
				eg.joinGame(gameId, gamePwd, userName,userId);
				//--If join was successful, go to lobby
				eg.getSocket().on('game_joined', data => {
					if(data !== null && data !== undefined){
						var players = data.players;
						that.getView().getModel("store").setProperty("/waitingPlayers", players);
						that.createAccessUrl(gameId, gamePwd);
					}                	
                	that.navToLobby();
				});	
				//--If join was not successful, show error message
				eg.getSocket().on('invalid_name_or_pwd', data => {
                	MessageBox.error("The game ID and/or your password is not correct");
            	});	
			}
		},


		/**
		 * Navigation
		 */
		navToUserName: function(source) {
			this.getView().getModel("store").setProperty("/commingFrom", source);
        	sap.ui.core.UIComponent.getRouterFor(this).navTo("userName");
		},

		navToLogin: function() {
        	sap.ui.core.UIComponent.getRouterFor(this).navTo("login");
		},

		navToPassword: function() {
        	sap.ui.core.UIComponent.getRouterFor(this).navTo("password");
		},

		navToCreateGame: function() {
        	sap.ui.core.UIComponent.getRouterFor(this).navTo("createGame");
		},
		navToLobby: function() {
        	sap.ui.core.UIComponent.getRouterFor(this).navTo("lobby");
		}

	});

});
