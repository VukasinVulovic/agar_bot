import asyncio
from player import Player
from agarClient import AgarClient
import random

SERVER_ADDRESS = "192.168.1.2:3004"
BOT_NAME = "OwO_" + str(random.randint(0, 100000))
SCREEN_W = 1080
SCREEN_H = 720

async def main():
    client = AgarClient(SERVER_ADDRESS, BOT_NAME, (SCREEN_W, SCREEN_H))
    client.connect()

    player = Player(client)
    
    while True:
        print(str(player.pos) + " " + str(player.state))

        client.receive_events()
        player.observe_enviroment()

if __name__ == "__main__":  
    asyncio.run(main())