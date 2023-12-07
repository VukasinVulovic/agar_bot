import requests
import json
import websockets.sync.client as wsc
import time
import re
import numHelper as nh
from custom_types import *

class AgarClient:
    server_address = None
    bot_name = None
    pid = None #player id
    screen_size = (0, 0)

    connected = False

    _ws_conn = None

    player = {
        "id": None,
        "pos": (0,0),
        "r": 0.0,
        "speed": 0.0
    }

    enviroment = {
        "blobs": []
    }

    def _parse_ws_event(self, msg):
        match = re.match(r"^[0-9]{1,3}(.+)", msg)

        if match == None:
            return None

        groups = match.groups()

        if len(groups) < 1:
            return None

        msg = json.loads(groups[0])

        if type(msg) != list:
            return None

        return {
            "event": msg[0],
            "data": msg[1:]
        }

    def __init__(self, server_address, bot_name, screen_size=(640, 480)):
        self.server_address = server_address
        self.bot_name = bot_name
        self.screen_size = screen_size

    def move_by(self, x, y):
        self._ws_conn.send("42[\"0\",{\"x\":"+str(x)+",\"y\":"+str(y)+"}]")

    def receive_events(self):        
        msg = self._ws_conn.recv()
        msg = self._parse_ws_event(msg)

        if msg is None:
            return

        data = msg["data"]


        # with open("out.txt", "a+") as f:
        #     f.write(json.dumps(data))

        match msg["event"]:
            case "serverTellPlayerMove":
                # if len(data[0]["cells"]) > 1:
                #     raise NotImplementedError("Not implemented split blob")

                self.player = {
                    "id": self.player["id"],
                    "pos": (data[0]["x"], data[0]["y"]),
                    "r": data[0]["cells"][0]["radius"],
                    "speed": data[0]["cells"][0]["speed"]
                }

                self.enviroment = {
                    "blobs": nh.flatten_array(data[1:]) # add filter for players and hide spots
                }

            # case _:
            #     raise ValueError(f"Unknown event {msg['event']}")

    def connect(self):
        #get socket id
        res = requests.get(f"http://{self.server_address}/socket.io/?type=player&EIO=4&transport=polling")
    
        if res.status_code != 200:
            raise ConnectionError(f"Could not connect, {res.status_code}: {res.text}")

        sid = json.loads(re.match(r"^[0-9]{1,3}(.+)", res.text).group(1))["sid"]

        res = requests.post(f"http://{self.server_address}/socket.io/?type=player&EIO=4&transport=polling&sid={sid}", data="40")
    
        if res.status_code != 200:
            raise ConnectionError(f"Could not connect, {res.status_code}: {res.text}")
        
        res = requests.get(f"http://{self.server_address}/socket.io/?type=player&EIO=4&transport=polling&sid={sid}")
    
        #get player id
        if res.status_code != 200:
            raise ConnectionError(f"Could not connect, {res.status_code}: {res.text}")

        pid = json.loads(re.match(r"^[0-9]{1,3}(.+)", res.text).group(1))["sid"]
        self.player["id"] = pid

        #connect to websocket and send join info
        
        ws = wsc.connect(f"ws://{self.server_address}/socket.io/?type=player&EIO=4&transport=websocket&sid={sid}")
        self._ws_conn = ws

        ws.send("2probe")
        message = ws.recv()

        if message != "3probe":
            raise ConnectionError("Server refused to connect or is using other API.")
        
        ws.send("5")

        epoch_now = int(time.time())

        ws.send("42[\"gotit\",{\"id\":\"{"+pid+"}\",\"hue\":28,\"name\":\""+str(self.bot_name)+"\",\"admin\":false,\"screenWidth\":"+str(self.screen_size[0])+",\"screenHeight\":"+str(self.screen_size[1])+",\"timeToMerge\":null,\"lastHeartbeat\":"+str(epoch_now)+",\"target\":{\"x\":0,\"y\":0}}]")
        ws.send("42[\"0\",{\"x\":0,\"y\":0}]")

        message = ws.recv()

        parsed_msg = self._parse_ws_event(message)

        if parsed_msg["event"] != "playerJoin" or parsed_msg["data"][0]["name"] != self.bot_name:
            raise ConnectionError("Could not join session.")