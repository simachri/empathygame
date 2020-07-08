* *manifest.yml*: Required for the deployment to **SAP Cloud Platform**.
* *runtime.txt*: Required for the deployment to **SAP Cloud Platform**.

## Local Development

1. Start python backend. Assumed to run on localhost:8080
2. Go to /web and execute
    * npm config set @sap:registry https://npm.sap.com // Only the first time
    * npm install
    * npm run dev

The service is reachable on localhost:3000 where the api is accessable on localhost:3000/api and the ui is accessable on localhost:3000/ui.