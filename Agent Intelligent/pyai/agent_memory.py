# -*- coding: utf-8 -*-

"""
Ajouter à l'Agent la possibilité de mémoriser des informations,
de s'en "souvenir" (elle sont présentes dans la perception).

La "Mémoire" est une liste de string.

Se compose donc de 2 modules
MemoryAction : memorize( str ), forget( str ), reset_memory()
MemoryPerception : ajoute le mémoire dans la perception
"""

from .core import Module

# ******************************************************************************
# ***************************************************************** MemoryAction
# ******************************************************************************
class MemoryAction(Module):
    """
    Définit les actions et rajoute une mémoire à l'agent.
    - memorize_info( str )
    - forget_info( str )
    - reset_memory()
    """
    def __init__(self, agent):
        self.agent = agent
        self.world = agent.env

        # add an empty memory to the agent
        self.agent.memory = []

        # add new methods to the agent
        setattr( agent, 'memorize', self.memorize )
        setattr( agent, 'forget', self.forget )
        setattr( agent, 'reset_memory', self.reset_memory )

    def describe(self):
        msg = """- "memorize( STR )" : ajoute STR dans la mémoire\n"""
        msg += """- "forget( STR )" : efface STR de la mémoire\n"""
        msg += """- "reset_memory()" : efface toute la mémoire\n"""
        return msg

    def memorize(self, info):
        if not info in self.agent.memory:
            self.agent.memory.append( info )

    def forget(self, info):
        if info in self.agent.memory:
            self.agent.memory.remove( info )

    def reset_memory(self):
        self.agent.memory = []

# ******************************************************************************
# ************************************************************* MemoryPerception
# ******************************************************************************
class MemoryPerception(Module):
    def __init__(self, agent):
        self.agent = agent
        self.world = agent.env

    def describe(self):
        msg = """- "info" pour chaque info de la mémoire de l'agent\n"""
        return msg

    def apply(self):
        return self.agent.memory

