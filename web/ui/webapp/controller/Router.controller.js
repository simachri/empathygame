sap.ui.define([
	"sap/ui/Device",
	"sap/ui/core/mvc/Controller",
	'sap/m/MessageBox',
	"sap/ui/model/json/JSONModel"
], function(Device, Controller, MessageBox, JSONModel) {
	"use strict";


	return Controller.extend("empathygame.controller.Router", {

		onInit: function() {

			this.getView().setModel(new JSONModel({
				isMobile: Device.browser.mobile,
				navFrom: "",
			}));	

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
				
				}	
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

	});

});
