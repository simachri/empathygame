# Innovator Challenge Group 424 - Empathy Game

* *manifest.yml*: Required for the deployment to **SAP Cloud Platform**.
* *runtime.txt*: Required for the deployment to **SAP Cloud Platform**.

## Local Development

### Start python backend

Assumed to run on localhost:8080

### Start application router

For the first time, please add @sap to you npm and install all dependencies:
```
# Add @sap to your npm
npm config set @sap:registry https://npm.sap.com // Only the first time
# Install all dependencies
npm install
```

After preparation you can start the application router by:
```
# Go to web folder
cd web
# Start development server
npm run dev
```

The service is reachable on localhost:3000 where the api is accessable on localhost:3000/api and the ui is accessable on localhost:3000/ui.