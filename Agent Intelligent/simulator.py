#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# test_simutk : GUI avec Environnement DISCRET (mais manque pervieve ?)
# test_steps : TEXTUEL, teste actions agent dans world.py (discret)
# test_alpha : test affichage de Environnement CONTINU, et qq perceptions
# test_sim_alpha : test Simulateur, perceive, run en CONTINU
# test_option : test simulator en utilisant l'Environment passé en option
#        ex  python3 simulation.py world

import sys
import argparse

from pyai.core import Simulator
from pyai.tk_simu import TkSimu
# import world
# import tk_simu


# ******************************************************************************
# **************************************************** MazeGridWorld Environment
# ******************************************************************************
def create_mazegridworld( parsed_args ):
    """
    Create app with simulator 'sim' of an MazeGridWorld
    Return: sim, app
    """
    from environments.mazegridworld import (MazeGridWorld,
                                            ObservationGrid,
                                            PerceptionGrid)
    from pyai.agent_memory import MemoryPerception, MemoryAction

    # -------------------------------------------------------------- Environment
    class Environment(MazeGridWorld):
        def __init__(self):
            MazeGridWorld.__init__(self, args.filename)

            if args.obs:
                print( "__Agent Perception de OBSERVATION ***************" )
                self.agent.perception_module.add_module( ObservationGrid( self.agent ))
            else:
                print( "__Agent Perception de ETAT **********************" )
                self.agent.perception_module.add_module( PerceptionGrid(self.agent))

            if args.mem:
                print( "__ADDING Memory to Agent ************************" )
                self.agent.perception_module.add_module( MemoryPerception( self.agent ))
                self.agent.action_module.add_module( MemoryAction( self.agent ))
            
            self.agent.perceive()

    # -----------------------------------------------------------  run Simulator
    sim = Simulator( Environment )
    app = TkSimu( sim, "MazeGrid World" )

    # Ajoute Value Iteration ??
    if args.value_iteration:
        from pyai.algo_valueiteration import AlgoValueIteration
        vi = AlgoValueIteration(sim.agent)
        sim.add_algo( vi, "VI Algo" )
    
    return sim, app
# ************************************************************************** END

# ******************************************************************************
# **************************************************** MazeRealWorld Environment
# ******************************************************************************
def create_mazerealworld( parsed_args ):
    """
    Create app with simulator 'sim' of an MazeRealdWorld
    Return: sim, app
    """
    from environments.mazerealworld import (MazeRealWorld,
                                            PerceptionReal)
    from pyai.agent_memory import MemoryPerception, MemoryAction

    # -------------------------------------------------------------- Environment
    class Environment(MazeRealWorld):
        def __init__(self):
            MazeRealWorld.__init__(self, args.filename)

            # if args.obs:
            #     print( "__Agent Perception de OBSERVATION ***************" )
            #     self.agent.perception_module.add_module( ObservationGrid( self.agent ))
            # else:
            #     print( "__Agent Perception de ETAT **********************" )
            #     self.agent.perception_module.add_module( PerceptionGrid(self.agent))

            # if args.mem:
            #     print( "__ADDING Memory to Agent ************************" )
            #     self.agent.perception_module.add_module( MemoryPerception( self.agent ))
            #     self.agent.action_module.add_module( MemoryAction( self.agent ))
            
            # self.agent.perceive()

    # -----------------------------------------------------------  run Simulator
    sim = Simulator( Environment )
    app = TkSimu( sim, "MazeReal World" )

    # # Ajoute Value Iteration ??
    # if args.value_iteration:
    #     from pyai.algo_valueiteration import AlgoValueIteration
    #     vi = AlgoValueIteration(sim.agent)
    #     sim.add_algo( vi, "VI Algo" )
    
    return sim, app
# ************************************************************************** END

# ******************************************************************************
# ************************************************************************* MAIN
# ******************************************************************************

## Argument to parse
parser = argparse.ArgumentParser()
parser.add_argument( 'filename',
                     default="fourcell_maze.txt",
                     nargs='?',
                     help="Filename de l'environnement" )
parser.add_argument( '-e', '--env',
                     choices=['MazeGrid', 'MazeReal'],
                     default='MazeGrid',
                     help="Environement utilisé")
parser.add_argument( '-o', '--obs',
                     action='store_true',
                     help="Observation de l'Etat" )
parser.add_argument( '-m', '--mem',
                     action='store_true',
                     help="Ajoute une mémoire à l'Agent" )
parser.add_argument( '--value_iteration',
                     action='store_true',
                     help="Ajoute l'Algorithme Value Iteration" )
args = parser.parse_args( sys.argv[1:] )

print( "args", args)

if args.env == 'MazeGrid':
    sim, app = create_mazegridworld( args )
