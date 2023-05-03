import numpy as np
from matplotlib.animation import FuncAnimation
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserParam, Slider
from mesa.visualization.modules import ChartModule
from Enviroment import FireflyWorld
from Agent import Firefly


def firefly_portrayal(agent):
    if agent is None:
        return

    portrayal = {}
    if isinstance(agent, Firefly):
        portrayal["Shape"] = "circle"
        portrayal["r"] = 0.5
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0

        if agent.is_flashing():
            portrayal["Color"] = "red"
        else:
            portrayal["Color"] = "grey"
    else:
        portrayal["Shape"] = "rect"
        portrayal["w"] = 1
        portrayal["h"] = 1
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["Color"] = "#FFFFFF"
    return portrayal


canvas_element = CanvasGrid(firefly_portrayal, 30, 30, 500, 500)

# create the chart visualization
chart = ChartModule([{"Label": "Flashing", "Color": "Red"}], data_collector_name='datacollector')

model_params = {
    "height": 30,
    "width": 30,
    "cycle_length": Slider("Cycle length", 1, 10, 20, 1),
    "flash_length": Slider("Flash duration", 1, 1, 5, 1),
    "number_of_fly": Slider("Number of Fly", 1, 200, 2000, 10),
    "flash_reset": Slider("Flash to reset", 1, 1, 3, 1)
}

server = ModularServer(FireflyWorld,
                       [canvas_element, chart],
                       "Firefly Model",
                       model_params)


server.port = 8521
server.launch()


