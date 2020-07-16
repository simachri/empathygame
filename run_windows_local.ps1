# Local Application Start

## Start backend
pipenv shell
### Set port
$Env:PORT = "8080"
### Start API
invoke-expression 'cmd /c start powershell -Command {write-host "Start empathygame api server"; py ./api/main.py }'


## Start @SAP/Approuter
### Set port
$Env:PORT = "3000"
### Start @SAP/Approuter
invoke-expression 'cmd /c start powershell -Command {write-host "Start empathygame approuter"; npm run dev --prefix ./web}'