elif args.env == 'MazeReal':
    sim, app = create_mazerealworld( args )
    
app.run()
sys.exit()


# ******************************************************************************
# *************************************************************** main_simulator
# ******************************************************************************
def main_simulator( argv ):
    """
    Set arguments, build a proper Environment from Grid and filename
    Set observation if needed
    Run simulator
    """
    ## Argument to parse
    parser = argparse.ArgumentParser()
    parser.add_argument( 'filename',
                         default="fourcell_maze.txt",
                         nargs='?',
                         help="Filename de l'environnement" )
    parser.add_argument( '-o', '--obs',
                         action='store_true',
                         help="Observation de l'Etat" )
    parser.add_argument( '-m', '--mem',
                         action='store_true',
                         help="Ajoute une mémoire à l'Agent" )
    parser.add_argument( '--value_iteration',
                         action='store_true',
                         help="Ajoute l'Algorithme Value Iteration" )
    args = parser.parse_args( argv[1:] )
    print( "Reading Environment from", args.filename )
    
    import mazegridworld
    import agent_memory
    # -------------------------------------------------------------- Environment
    class Environment(mazegridworld.MazeGridWorld):
        def __init__(self):
            mazegridworld.MazeGridWorld.__init__(self, args.filename)

            if args.obs:
                print( "__Agent Perception de OBSERVATION ***************" )
                self.agent.perception_module.add_module( mazegridworld.ObservationGrid( self.agent ))
            else:
                print( "__Agent Perception de ETAT **********************" )
                self.agent.perception_module.add_module( mazegridworld.PerceptionGrid(self.agent))

            if args.mem:
                print( "__ADDING Memory to Agent ************************" )
                self.agent.perception_module.add_module( agent_memory.MemoryPerception( self.agent ))
                self.agent.action_module.add_module( agent_memory.MemoryAction( self.agent ))
            
            self.agent.perceive()

    # -----------------------------------------------------------  run Simulator
    sim = core.Simulator( Environment )
    app = tk_simu.TkSimu( sim, "MazeGrid World" )

    # Ajoute Value Iteration ??
    if args.value_iteration:
        import algo_valueiteration
        vi = algo_valueiteration.AlgoValueIteration(mzg.agent)
        sim.add_algo( vi, "VI Algo" )
        
    app.run()
# ******************************************************************************
# ******************************************************************************

def test_value_iteration():
    import mazegridworld
    # -------------------------------------------------------------- Environment
    class Environment(mazegridworld.MazeGridWorld):
        def __init__(self):
            mazegridworld.MazeGridWorld.__init__(self, "fourcell_maze.txt")

            print( "***** SETTING TO STATE PERCEPTION" )
            self.agent.perception_module.add_module( mazegridworld.PerceptionGrid(self.agent))
            self.agent.perceive()

    mzg = Environment()

    import algo_valueiteration
    vi = algo_valueiteration.AlgoValueIteration(mzg.agent)
    for i in range(10):
        vi.step( True )
        print( f"__VI={vi.state_value}" ) 

    # -----------------------------------------------------------  run Simulator
    sim = core.Simulator( Environment )
    app = tk_simu.TkSimu( sim, "VI + MazeGrid World" )
    sim.add_algo( vi, "VI Algo" )
    app.run()
            
# ***************************************************************** test_unicode
def test_unicode():
    tlbr = u'\u250F\u2513\n\u2517\u251B'
    _lbr = u'\u257B\u257B\n\u2517\u251B'
    t_br = u'\u257A\u2513\n\u257A\u251B'
    tl_r = u'\u250F\u2513\n\u2579\u2579'
    tlb_ = u'\u250F\u2578\n\u2517\u2578'
    __br = u' \u257B\n\u257A\u251B'
    _l_r = u'\u257B\u257B\n\u2579\u2579'
    _lb_ = u'\u257B \n\u2517\u2578'
    t__r = u'\u257A\u2513\n \u2579'
    t_b_ = u'\u257A\u2578\n\u257A\u2578'
    tl__ = u'\u250F\u2578\n\u2579 '
    t___ = u'\u257A\u2578\n  '
    _l__ = u'\u257B \n\u2579 '
    __b_ = u'  \n\u257A\u2578'
    ___r = u' \u257B\n \u2579'
    vide = u'  \n  '
    
    print( tlbr )
    print( _lbr )
    print( t_br )
    print( tl_r )
    print( tlb_ )
    print( __br )
    print( _l_r )
    print( _lb_ )
    print( t__r )
    print( t_b_ )
    print( tl__ )
    print( t___ )
    print( _l__ )
    print( __b_ )
    print( ___r )
    print( vide )
    
    

# ****************************************************************** test_simutk
def test_simutk():
    sim = core.Simulator( world.Environment ) 
    app = tk_simu.TkSimu( sim , "Aspirateur - monde discret" )

    app.run()

