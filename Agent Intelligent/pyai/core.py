# -*- coding: utf-8 -*-

## Generic Agent and Simulator

# From Environment coordinate to Canvas coordinate
from .utils import _xscreen, _yscreen
import numpy as np

## Change object at runtime
import types

import tkinter as tk
from tkinter import filedialog
from .tk_console import TkConsole
from .tk_editor import TkEditor

# MEMOIRE
mem_avancer = 0
mem_turnG = 0
mem_turnD = 0

# ******************************************************************************
# ******************************************************************** Simulator
# ******************************************************************************
class Simulator:
    """
    Needs an Environment : reset(), agent,
                           get_canvas_size(), init_draw(), draw()
    Agent : perceive(), decide(), act()

    apply_code() to apply code from editor to Agent => agent.decision_module

    build_gui : create self.editor et self.console_frame
    - console_frame [TkConsole] : clear(), display()
    - editor  [TkEditor] : text.get( start, end ), set_text()
    """
    def __init__(self, env_class ):
        self.env = env_class()
        self.env.reset()
        self.agent = self.env.agent
        self.algo_l = []
        self.verb_int = None # defined once Tk is initialized
        self.should_stop = False
        
    def is_verb(self):
        if self.verb_int is None:
            return False
        return self.verb_int.get() == 1
        
    def __str__(self):
        return str(self.env) +" "+ str(self.agent)

    # ------------------------------------------------------------------ command
    def reset(self):
        log = "__RESET\n"
        self.env.reset()
        log += str( self.env )

        self.console_frame.clear()
        self.console_frame.display( log )
        
    def step(self):
        log = "__STEP\n"

        self.agent.perceive()
        if self.is_verb():
            log += str(self)+'\n'

        self.agent.decide()
        log += " P=" + self.agent.str_per()
        log += " A=" + self.agent.str_act()
        self.agent.act()
        self.agent.perceive()
        log += " ==> P=" + self.agent.str_per()

        self.console_frame.display( log )

    def run(self):
        log = "__RUNNING\n"

        self.should_stop = False
        # run_btn devient vert
        self.run_btn.configure( bg="green" )
        self.run_btn.update()
        # stop_btn peut être utilisé
        self.stop_btn["state"] = "normal"
        
        self._run_command()

        self.console_frame.display( log )

    def _run_command(self):
        if not self.should_stop:
            self.step()
            self.btn_frame.after( 500, self._run_command )

        
    def stop(self):
        log = "__STOP\n"
        
        self.should_stop = True
        # run_btn devient gris
        self.run_btn.configure( bg=self._default_bg_color)
        self.run_btn.update()
        # stop_btn ne peut pas être utilisé
        self.stop_btn["state"] = "disabled"
        
        self.console_frame.display( log )
        
    def apply_code(self):
        """
        Read code from editor and change agent.decision.
        """
        print( "__APPLY" )
        #print( "  globals="+ str(globals()) )
        log = "__APPLY CODE\n"

        txt_command = self.editor.text.get( 1.0, tk.END )
        txt_command += "\nself.agent.decision_module.apply = types.MethodType( apply, self.agent.decision_module )"
        ##cpl_command = compile( txt_command, '<string>', 'exec' )
        exec( txt_command )

    # ---------------------------------------------------------------------- gui
    def build_gui(self, main_window ):
        self.main_window = main_window
        self.verb_int = tk.IntVar()
        # background color for GUI
        self._default_bg_color = main_window.cget("background")

        ## Environment
        env_w, env_h = self.env.get_canvas_size()
        self.env_frame = tk.LabelFrame( main_window,
                                        text="Environment",
                                        bd=5, relief=tk.GROOVE,
        )
        self.env_frame.grid( row=1, column=0,
                             rowspan=2, columnspan=1,
                             padx=5, pady=5,
                             sticky=(tk.N,tk.E,tk.W,tk.S),
        )
        self.env_frame.rowconfigure( 0, weight=1 )
        self.env_canvas = tk.Canvas( self.env_frame, width=env_w, height=env_h )
        self.env_canvas.pack()

        # Console
        self.console_frame = TkConsole( main_window, row=3, col=0 )

        self.console_frame.set_height( 10 )
        # Buttons
        self.btn_frame = tk.LabelFrame( main_window,
                                        text="Simulateur",
                                        bd=5, relief=tk.GROOVE)
        self.btn_frame.grid( row=0, column=0,
                             rowspan=1, columnspan=1,
                             padx=5, pady=5,
                             sticky=(tk.W, tk.E))
        # -- step --
        step_btn = tk.Button( self.btn_frame, text='Step',
                              command = self.step )
        step_btn.grid( row=0, column=0, padx=5, pady=5 )

        # -- run --
        self.run_btn = tk.Button( self.btn_frame, text='Run',
                              command = self.run )
        self.run_btn.grid( row=0, column=1, padx=5, pady=5 )
        # -- stop --
        self.stop_btn = tk.Button( self.btn_frame, text='Stop',
                              command = self.stop )
        self.stop_btn.grid( row=0, column=2, padx=5, pady=5 )
        self.stop_btn["state"] = "disabled"

        # -- reset --
        reset_btn = tk.Button( self.btn_frame, text='Reset',
                               command = self.reset )
        reset_btn.grid( row=0, column=3, padx=5, pady=5 )
        
        # -- verb --
        verb_btn = tk.Checkbutton( self.btn_frame,
                                   variable = self.verb_int,
                                   text="verbeux",
                                   anchor='w' )
        verb_btn.deselect() # select(), toggle()
        verb_btn.grid( row=0, column=4, padx=5, pady=5,
                         columnspan=2)
        # -- quit --
        quit_btn = tk.Button( self.btn_frame, text='Quit',
                              command = self.main_window.destroy )
        quit_btn.grid( row=0, column=6, padx=(60,5), pady=5 )

        ## Buttons Editor
        self.edbtn_frame = tk.LabelFrame( main_window,
                                          text="Editeur",
                                          bd=5, relief=tk.GROOVE)
        self.edbtn_frame.grid( row=0, column=2, padx=5, pady=5 )
        ##self.edbtn_frame.columnconfigure( 0, weight=1)
        # -- apply --
        apply_btn = tk.Button( self.edbtn_frame, text='Apply Changes',
                               command = self.apply_code )
        apply_btn.grid( row=0, column=0, padx=5, pady=5 )
        save_edbtn = tk.Button( self.edbtn_frame, text="Save",
                                command=self.save_editor )
        save_edbtn.grid( row=0, column=2, padx=5, pady=5 )
        load_edbtn = tk.Button( self.edbtn_frame, text="Load",
                                command=self.load_editor )
        load_edbtn.grid( row=0, column=1, padx=5, pady=5 )
        

        
        ## Notebook for Editor and Help
        self.edit_nn = tk.ttk.Notebook( main_window )
        self.edit_nn.grid( row=1, column=1,
                           sticky=(tk.N,tk.E,tk.W,tk.S),
                           rowspan=3, columnspan=2,
                           padx=5, pady=5 )
        self.edit_nn.rowconfigure( 1, weight=1 )
        self.edit_nn.columnconfigure( 1, weight=1 )

        ## Code Editor
        
        self.edit_frame = tk.LabelFrame( self.edit_nn,
                                         text="Decision editor",
                                         bd=5, relief=tk.GROOVE )
        self.edit_frame.pack( expand="yes", fill="both" )
        # self.edit_frame.grid( row=0, column=1,
        #                       rowspan=3, columnspan=1,
        #                       padx=5, pady=5 )
        # self.env_frame.rowconfigure( 0, weight=1 )

        self.editor = TkEditor( self.edit_frame )
        self.editor.set_text( self.agent.decision_module.get_init_text() )
        self.edit_nn.add( self.edit_frame, text='Editor' )
        ## Help Frames
        self.hperc_frame, self.hperc_text = self.make_text(
            self.edit_nn,
            "Perception",
            self.agent.perception_module.describe() )
        self.edit_nn.add( self.hperc_frame, text='Perception' )
        
        self.haction_frame, self.haction_text = self.make_text(
            self.edit_nn,
            "Action",
            self.agent.action_module.describe() )
        self.edit_nn.add( self.haction_frame, text='Action' )

        self.hdecide_frame, self.hdecide_text = self.make_text(
            self.edit_nn,
            "Decision",
            self.agent.decision_module.describe() )
        self.edit_nn.add( self.hdecide_frame, text='Decision' )

        self.env_frame.after( 10, self.refresh )

    # --------------------------------------------------------------------- draw
    def init_draw(self):
        self.env.init_draw( self.env_canvas )
    def draw(self):
        ##self.console_frame.display( "Drawing" )
        self.env.draw( self.env_canvas )

        # Draw modules
        for algo in self.algo_l:
            algo.draw( self.env_canvas )
    def refresh(self):
        self.draw()
        self.main_window.update()
        self.env_frame.after( 10, self.refresh )


    # ---------------------------------------------------------------- make_text
    def make_text(self, parent, title, txt ):
        text_frame = tk.LabelFrame( parent,
                                    text=title,
                                    bd=5, relief=tk.GROOVE )
        text = tk.Text( text_frame )
        scroll = tk.Scrollbar( text_frame, orient=tk.VERTICAL,
                               command=text.yview )
        scroll.pack( side=tk.RIGHT, fill=tk.Y )
        # text['yscrollcommand']=scroll.set
        print( title+" = " +txt )
        text.config( state=tk.NORMAL )
        text.insert( tk.END, txt )
        text.config( state=tk.DISABLED )
        text.pack( side=tk.LEFT, fill=tk.BOTH, expand= tk.YES )
        text_frame.pack( side=tk.LEFT, fill=tk.BOTH, expand= tk.YES )
        return text_frame, text

    # ----------------------------------------------------------------- add_algo
    def add_algo(self, algo_module, title="algo"):
        """
        Adds a new Algo and its GUI in a "Panel" 
        
        draw : call algo_module.draw( canvas )
        """
        self.algo_l.append( algo_module )

        ## A frame with
        # - module.describe in a text_frame
        # - the module_frame created by the module.build_gui(parent)
        module_frame = tk.LabelFrame( self.edit_nn,
                                      text=title,
                                      bd=5, relief=tk.GROOVE )
        
        text_frame, describe_text = self.make_text( module_frame,
                                                   "Description",
                                                   algo_module.describe() )
        text_frame.pack(side=tk.TOP, fill=tk.X)

        algo_frame = algo_module.build_gui( module_frame, self.console_frame )
        algo_frame.pack(side=tk.TOP, fill=tk.BOTH)
        
        self.edit_nn.add( module_frame, text=title )
        

    # --------------------------------------------------------- load/save_editor
    def save_editor(self):
        filename = filedialog.asksaveasfilename(
            initialdir=".",
            title="Sauvegarder dans...",
            filetypes = [('fichier decision', '*.dec')]
        )
        # Check for cancelation
        if len(filename) > 0:
            print( f"Save as {filename}" )
            fileobj = open( filename, "w" )
            fileobj.write( self.editor.text.get( 1.0, tk.END ) )
            fileobj.close()

    def load_editor(self):
        filename = filedialog.askopenfilename(
            initialdir=".",
            title="Charger depuis...",
            filetypes = [('fichier decision', '*.dec')]
        )
        # Check for cancelation
        if len(filename) > 0:
            print( f"Loading {filename}" )
            fileobj = open( filename, "r" )
            editor_code = fileobj.read()
            fileobj.close()
            self.editor.set_text( editor_code )


