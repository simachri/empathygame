sap.ui.define([
	"sap/ui/Device",
	"sap/ui/core/mvc/Controller",
	"sap/ui/model/json/JSONModel",
	'sap/m/MessageBox',
	'sap/m/MessageToast'
], function(Device, Controller, JSONModel, MessageBox, MessageToast ) {
	"use strict";


	return Controller.extend("empathygame.controller.Lobby", {

		onInit: function() {

			var store = this.getOwnerComponent().getModel("store"); 
			var waitingPlayers = store.getProperty("/waitingPlayers");
			
			this.getView().setModel(new JSONModel({
				isMobile: Device.browser.mobile,
				players: waitingPlayers,
				rolesAssigned: false
			}));		
			
			var eg = store.getProperty("/eg");

			//--Update view if player are joining or leaving...
			eg.getSocket().on('players_changed', data => {
				MessageToast.show ("Players in lobby changed");
				if(data !== null && data !== undefined){
					store.setProperty("/waitingPlayers", data.players);
					this.getView().setModel(new JSONModel({						
						players: data.players
					}));
				}
			});	
			//--Update view if roles are assigned
			eg.getSocket().on('roles_assigned', data => {
				MessageToast.show ("All roles assigned!");
				if(data !== null && data !== undefined){
					store.setProperty("/waitingPlayers", data.players);
					this.getView().setModel(new JSONModel({						
						players: data.players,
						rolesAssigned: true
					}));
				}
			});			
		},

		/**
		 * Redirect if not logged in
		*/
		onBeforeRendering: function() {

			//--Check if we are logged in, otherwise route to login
			//if(this.getView().getModel("store").getProperty("/gameId") === ""){
			//	sap.ui.core.UIComponent.getRouterFor(this).navTo("router");
			//}		
		}, 

		onAfterRendering: function(){

		},

		/**
		 * 
		 * Copies the current link to clipboard
		 */
		copyLink: function(){
			var textArea = document.createElement('textarea');
			textArea.setAttribute('style','width:1px;border:0;opacity:0;');
			document.body.appendChild(textArea);
			textArea.value = this.getView().getModel("store").getProperty("/accessUrl");
			textArea.select();
			document.execCommand('copy');
			document.body.removeChild(textArea);
			MessageToast.show ("Game access URL copied to clipboard");
		},

		/**
		 * Emit event to assign roles to all users
		 */
		assignRoles: function(){
			var eg = this.getView().getModel("store").getProperty("/eg");
			eg.assignRoles();
		},

		/**
		 * Start the game
		 */
		startGame: function(){
			MessageToast.show ("Starting the game... (Not yet implemented)");
		},

		/**
		 * Call hello world test
		 */
		callToGetWelcomeMessage: function(){
			var that = this;
			return jQuery
				.ajax({
				url: "/api/hello",
				method: "GET",
				beforeSend: function(xhr){
					xhr.setRequestHeader('X-Csrf-Token', 'fetch');
				},
				})
				.success(function(json, textStatus, request) {

				// Check if we face mult. repositories
				if(json !== null && json !== undefined){
					// Take first entry as default
					that.getView().getModel().setProperty("/welcomeMessage", json.message);
				} 
				else{
					MessageBox.error("Payload is null or undefined");
				}     
				}).always(function(res, textStatus, request) { that.addXcrfTokenHeader(request)});//--Add new updated X-CSRF-Token 
		},
		
		/**
		 * Navigation
		 */
		 navToHome: function() {
        	document.location.href="/";
		}

	});

});
