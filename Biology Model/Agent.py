import math

from mesa import Agent
import random


class Firefly(Agent):
    def __init__(self, unique_id, pos, model):
        super().__init__(unique_id, model)
        self.pos = pos
        self.clock = self.random.randint(1, self.model.cycle_length)

    def is_flashing(self):
        return self.clock <= self.model.flash_length

    def step(self):
        # self.clock = self.clock+1
        self._next = self.clock + 1
        if self._next > self.model.cycle_length:
            self._next = 1

        if not self.is_flashing():
            neighbours = self.model.grid.get_neighbors(self.pos, True)
            for neighbour in neighbours:
                if neighbour.is_flashing():
                    self._next = self.model.flash_length + 1

    def advance(self):
        self.clock = self._next
        self.move()

    def move(self):
        next_moves = self.model.grid.get_neighborhood(self.pos, True, True)
        next_move = self.random.choice(next_moves)
        self.model.grid.move_agent(self, next_move)