# ******************************************************************************
# *************************************************************** PerceptionCore
# ******************************************************************************
class Module(object):
    def __init__(self, agent, init_msg=""):
        self.agent = agent
        self.world = agent.env
        self.init_msg = init_msg
        self.module_l = []
        
    def describe(self):
        print( "MOD DESCRIBE - Module ", self.init_msg)
        msg = self.init_msg
        for mod in self.module_l:
            msg += mod.describe()
        print( "  final msg", msg )
        return msg

    def apply(self):
        print( "MOD APPLY - Module")
        result = []
        for mod in self.module_l:
            result.extend( mod.apply() )
        print( "  result", result )
        return result

    def add_module(self, mod):
        self.module_l.append( mod )

class PerceptionModule(Module):
    def __init__(self, agent):
        Module.__init__(self, agent,
                        "Une Perception est composée de\n")
        #self.agent.perc = self.apply
        
    def describe(self):
        msg = Module.describe(self)
        msg += '\n\nExemple '+self.str_display(self.apply())
        return msg

    def apply(self):
        print( "MOD APPLY - Module")
        result = []
        for mod in self.module_l:
            result.extend( mod.apply() )
        print( "  result", result )
        return result

    def str_display(self, perception):
        msg = str(perception)
        return msg

class ActionModule(Module):
    def __init__(self, agent):
        Module.__init__(self, agent,
                        "Actions possibles : \n" )                        
    
