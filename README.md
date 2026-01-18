# WebSocket Server  

## Simple Server to Client interaction

#### 1. Code Redeem Feature
##### When player's typed `SUMMER2016` on chat, Server will running command to give xp 3000 on sender.
#### 2. Dashboard Website
##### You can monitor who claims the redeem code on the Dashboard website.
#### 3. Server Broadcast
##### On the dashboard website you can send announcement messages from the server to the minecraft client.
#### 4. Database
##### The data will be stored at simple database using sqlite.
##
##### Run the server:
###### Activated the venv
```bash
venv\Scripts\activate
```
###### Then run
```bash
python server.py
```
###### Website port:
```bash
3002
```
###### WsServer port:
```bash
8000
```
##
##### You can customize the port and command at:
```bash
server.py
```
##### You can customize website styling at:
```bash
base.html
```
##

##### Client Side:
###### in chat type this command:
```bash
/connect your_ip:8000
```
###### or:
```bash
/wsserver your_ip:8000
```

## Tech used:
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Python](https://img.shields.io/badge/bedrockpy-black?style=for-the-badge&logo=python&logoColor=white)
![Jinja](https://img.shields.io/badge/jinja-black.svg?style=for-the-badge&logo=jinja&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