# ******************************************************************* test_steps
def test_steps():
    """
    Dans Environnement discret (world.py), teste les effets des actions
    de l'agent.
    TEXTUEL.
    p = perceive+decide+act, a=aspire, d=droite, g=gauche
    b = percieve+decide+eval(agent.action), q = quit
    """
    sim = core.Simulator( world.Environment )
    
    print( sim )
    while True:
        ans = input( "p or a/g/d/m or b or q --> ")
        if ans == 'q':
            break
        elif ans == 'p':
            sim.agent.perceive()
            sim.agent.decide()
            sim.agent.act()
        elif ans == 'd':
            sim.agent.move_right()
        elif ans == 'g':
            sim.agent.move_left()
        elif ans == 'a':
            sim.agent.aspire()
        elif ans == 'b':
            sim.agent.perceive()
            sim.agent.decide()
            act = sim.agent.action
            print( "+++ "+str(sim.agent.state)+"  "+str(act) )
            eval( "sim.agent."+act )
        sim.agent.perceive()
        print( sim )

# ******************************************************************* test_alpha
import world_alpha
import tkinter as tk
class AlphaTest:
    def __init__(self):
        self.env = world_alpha.Environment()
        
        self.main_window = tk.Tk()
        self.main_window.title( "Alpha" )

        ## Environment
        self.env_frame = tk.LabelFrame( self.main_window,
                                        text="Environment",
                                        bd=5, relief=tk.GROOVE )
        self.env_frame.grid( row=0, column=0,
                             rowspan=1, columnspan=1,
                             padx=5, pady=5 )
        
        self.env_canvas = tk.Canvas( self.env_frame, width=800, height=800 )
        self.env_canvas.pack()

        self.env.agent.perceive()
        self.env.draw( self.env_canvas)

    def perception(self):
        import math
        self.env.agent.perceive()
        print( "__PER" )
        print( self.env.agent.state )

        print( "__TEST PER" )
        tp = self.env.agent.perception_module
        dmov = [ (2, 2.3, math.pi/2.0), (1, 2.3, math.pi/4.0),
                 (3, 2.3, -math.pi/6.0), (1.7, 0.5, math.pi) ]
        for x,y,ang in dmov:
            msg = "  for {},{} : {}".format( x,y, ang/math.pi*180.0 )
            for o in tp.orient:
                res = tp.dist_sensor_value( x, y, ang+o )
                msg += " look {} = {}".format( o/math.pi*180.0, res )
            print( msg )
        
    def run(self):
        self.main_window.mainloop()

# ******************************************************************* test_alpha
def test_alpha():
    app = AlphaTest()
    app.perception()
    app.run()

# *************************************************************** test_sim_alpha
def test_sim_alpha():
    sim = core.Simulator( world_alpha.Environment )
    sim.agent.perceive()
    app = tk_simu.TkSimu( sim, "Créature Braitenberg - monde continu" )

    app.run()

# *************************************************************** test_gridworld
def test_gridworld():
    import gridworld
    class Environment(gridworld.GridWorld):
        def __init__(self):
            gridworld.GridWorld.__init__(self, 3, 3)

    
    sim = core.Simulator( Environment )
    sim.agent.perceive()
    app = tk_simu.TkSimu( sim, "GridWorld" )

    app.run()
# ************************************************************** test_grid_light
def test_grid_light():
    import env_discret_light

    sim = core.Simulator( env_discret_light.Environment )
    sim.agent.perceive()
    app = tk_simu.TkSimu( sim, "Grid + Light" )

    app.run()
# **************************************************************** test_mazegrid
def test_mazegrid():
    import mazegridworld
    class Environment(mazegridworld.MazeGridWorld):
        def __init__(self):
            mazegridworld.MazeGridWorld.__init__(self, "cheeze_maze.txt")

    sim = core.Simulator( Environment )
    #sim.agent.perceive()
    app = tk_simu.TkSimu( sim, "MazeGrid World" )

    app.run()

    
# ***************************************************************** test_options
def test_option( env_name ):
    ## Create sim
    sim = None
    txt_code = "core.Simulator( "+env_name+".Environment )"
    sim = eval( txt_code )
    sim.agent.perceive()

    ## GUI application from sim
    app = tk_simu.TkSimu( sim, sim.env.title )
    app.run()
# ************************************************************************* MAIN


if __name__ == '__main__':
    test_value_iteration()
    # main_simulator( sys.argv )
    #test_steps()
    #test_simutk()
    #test_alpha() 
    #test_sim_alpha()
    #test_gridworld()
    #test_grid_light()
    #test_mazegrid()
    #test_option( sys.argv[1] )
    #test_unicode()
