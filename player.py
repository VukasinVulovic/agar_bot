from custom_types import *
from agarClient import *
import numHelper as nh
import numpy as np

class Player:
    pos = Position(0, 0)
    radius = 0
    speed = 0
    state = PlayerState.WANDER
    name = None

    vision = VisibleField(500, [])

    def __init__(self, agar_client: AgarClient):
        self.__client = agar_client
        self.name = agar_client.bot_name

    def move_to(self, new_pos: Position):
        if self.__client != None:
            dp = (new_pos.x - self.pos.x, new_pos.y - self.pos.y)
            dp = nh.norm_vec(dp)

            dp = nh.mul_vec(dp, self.__client.screen_size)

            self.__client.move_by(dp[0], dp[1])

    def move_from(self, from_pos: Position):
        if self.__client != None:
            dp = (from_pos.x - self.pos.x, from_pos.y - self.pos.y)
            dp = nh.norm_vec(dp)
            dp = nh.mul_vec(dp, (-1, -1))
            dp = nh.mul_vec(dp, self.__client.screen_size)

            self.__client.move_by(dp[0], dp[1])

    def _handle_state(self):
        if len(self.vision.items) > 0:
            enemies = list(filter(lambda i: i.item_type == ItemType.ENEMY, self.vision.items))
            # shelter = list(filter(lambda i: i.item_type == ItemType.SHELTER, self.vision.items))

            if len(enemies) > 0:
                enemy = enemies[0] #add support for multiple enemies

                if nh.dis_vec((self.pos.x, self.pos.y), (enemy.pos.x, enemy.pos.y)) < self.vision.radius + self.radius + enemy.radius: #should care
                    if enemy.radius < self.radius: #if smaller than bot
                        self.state = PlayerState.ATTACK
                    else:
                        self.state = PlayerState.ESCAPE

        else:
            self.state = PlayerState.WANDER

        match self.state:
            case PlayerState.WANDER:
                food = list(filter(lambda i: i.item_type == ItemType.FOOD, self.vision.items))

                if len(food) > 0:
                    closest_blob = sorted(food, key=lambda i: abs(i.pos.x - self.pos.x) + abs(i.pos.y - self.pos.y))[0] #todo add to perfer clusters

                    self.move_to(closest_blob.pos)
                else:
                # self.move_to((0, 0))
                    pass #todo add if no food
                
            case PlayerState.ATTACK:
                if len(enemies) > 0:
                    closest_enemy = enemies[0] #add logic for multiple enemies
                    self.move_to(closest_enemy.pos)
                else:
                    self.state = PlayerState.WANDER

            case PlayerState.ESCAPE:
                if len(enemies) > 0:
                    closest_enemy = enemies[0] #add logic for multiple enemies
                    self.move_from(closest_enemy.pos)
                else:
                    self.state = PlayerState.WANDER

            case _:
                raise ValueError("Unknown state " + str(self.state))


    def observe_enviroment(self):
        self.pos = Position(self.__client.player["pos"][0], self.__client.player["pos"][1])
        self.radius = self.__client.player["r"]
        self.speed = self.__client.player["speed"]

        all_field_items = self.__client.enviroment["blobs"]

        field_items = []

        for item in all_field_items:
            item_type = ItemType.FOOD

            if "name" in item:
                if item["name"] == self.__client.bot_name:
                    item_type = ItemType.BOT
                else:
                    item_type = ItemType.ENEMY
            elif "fill" in item:
                item_type = ItemType.SHELTER
            else:
                item_type = ItemType.FOOD 

            radius = 0

            if item_type in (ItemType.BOT, ItemType.ENEMY):
                radius = item["cells"][0]["radius"] #todo add multiple blob support
            else:
                radius = item["radius"]

            field_items.append(Item(Position(item["x"], item["y"]), radius, item_type))

        self.vision = VisibleField(self.vision.radius, field_items)
        
        self._handle_state()