class DecisionModule(Module):
    def __init__(self, agent):
        Module.__init__(self, agent,
                        """La méthode 'apply(...)' de DECISION doit renvoyer une LISTE de CHAÎNE DE CARACTÈRE (str) qui décrit l'action à utiliser.\n\n"""
        )

    def apply(self, agent_state):
        print( "DecisionModule.apply(self, agent_state)" )
        return ["__str__()"]
        
# ************************************************************************ Agent
# ******************************************************************************
class Agent:
    """
    perceive()
    decide()
    act()
    draw()
    
    Must be given Perception, Action and Policy
    - perception_module : str_state( Agent.state )
    - decision_module : apply( Agent.state )
    - action : must be evaluated through eval( "self."+self.action )
    """
    # --------------------------------------------------------------------- init
    
    def __init__(self, env):
        """
        """
        self.env = env
        ## Internal State
        self.state = None
        self.action = [] #liste des actions à faire
        ## Modules
        self.perception_module = PerceptionModule( self )
        self.action_module = ActionModule( self )
        self.decision_module = DecisionModule( self )
        ## MEMOIRE
        self.mem_avancer = 0
        self.mem_turnR = 0
        self.mem_turnL = 0

    def __str__(self):
        # if self.perception_module:
        #     str_s = self.perception_module.str_display( self.state )
        # else:
        #str_s = str(self.state)
        return "S={} A={}".format( self.state, self.action )

    def str_per(self):
        return self.perception_module.str_display( self.state )
    def str_act(self):
        return str(self.action)
    
    # --------------------------------------------------------------------  Core
    def perceive(self):
        if self.perception_module is not None:
            self.state = self.perception_module.apply()
    def decide(self):
        if self.decision_module is not None:
            self.action = self.decision_module.apply( self.state )
            
    def act(self):
        if self.action is not None and len(self.action) > 0:
            for act in self.action:
                ## to call an action, it must be evaluated
                eval( "self."+act )

    # --------------------------------------------------------------------- draw
    def draw(self, canvas, x, y):
        """
        A blue circle of width 3

        Params:
        - canvas : tk.Canvas
        - x, y : where to draw
        """
        size = 0.2
        canvas.create_oval( _xscreen( x-size ), _yscreen( y-size ),
                            _xscreen( x+size ), _yscreen( y+size ),
                            outline='blue', width=3 )

