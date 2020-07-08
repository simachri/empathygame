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
			}), "view");	

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
		 * Navigation
		 */
		navToLogin: function() {
        	sap.ui.core.UIComponent.getRouterFor(this).navTo("login");
		},

		navToPassword: function() {
        	sap.ui.core.UIComponent.getRouterFor(this).navTo("password");
		},

	});

});
