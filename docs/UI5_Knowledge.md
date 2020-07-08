# SAP UI5 Knowledge

## Routing

### Routing Activation
To activate routing in your project, open your `Component.js` file and add the following:

```
/*
* Component.js
* return 
*/ 
// [...]
UIComponent.extend("<...>.Component", {
    // [...]
    init: function () {

			// [...]

			this.getRouter().initialize();
    }

});
// [...]

```

### Routing Definition
The routing definition is done in the `manfest.json` file:

```
"routing": {
			"config": {
				"routerClass": "sap.m.routing.Router",
				"viewType": "XML",
				"async": true,
				"viewPath": "empathygame.view",
				"controlAggregation": "pages",
				"controlId": "app",
				"clearControlAggregation": false
			},
			"routes": [
				{
					"name": "routeA",
					"pattern": "", #<-- empty means landing route
					"target": ["routeA"]
				},
				{
					"name": "routeB",
					"pattern": "routeB",  #<-- url e.g. http://localhost:3000/ui/index.html#/routeB
					"target": ["routeB"]
				}
			],
			"targets": {
				"routeA": {
					"viewType": "XML",
					"transition": "slide",
					"clearControlAggregation": false,
					"viewName": "RouteA" #<-- Name of view
				},
				"routeB": {
					"viewType": "XML",
					"transition": "slide",
					"clearControlAggregation": false,
					"viewName": "RouteB"
				}
			}
```

### Navigation
In the control you can navigate to other views by executing:

```
sap.ui.core.UIComponent.getRouterFor(this).navTo("routeB");

```