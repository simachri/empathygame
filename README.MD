# Deployment to SAP Cloud Platform

* *manifest.yml*: Required for the deployment to **SAP Cloud Platform**.
* *runtime.txt*: Required for the deployment to **SAP Cloud Platform**.

# Local development

## Python backend (start first)

1. Install [Cloud Foundry CLI](https://github.com/cloudfoundry/cli#downloads)
2. Log on to our Cloud Foundry Environment through the CLI [Source](https://help.sap.com/viewer/65de2977205c403bbc107264b8eccf4b/Cloud/en-US/7a37d66c2e7d401db4980db0cd74aa6b.html):
	* `cf login`
	* API endpoint: https://api.cf.eu10.hana.ondemand.com  (taken from our Subaccount overview page)
	* Email: `<your SAP mail address>`
	* Password: `<your SSO SAP password>`
3. Create new Python project with your favourite IDE.
4. Use _Pipenv_ for dependency management.
5. Clone the Github repo https://github.com/simachri/empathygame.
6. Run `pipenv install` to install the dependencies locally.
7. This is an example launch configuration from PyCharm:
![PyCharm run configuration](docs/resources/run_config_pycharm.png)

## Frontend (start second)

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