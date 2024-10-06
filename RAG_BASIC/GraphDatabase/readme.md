## Install
https://neo4j.com/docs/operations-manual/current/installation/
install desktop version too


### 1. In console
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/neotechnology.gpg
echo 'deb [signed-by=/etc/apt/keyrings/neotechnology.gpg] https://debian.neo4j.com stable latest' | sudo tee -a /etc/apt/sources.list.d/neo4j.list
sudo apt-get update

### 2. install console - Community Edition
sudo apt-get install neo4j=1:5.22.0

## Once installed
### 1. check status

sudo systemctl status neo4j

### 2. start service
sudo systemctl start neo4j

### 3. stop serviceDefault login is username 'neo4j' and password 'neo4j'
sudo systemctl stop neo4j

### 4. Enable Neo4j to Start on Boot
sudo systemctl enable neo4j

### 5. Disable Neo4j from Starting on Boot
sudo systemctl disable neo4j


### 6. View Neo4j Logs
sudo journalctl -u neo4j


## Configure service web-browser
http://localhost:7474/browser/
Default login is username 'neo4j' and password 'neo4j'





## APOC
if error APOC please go to Desktop APP, select project and plugins tab, install APOC



pip install neo4j