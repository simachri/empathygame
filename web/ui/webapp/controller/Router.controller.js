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

		/**
		 * Reads the url parameter and checks if
		 * game id and game password are given. 
		 */
		getDirectGameLink: function(){
			
			const queryString = window.location.search;
			const urlParams = new URLSearchParams(queryString);
			var resOb = null;
			var gameId = urlParams.get('game_id');
			var gamePwd = urlParams.get('game_pwd');

			if( (gameId !== null && gameId !== undefined && gameId !== "") &&
				(gamePwd !== null && gamePwd !== undefined && gamePwd !== "") )
			{
				resOb = {};
				resOb.gameId = gameId;
				resOb.gamePwd = gamePwd;
				var baseUrl = location.protocol + '//' + location.host + location.pathname;
				window.history.replaceState({}, "" , baseUrl );
			}
			return resOb;
		},

		initializeLocalStorageGameInfo: function(store){

			var userId = window.localStorage.getItem('empathygame.userId');
			var userName = window.localStorage.getItem('empathygame.userName');
			var gameId = window.localStorage.getItem('empathygame.gameId');
			var gamePwd = window.localStorage.getItem('empathygame.gamePwd');

			store.setProperty('/userId', userId !== null ? userId : store.getProperty('/userId'));
			store.setProperty('/userName', userName !== null ? userName : store.getProperty('/userName'));
			store.setProperty('/gameId', gameId !== null ? gameId : store.getProperty('/gameId'));
			store.setProperty('/gamePwd', gamePwd !== null ? gamePwd : store.getProperty('/gamePwd'));
		},

		setLocalStorageGameInfo: function(store){
			window.localStorage.setItem('empathygame.userId', store.getProperty('/userId'));
			window.localStorage.setItem('empathygame.userName', store.getProperty('/userName'));
			window.localStorage.setItem('empathygame.gameId', store.getProperty('/gameId'));
			window.localStorage.setItem('empathygame.gamePwd', store.getProperty('/gamePwd'));
		},

		onInit: function() {
			
			//--Define local JSON model
			this.getView().setModel(new JSONModel({
				isMobile: Device.browser.mobile,
				userInitials: "CL",
				navFrom: "",
				gameOn: false
			}));	

			//--Read global store
			var store = this.getOwnerComponent().getModel("store"); 

			//--Check if our store is initial and load from local store if so
			if(store.getProperty('/gameId') === "" && store.getProperty('/gamePwd') === ""){
				this.initializeLocalStorageGameInfo(store);
			}			

			//--Check on what screen we are and if we have to re-route the user
			switch(this.getView().sViewName) {
				case 'empathygame.view.Router':
					//--Inital screen, check url params
					var directGameLink = this.getDirectGameLink();
					if( directGameLink  !== null ){
						store.setProperty('/gameId', directGameLink.gameId);
						store.setProperty('/gamePwd', directGameLink.gamePwd);
						this.navToUserName('direct');
					}
				break;
			}

			//--Check if a game is ongoing
			if(store.getProperty('/gameId') !== "" && store.getProperty('/gamePwd') !== "" && store.getProperty('/userId') !== null){
				this.getView().getModel().setProperty('/gameOn', true);
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
				eg.joinGame(gameId, gamePwd, userName, userId);
				//--If join was successful, go to lobby
				eg.getSocket().on('game_joined', data => {
					if(data !== null && data !== undefined){
						that.getView().getModel("store").setProperty("/gameId", data.game_id);
						that.getView().getModel("store").setProperty("/gamePwd", data.game_pwd);
						that.getView().getModel("store").setProperty("/userId", data.user_id);
						that.getView().getModel("store").setProperty("/userName", data.user_name);
						var players = data.players;
						that.getView().getModel("store").setProperty("/waitingPlayers", players);
						that.createAccessUrl(gameId, gamePwd);
						that.setLocalStorageGameInfo( that.getView().getModel("store"));
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
		 navToHome: function() {
        	document.location.href="/";
		},
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
