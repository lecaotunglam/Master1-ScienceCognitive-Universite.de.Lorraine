# from mesa import Model, Agent
# from mesa.space import MultiGrid
# from mesa.time import RandomActivation
# from mesa.visualization.modules import CanvasGrid
# from mesa.visualization.ModularVisualization import ModularServer
#
#
# class MyAgent(Agent):
#     def __init__(self, unique_id, model):
#         super().__init__(unique_id, model)
#         self.color = "grey"
#
#     def step(self):
#         # Define the agent's behavior in each step
#         self.color = "yellow" if self.color == "grey" else "grey"
#
#
# class MyModel(Model):
#     def __init__(self, N):
#         self.num_agents = N
#         self.schedule = RandomActivation(self)
#         self.grid = MultiGrid(10, 10, torus=True)
#
#         # Create agents
#         for i in range(self.num_agents):
#             a = MyAgent(i, self)
#             self.schedule.add(a)
#             x = self.random.randrange(self.grid.width)
#             y = self.random.randrange(self.grid.height)
#             self.grid.place_agent(a, (x, y))
#
#         # Define visualization
#         self.grid_canvas = CanvasGrid(self.draw_agent, 10, 10, 500, 500)
#         self.server = ModularServer(MyModel,
#                                     [self.grid_canvas],
#                                     "My Model",
#                                     {"N": N})
#
#     def step(self):
#         self.schedule.step()
#         self.grid_canvas._buffer = self.grid_canvas.draw_cell_grid(self.grid)
#
#     def draw_agent(self, agent):
#         return {"Shape": "circle",
#                 "r": 0.5,
#                 "Filled": True,
#                 "Color": agent.color}
#
# model = MyModel(10)
# model.server.launch()

import math
import random
from mesa import Agent, Model
from mesa.space import ContinuousSpace
from mesa.time import RandomActivation
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter


class Firefly(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos
        self.color = "yellow"
        self.turns_left = random.randint(10, 30)

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False)
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)
        self.turns_left -= 1
        if self.turns_left <= 0:
            self.color = "black"
            self.model.schedule.remove(self)


class FireflyModel(Model):
    def __init__(self, num_fireflies):
        self.num_fireflies = num_fireflies
        self.grid = ContinuousSpace(20, 20, True)
        self.schedule = RandomActivation(self)
        self.running = True

        # Create fireflies
        for i in range(self.num_fireflies):
            x = self.random.random() * self.grid.width
            y = self.random.random() * self.grid.height
            firefly = Firefly(i, self, (x, y))
            self.grid.place_agent(firefly, (x, y))
            self.schedule.add(firefly)

    def step(self):
        self.schedule.step()
        if self.schedule.get_agent_count() == 0:
            self.running = False


def firefly_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Color": agent.color,
                 "Filled": "true",
                 "r": 0.5}
    return portrayal


model_params = {"num_fireflies": UserSettableParameter('slider', 'Number of fireflies', 10, 1, 100)}

canvas_element = CanvasGrid(firefly_portrayal, 20, 20, 500, 500)

server = ModularServer(FireflyModel,
                       [canvas_element],
                       "Firefly Model",
                       model_params)

server.port = 8521
server.launch()


import numpy as np
import matplotlib.pyplot as plt
from plotnine import *
import pandas as pd
%matplotlib inline

from mesa import Agent,Model
from mesa.time import SimultaneousActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

class Firefly(Agent):
    def __int__(self,unique_id,pos,model):
        super().__init__(unique_id,model)
        self.pos = pos
        self.clock = self.random.randint(1,10)

    def is_flashing(self):
        return self.clock == 1

    def step(self):
        self.clock = self.clock+1
        if self.clock > 10:
            self.clock == 1


class FireflyWorld(Model):
    def __init__(self, height=30, width=30):
        super().__init__()
        self.schedule = SimultaneousActivation(self)
        self.grid = MultiGrid(height,width, torus=True)
        self.dc = DataCollector({"Flashing":lambda m: self.count_flashing()})

        for i in range(2000): #2000 is the number of fly
            pos = (self.random.randint(0,width-1),
                   self.random.randint(0,height-1))
            f = Firefly(self.next_id(),pos,self)
            self.grid.place_agent(f,pos)
            self.schedule.add(f)

        self.running = True

    def step(self):
        self.schedule.step()
        self.dc.collect(self)

        if self.schedule.time > 500:
            self.running = False

    def count_flashing(self):
        count = 0
        for f in self.schedule.agents:
            if f.is_flashing():
                count+=1
        return count

ff = FireflyWorld(30,30)