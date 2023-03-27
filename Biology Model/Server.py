from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserParam, Slider
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
            portrayal["Color"] = "yellow"
        else:
            portrayal["Color"] = "green"
    else:
        portrayal["Shape"] = "rect"
        portrayal["w"] = 1
        portrayal["h"] = 1
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["Color"] = "#FFFFFF"
    return portrayal


canvas_element = CanvasGrid(firefly_portrayal, 30, 30, 500, 500)

model_params = {
    "height": 30,
    "width": 30,
    "cycle_length": Slider("Cycle length", 1, 10, 20, 1),
    "flash_length": Slider("Flash duration", 1, 1, 5, 1)
}

server = ModularServer(FireflyWorld,
                       [canvas_element],
                       "Firefly Model",
                       model_params)

server.port = 8521
server.launch()
