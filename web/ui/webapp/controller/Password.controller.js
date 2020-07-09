sap.ui.define([
	"sap/ui/Device",
	"sap/ui/core/mvc/Controller",
	'sap/m/MessageBox',
	"sap/ui/model/json/JSONModel"
], function(Device, Controller, MessageBox, JSONModel) {
	"use strict";


	return Controller.extend("empathygame.controller.Password", {

		onInit: function() {

			this.getView().setModel(new JSONModel({
				isMobile: Device.browser.mobile,
			}), "view");	
		},

		/**
		 * Redirect if gameId is not defined yet
		 */
		onBeforeRendering: function() {

			//--Check if we know the game id. Otherwise ask for it.
			if(this.getView().getModel("store").getProperty("/gameId") === ""){
				sap.ui.core.UIComponent.getRouterFor(this).navTo("login");
			}
		},
		
		/**
		 * Function to access game on backend
		 */
		accessGame: function(oEvent) {

			//--Check if password was given
			if(this.getView().getModel("store").getProperty("/gamePwd") === ""){
				MessageBox.error("Please enter your password");
			}
			else{
				//--Submit data to get access
				this.getView().getModel("store").setProperty("/gamePwd", "****");
				//--Navigate to landing page
				this.navToLobby();
			}
		},

		/**
		 * Navigation
		 */
		navToLogin: function() {
        	sap.ui.core.UIComponent.getRouterFor(this).navTo("login");
		},
		navToLobby: function() {
        	sap.ui.core.UIComponent.getRouterFor(this).navTo("lobby");
		}
	});
});
