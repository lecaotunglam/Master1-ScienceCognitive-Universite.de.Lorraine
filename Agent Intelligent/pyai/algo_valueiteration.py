# -*- coding: utf-8 -*-

"""
Implements Value Iteration for a MazeGridWorld (states) and Agent (for actions)

"""
import sys
import tkinter as tk

from .core import Agent, Module
from environments.mazegridworld import Movable, ActionGrid
from .utils import _xscreen, _yscreen
# ******************************************************************************
# *********************************************************** AlgoValueIteration
# ******************************************************************************
class AlgoValueIteration(Module):
    """
    """
    # ----------------------------------------------------------------- __init__
    def __init__(self, agent):
        Module.__init__(self, agent)

        ## TkVAr for activation
        self.activated = None # created in build_gui
        self.console = None   # tk_console
        
        ## Need states and actions
        # Get list of cells from World
        self.state_value = {}
        for idr in range(self.world.nbrow):
            for idc in range(self.world.nbcol):
                if self.world.cell_matrix[idr][idc] != 'X':
                    state = ("cell_"+self.world.cell_matrix[idr][idc], "*")
                    self.state_value[state] = 0.0
        print( "__ALGO STATE_VALUE", self.state_value )
        
        # Get list of action from Agent
        self.actions = [ "move_right()",
                          "move_left()" ]
                          # "move_up()",
                          # "move_down()" ]

        ## Need rewarded states
        self.reward_state = { ("cell_2","*") : 10.0 }
        self.gamma = 0.8
        
        ## Need terminal states
        self.terminal_state = [("cell_2", "*",)]

        ## Need to compute Transitions
        self.trans = {}
        for s in self.state_value.keys():
            for a in self.actions:
                    self.trans[(s,a)] = []
        self._compute_transitions()
        print( "__ALGO TRANS", self.trans )

    # ---------------------------------------------------------------- desrcribe
    def describe(self):
        msg = """**Value Iteration**\n  (algorithme de planification par programmation dynamique)\n"""
        msg += """\n- activé (O/N) : affiche les valeurs dans les "cells"""
        msg += """\n- reset : remet toutes les "Valeurs" à 0"""
        msg += """\n- step : une itération de l'algoritme Value Iteration"""
        msg += """\n- run : lance des itérations jusqu'à convergence\n  (différence de la somme des carrés des valeurs entre deux itérations inférieur à 0.01)"""
        
        return msg
    # ----------------------------------------------- PRIV _compute_transistions
    def _compute_transitions(self):
        ## Need Virtual Agent
        self.vi_agent = Agent( self.agent.env )
        self.vi_mov_agent = Movable( self.vi_agent, 0, 0 )
        self.world.movable_l.append( self.vi_mov_agent )
        self.vi_agent.action_module.add_module(ActionGrid( self.vi_agent ))
        ## Tries all actions in evert state
        for s in self.state_value.keys():
            if not s in self.terminal_state:
                for a in self.actions:
                    ## puts vi_agent in the propor position
                    cellname = s[0]
                    cell_id = cellname[5:]
                    cellx, celly = self.world.pos_from_cellid( cell_id )

                    self.vi_mov_agent.posx = cellx
                    self.vi_mov_agent.posy = celly
                    self.vi_agent.action = [a]
                    self.vi_agent.act()
                    # new state
                    newsx = self.vi_mov_agent.posx
                    newsy = self.vi_mov_agent.posy
                    new_state = "cell_"+str(self.world.index_from_pos(newsx, newsy))

                    print( f" {s} + {a} => {new_state}" )
                    self.trans[(s,a)].append( (1.0, (new_state,"*")) )

    # ------------------------------------------------------------------ Actions
    def reset(self):
        for s in self.state_value.keys():
            self.state_value[s] = 0.0
        if self.console:
            self.console.display( f"__VI ALGO reset" )

    def step(self, verb=False):
        """
        Return: la somme des carrés de différences de valeurs
        """
        delta_v = 0.0
        ## Copy the current values
        cur_statevalue = self.state_value.copy()

        ## Compute new values
        for s in self.state_value.keys():
            if verb:
                print( f"  s={s}" )
                
            max_val = - sys.float_info.max
            for a in self.actions:
                value = 0.0
                for prob, news in self.trans[(s,a)]:
                    value += self.gamma * prob * cur_statevalue[news]
                    if news in self.reward_state:
                        value += self.reward_state[news]

                if verb:
                    print( f"    value of action {a} = {value}" )
                if value > max_val:
                    max_val = value

            delta_v += (max_val - cur_statevalue[s])**2
            self.state_value[s] = max_val
            if verb:
                print( f"  => new value={max_val}" )

        if self.console:
            self.console.display( f"__VI ALGO step, delta_v={delta_v}" )

        return delta_v

    def run(self):
        delta_v = sys.float_info.max # max float (ie: infinity)
        count = 0
        while delta_v > 0.01:
            delta_v = self.step()
            count += 1

        print( f"__VI ALGO convergence en {count} steps" )
        if self.console:
            self.console.display( f"__VI ALGO convergence en {count} steps" )

    # --------------------------------------------------------------------- draw
    def draw(self, canvas):
        """Text sous le nom des cells
        """
        if self.activated.get() == 1:
            ## Cells
            for y in range( self.world.nbrow ):
                for x in range( self.world.nbcol ):
                    id = self.world.cell_matrix[y][x]
                    if id != 'X':
                        msg = "val={:5.1f}".format(self.state_value[('cell_'+str(id),'*')])
                        canvas.create_text( _xscreen( x+0.5 ), _yscreen( y+0.25 ),
                                            fill="black",
                                            text=msg )

    # ---------------------------------------------------------------- build_gui
    def build_gui(self, parent, console ):
        self.console = console
        ## variable can only created after Tk "started"
        self.activated = tk.IntVar()
        
        mod_frame = tk.Frame( parent, bd=5, relief=tk.GROOVE )
        mod_frame.pack()

        # Able/Disable
        active_btn = tk.Checkbutton( mod_frame,
                                     variable = self.activated,
                                     text="activé",
                                     anchor='w' )
        active_btn.select() # deselect(), toggle()
        active_btn.grid( row=0, column=0, padx=5, pady=5,
                         columnspan=2)

        # Actions
        step_btn = tk.Button( mod_frame, text='Step',
                               command = self.step )
        step_btn.grid( row=1, column=0, padx=5, pady=5 )
        run_btn = tk.Button( mod_frame, text='Run',
                               command = self.run )
        run_btn.grid( row=1, column=1, padx=5, pady=5 )
        reset_btn = tk.Button( mod_frame, text='Reset',
                               command = self.reset )
        reset_btn.grid( row=1, column=2, padx=5, pady=5 )
        
        return mod_frame

# ************************************************************************* END 

    
                                        

            
