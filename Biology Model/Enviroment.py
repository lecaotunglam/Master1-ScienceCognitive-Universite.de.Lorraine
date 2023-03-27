import random

from mesa import Model
from mesa.space import MultiGrid, ContinuousSpace
from mesa.time import RandomActivation
from mesa import Agent,Model
from mesa.time import SimultaneousActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from Agent import Firefly


class FireflyWorld(Model):
    def __init__(self, height=30, width=30, cycle_length=10, flash_length=1):
        super().__init__()
        self.cycle_length = cycle_length
        self.flash_length = flash_length

        self.schedule = SimultaneousActivation(self)
        self.grid = MultiGrid(height,width, torus=True)
        self.dc = DataCollector({"Flashing":lambda m: self.count_flashing()})

        for i in range(200): #200 is the number of fly
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