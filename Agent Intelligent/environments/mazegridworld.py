# -*- coding: utf-8 -*-

"""
A generic MazeGridWorld

Lit un fichier avec
size: row x col
Puis, une ligne par 'row' avec soit un numéro de cell, soit X pour obstacle

Eventuellement, une liste d'élements dans le monde, avec sa position (0x0 est
en haut à gauche)
light: 2 x 2
"""

from pyai.utils import intersect, _xscreen, _yscreen, _xenv, _yenv

import tkinter as tk
from pyai.tk_console import TkConsole

import random

from pyai.core import Agent, Module, DecisionModule

# ******************************************************************************
# ********************************************************************** Movable
# ******************************************************************************
class Movable:
    """ Stores info about moveable object
    """
    def __init__(self, py_object, posx=0, posy=0):
        self.py_object = py_object
        self.posx = posx
        self.posy = posy
    def __str__(self):
        msg = str(self.py_object)+f" ({self.posx}, {self.posy})"
        return msg

# ******************************************************************************
# ******************************************************************** GridWorld
# ******************************************************************************
class MazeGridWorld(object):
    """
    With inner classes : Perception, Action

    Discrete Environment
        - get_position( Moveable )
        - possible_move( Agent, dx, dy, da ) => allowed
        - init_draw() : 
        - draw() : walls as line, cells as rectangles, agent.draw()
    
    With a right click, will move 'light' element if it exists
    using canvas.bind<'', cbk) in init_draw

    agent [core.Agent] : crée et dote de capacités
        - perception_module = PerceptionGrid
        - action_module = ActionGrid
        - decision_module = DecisionGrid
    - wall_l [ (x,y, xx,yy) ]
    - cell_matrix[idrow][idcol]= str(id) OR 'X'
    - movable_l = [Movable] dont Movable(self.agent)
    """

    def __init__(self, filename):
        """
        Read filename to determine size, wall positions, cells pos and numbers,
        etc
        """
        self.cell_matrix = []
        self.wall_l = []
        self.movable_l = []
        
        self.read_file(filename)
        print( "self.cell_matrix", self.cell_matrix )
        print( "self.wall_l", self.wall_l )
        print( "self.movable_l", self.movable_l )
        
        self.dimx = self.nbcol
        self.dimy = self.nbrow
        
        # ## List of movable 'Object' (Agent are movable :o) )
        self.agent = Agent( self )
        self.movable_agent = Movable( self.agent, 0, 0 )
        self.movable_l.append( self.movable_agent )
        #self.agent.perception_module.add_module( PerceptionGrid(self.agent))
        #self.agent.perception_module = PerceptionGrid( self.agent, self )
        #self.agent.perception_module = ObservationGrid( self.agent, self )
        self.agent.action_module.add_module(ActionGrid( self.agent ))
        self.agent.decision_module = DecisionGrid( self.agent )

        self.reset()

        self.agent.perceive()

    def __str__(self):
        ## Agent position
        msg = " Agent=({}, {})".format( self.movable_agent.posx,
                                        self.movable_agent.posy )
        return msg

    def read_file(self, filename):
        with open(filename) as fd:
            file_content = fd.readlines()

            # an index on the line count
            idl = 0
            # pass comment or empty lines and check for 'title: <string>'
            idl = self._step_empty_lines(0, file_content)
            if idl < len(file_content):
                line = file_content[idl]
                # look for 'title: <string>'
                idtitle = line.find( 'title:')
                if idtitle< 0:
                    msg = f"'title:' not found in line ({idl}):{line}"
                    raise RuntimeError( msg )
                self.title = line[idtitle+1:]

            # pass comment or empty lines and check for 'size: # x #'
            idl = self._step_empty_lines(idl+1, file_content)
            if idl < len(file_content):
                line = file_content[idl]
                # look for 'size: row x col'
                idrow = line.find( 'size:')
                if idrow < 0:
                    msg = f"'size:' not found in line ({idl}):{line}"
                    raise RuntimeError( msg )
                idx = line.find( 'x' )
                if idx < 0:
                    msg = f"'row x col' not found in line ({idl}):{line}"
                    raise RuntimeError( msg )
                # print( f"Reading row from {line[idrow+5:idx]}" )
                # print( f"Reading col from {line[idx+1:]}" )
                self.nbrow = int( line[idrow+5:idx] )
                self.nbcol = int( line[idx+1:] )
                print( f"__READ size= {self.nbrow} x {self.nbcol}" )

            # pass comment and check for cells names and positions
            #idl += 1
            idl = self._step_empty_lines(idl+1, file_content)
            if idl < len(file_content):
                for idr in range(self.nbrow):
                    line = file_content[idl]
                    cells_nb = line.split()
                    if len(cells_nb) != self.nbcol :
                        msg = f"Needs {self.nbcol} token in line ({idl}):{line}"
                        raise RuntimeError( msg )
                    self.cell_matrix.append( cells_nb )
                    idl += 1
            print( "__READ cells", self.cell_matrix )
            self._make_cells_and_walls( self.cell_matrix )

            # pass comment and read various elements
            idl = self._step_empty_lines(idl+1, file_content)
            while idl < len(file_content):
                line = file_content[idl]
                iddp = line.find( ':' )
                if iddp < 0:
                    msg = f"':' not found in line ({idl}):{line}"
                    raise RuntimeError( msg )
                cell_id = int( line[iddp+1:] )
                # find position of the cell with cell_id
                idc, idr = self._get_cell_indexes( cell_id )
                self.movable_l.append( Movable( line[:iddp], idc+0.5, idr+0.5 ))
                idl = self._step_empty_lines(idl+1, file_content)

    def _step_empty_lines(self, index, content, verb=True):
        """Return index of firt interesting line or index to len(content)
        """
        for idl in range(index, len(content)):
            line = content[idl]
            if verb:
                print( f"Checking ({idl}):{line} len={len(line)}" )
            if len(line) > 1 and not line.startswith( '#' ):
                return idl
        return len(content)

    def _make_cells_and_walls(self, cells):
        """cells is a list of list of {cell_nb or X}
        
        Build the
        - self.cell_matrix
        - self.wall_l = (x,y, xx,yy) for walls
        """
        # cells positions
        self.wall_l = []
        for idr in range(self.nbrow):
            for idc in range(self.nbcol):
                if cells[idr][idc] != 'X':
                    if idr == 0:
                        # wall above
                        self.wall_l.append( (idc,idr, idc+1,idr) )
                    if idc == 0:
                        # wall left
                        self.wall_l.append( (idc,idr, idc,idr+1) )
                    if idr == (self.nbrow-1):
                        # wall below
                        self.wall_l.append( (idc,idr+1, idc+1,idr+1) )
                    if idc == (self.nbcol-1):
                        # wall right
                        self.wall_l.append( (idc+1,idr, idc+1,idr+1) )
                        
                elif cells[idr][idc] == 'X':
                    # wall above ?
                    if idr > 0 and cells[idr-1][idc] != 'X':
                        self.wall_l.append( (idc,idr, idc+1,idr) )
                    # wall left ?
                    if idc > 0 and cells[idr][idc-1] != 'X':
                        self.wall_l.append( (idc,idr, idc,idr+1) )
                    # wall below ?
                    if idr < (self.nbrow-1) and cells[idr+1][idc] != 'X':
                        self.wall_l.append( (idc,idr+1, idc+1,idr+1) )
                    # wall right ?
                    if idc < (self.nbcol-1) and cells[idr][idc+1] != 'X':
                        self.wall_l.append( (idc+1,idr, idc+1,idr+1) )

    def _get_cell_indexes(self, cell_id ):
        """Look in self.cell_matrix
        """
        for idr in range( self.nbrow ):
            for idc in range( self.nbcol ):
                if self.cell_matrix[idr][idc] == str(cell_id):
                    return (idc, idr)
        return None
    
    def reset(self):
        """
        Reset the agent position to a random cell
        """
        # need to be a valid cell !
        idr = random.randrange( self.nbrow )
        idc = random.randrange( self.nbcol )
        while self.cell_matrix[idr][idc] == 'X':
            idr = random.randrange( self.nbrow )
            idc = random.randrange( self.nbcol )
        self.movable_agent.posx = 0.5+1.0*idc
        self.movable_agent.posy = 0.5+1.0*idr

    def get_movable( self, elem ):
        for mov in self.movable_l:
            if mov.py_object == elem:
                return mov
        return None
    def get_position( self, mov ):
        return mov.posx,mov.posy

    def get_rowcol( self, mov ):
        scrx, scry = self.get_position( mov )
        return round(scry-0.5), round(scrx-0.5)
    
    def possible_move( self, srcx, srcy, deltax, deltay ):
        """
        Is Move from (srcx, srcy) of (desx, desy) possible: ie, no collision with wall
        Return allwed, destx, desty
        """
        ## Check valid agent
        #srcx,srcy = self.get_position( agent )
        desx = srcx + deltax
        desy = srcy + deltay
        
        allowed = True
        for wall in self.wall_l:
            allowed = allowed and not intersect( srcx, srcy, desx, desy,
                                                 *wall )
        # if allowed:
        #     self.movable_agent.posx = desx
        #     self.movable_agent.posy = desy
        return allowed, desx, desy

    def move(self, elem, deltax, deltay):
        ## Check valid element
        mov = self.get_movable( elem )
        if mov:
            srcx,srcy = self.get_position( mov )
            possible, newx, newy = self.possible_move( srcx, srcy, deltax, deltay )
            if possible:
                mov.posx = newx
                mov.posy = newy
            
    
    def get_canvas_size(self):
        return _xscreen( self.dimx ), _yscreen( self.dimy )

    def index_from_pos(self, posx, posy):
        """
        find cell index give position by looking at self.cell_matrix
        """
        idx = round( posx - 0.5 )
        idy = round( posy - 0.5 )
        if self.cell_matrix[idy][idx] != 'X':
            return int(self.cell_matrix[idy][idx])
        return None
    def pos_from_cellid(self, cell_id):
        for idr in range( self.nbrow ):
            for idc in range( self.nbcol ):
                if self.cell_matrix[idr][idc] == str(cell_id):
                    return idc+0.5, idr+0.5
    
    def init_draw(self, canvas):
        canvas.bind('<Button-3>', self.on_rclick_event)
        canvas.bind('<Button-2>', self.on_mclick_event)
        canvas.bind('<Alt-s>', self.on_mclick_event)
        
    def on_rclick_event(self, event):
        """
        Change the position of the 'light' element if it exists and a
        valid cell is clicked.
        """
        id_click = self.index_from_pos( _xenv(event.x), _yenv(event.y) )
        col_click, row_click = self._get_cell_indexes( id_click )
        print( f"Click at {event.x}x{event.y} => id={id_click} for {row_click},{col_click}" )
        ## valid cell ?
        if not self.cell_matrix[row_click][col_click] == 'X':
            ## move light if valid movable element
            mov = self.get_movable( 'light' )
            if mov is not None:
                mov.posx, mov.posy = self.pos_from_cellid( id_click )

    def on_mclick_event(self, event):
        print( "Elem", self.element_l )
        for mov in self.movable_l:
            if mov.py_object == self.agent:
                print( "A  ", mov )
            else:
                print( "M  ", mov )
    
    def draw(self, canvas ):
        canvas.delete( tk.ALL )
        for wall in self.wall_l:
            canvas.create_line( _xscreen(wall[0]), _yscreen(wall[1]),
                                _xscreen(wall[2]), _yscreen(wall[3]),
                                width=3 )
        ## Cells
        for y in range( self.nbrow ):
            for x in range( self.nbcol ):
                id = self.cell_matrix[y][x]
                if id != 'X':
                    canvas.create_rectangle( _xscreen( x ), _yscreen( y ),
                                             _xscreen( x+1 ), _yscreen( y+1 ),
                                             fill = "", width = 2,
                                             dash=(10, 40) )
                    canvas.create_text( _xscreen( x+0.5 ), _yscreen( y+0.1 ),
                                        fill="black",
                                        text="cell_"+self.cell_matrix[y][x] )
        ## Agent
        self.agent.draw( canvas,
                         self.movable_agent.posx,
                         self.movable_agent.posy )

        ## Elements
        # for elem, posx, posy in self.element_l:
        #     self._draw_element( canvas, elem, posx, posy )
        for mov in self.movable_l:
            if mov.py_object != self.agent:
                self._draw_element( canvas, mov.py_object, mov.posx, mov.posy )

    def _draw_element(self, canvas, elem, posx, posy ):
        if elem in ['light', 'Light', 'LIGHT']:
            self._polygon_star( canvas, posx, posy )

    def _polygon_star(self, canvas, posx, posy, length=0.3, width=0.08  ):
        ## list of points to draw
        pts = []
        for i in (1,-1):
            pts.extend( (_xscreen( posx),            _yscreen( posy + i*length) ))
            pts.extend( (_xscreen( posx + i*width),  _yscreen( posy + i*width)  ))
            pts.extend( (_xscreen( posx + i*length), _yscreen( posy)            ))
            pts.extend( (_xscreen( posx + i*width),  _yscreen( posy - i*width)  ))
        canvas.create_polygon( pts, outline="green", fill="green", width=1 )



    
            
        
# ******************************************************************************
# *************************************************************** PerceptionGrid
# ******************************************************************************
class PerceptionGrid(Module):
    """
    Définit des senseurs cell, elements

    describe() => str
    apply() => [self.dist, self.light]
    """
    def __init__(self, agent):
        self.agent = agent
        self.world = agent.env

    def describe(self):
        print( "MOD DESCRIBE - PerceptionGrid")
        msg = '- position de l\'agent : nom de la cellule (ex "cell_0", "cell_1", etc)\n'
        msg += '- "elem_ID" ou ID est l\identifiant de la cellule qui contient "elem"\n'
        return msg

    def apply(self):
        """
        Return: [ "cell_ID" ] où ID est la cell où se trouve l'agent,
        puis, pour chaque élément 'elem' du monde, "elem_ID" où ID est l'identifiant de la cell qui contient l'élément.
        """
        print( "MOD APPLY - PerceptionGrid")
        perc = []
        # position agent
        srcx,srcy = self.world.get_position( self.world.get_movable( self.agent ))
        perc.append( "cell_"+str( self.world.index_from_pos(srcx, srcy )) )
        # position other elements
        # for elem, ex, ey in self.world.element_l:
        #     perc.append( elem+"_"+str( self.world.index_from_pos(ex, ey )) )
        for mov in self.world.movable_l:
            if mov.py_object != self.world.agent:
                perc.append( str(mov.py_object)+"_"+str( self.world.index_from_pos(mov.posx, mov.posy)) )

        print( "  perc=", perc )
        return perc


# ******************************************************************************
# *************************************************************** PerceptionGrid
# ******************************************************************************
class ObservationGrid(Module):
    """
    Définit des senseurs
    - l'agent voit les murs qui l'entourent

    describe() => str
    apply() => [self.dist, self.light]
    """
    def __init__(self, agent):
        self.agent = agent
        self.world = agent.env

    def describe(self):
        msg = '- murs autours de l\'agent (ex "_lb_" signifie un mur a gauche (l) et en bas (b)\n'
        msg += '- "elem" si la cellule de l`agent "elem"\n'
        return msg

    def apply(self):
        """
        Return: [ "_tb_" ] où ID est la cell où se trouve l'agent,
        puis, pour chaque élément 'elem' du monde, "elem" si "elem" est present dans la cellule de l\'agent
        """
        perc = []
        # position agent
        idr, idc = self.world.get_rowcol( self.world.get_movable( self.agent ))
        print( f"__OBS agent in {idr} x {idc}" )
        # check wall around
        obs = ""
        if idr == 0 or self.world.cell_matrix[idr-1][idc] == 'X':
            obs += "t"
        else:
            obs += "_"
        if idc == 0 or self.world.cell_matrix[idr][idc-1] == 'X':
            obs += "l"
        else:
            obs += "_"
        if idr == (self.world.nbrow-1) or self.world.cell_matrix[idr+1][idc] == 'X':
            obs += "b"
        else:
            obs += "_"
        if idc == (self.world.nbcol-1) or self.world.cell_matrix[idr][idc+1] == 'X':
            obs += "r"
        else:
            obs += "_"
        perc.append( obs )

        # position other elements
        agx, agy = self.world.get_position( self.world.get_movable( self.agent ))
        id_cellagent = self.world.index_from_pos( agx, agy )
        for elem, ex, ey in self.world.element_l:
            if id_cellagent == self.world.index_from_pos(ex, ey ):
                perc.append( elem )
        return perc
    
# ******************************************************************************
# ******************************************************************* ActionGrid
# ******************************************************************************
class ActionGrid(Module):
    """
    Définit des actions :
    - move_left => Environment.possible_move( agent, dx, dy, da)
    - move_right => "
    - move_random => "
    - do_nothing =>

    describe() => str
    """
    def __init__(self, agent):
        self.agent = agent
        self.world = agent.env
        ## add new method to agent
        setattr( agent, 'move_left', self.move_left )
        setattr( agent, 'move_right', self.move_right )
        setattr( agent, 'move_up', self.move_up )
        setattr( agent, 'move_down', self.move_down )
        setattr( agent, 'move_random', self.move_random )
        setattr( agent, 'do_nothing', self.do_nothing )

    def describe(self):
        msg = """- "move_right()" : bouge d'une case vers la droite\n"""
        msg += """- "move_left()" : bouge d'une case vers la gauche\n"""
        msg += """- "move_up()" : bouge d'une case vers le haut\n"""
        msg += """- "move_down()" : bouge d'une case vers le bas\n"""
        msg += """- "move_random()" : bouge aléatoirement\n"""
        msg += """- "do_nothing()" : ne fait rien\n"""
        return msg

    def move_left(self):
        """ x : -1.0 si move possible
        """
        #return self.world.possible_move( self.agent, -1.0, 0 )
        return self.world.move( self.agent, -1.0, 0 )
    def move_right(self):
        """ x : +1.0 si move possible
        """
        return self.world.move( self.agent, 1.0, 0.0 )
    def move_up(self):
        """ y : -1.0 si move possible
        """
        return self.world.move( self.agent, 0.0, -1.0 )
    def move_down(self):
        """ y : 1.0 si move possible
        """
        return self.world.move( self.agent, 0.0, 1.0 )        
    def move_random(self):
        """ any move """
        act = random.choice( [self.move_right, self.move_left,
                              self.move_up, self.move_down] )
        return act()
    def do_nothing(self):
        """ do nothing """
        pass
            
# ******************************************************************************
# ***************************************************************** DecisionGrid
# ******************************************************************************
class DecisionGrid(DecisionModule):
    """
    Définit une manière de choisir des Actions.
    - policy [ (["perc1", "perc2", etc], "action"),
               ([], "action") ] ## clause toujours vérifiée

    describe() => str
    apply( state ) =>  str décrivant une action "action()"

    is_valid( conditions, state ) => bool if all conditions in state
    """
    # def __init__(self, agent ):
    #     DecisionGrid
    #     self.agent = agent
    #     self.world = agent.env
        

    def describe(self):
        msg = Module.describe(self)
        msg += 'Par exemple, se terminer par:\n'
        act = self.apply( self.agent.state )
        msg += """    return """+str(act)
        return msg

    def apply(self, state):
        """
        Return:
        "self.action()" that can be evaluated
        """
        ## Règles : [conditions1, condition2], ["action1", "action2", ...]
        self.policy = [ (["cell_0"], ["move_right()"]),
                        ([], ["move_random()"])]
        
        ## find proper rule
        ## (note, la condition vide [] est toujours valide)
        for cond,act in self.policy:
            if self.is_valid( cond, state, verb=True ):
                self.act = act
                return self.act

    def get_init_text(self):
        return """def apply(self, state):
        ## Règles : [conditions1, condition2], ["action1", "action2", ...]
        self.policy = [ (["cell_0"], ["move_right()"]),
                        ([], ["move_random()"]) ]

        ## Cherche la première règle valide à appliquer
        ## (note, la condition vide [] est toujours valide)
        for cond,act in self.policy:
            if self.is_valid( cond, state):
                self.act = act
                return self.act"""

    def is_valid(self, cond, state, verb=False ):
        nb_ok = 0
        if verb:
            print( f"__IS_VALID: {cond} is_valid dans l\'état {state} ?" )
        if len(cond) == 0:
            if verb:
                print( "  VRAI car condition est vide []")
            return True
        for clause in cond:
            if clause == "*":
                print( f"  vu clause *, donc il suffit de ne pas avoir de clause absente dans l\'état" )
                nb_ok = len(state)
            elif not clause in state:
                print( f"  FAUX car {clause} n'est dans {state}" ) 
                return False
            else:
                if nb_ok != len(state):
                    nb_ok += 1
        if nb_ok == len(state):
            if verb:
                print( "  VRAI car toutes les clauses présentes et le bon nombre de clauses présentes (ou clause *)" )
            return True

        if verb:
            print( f"  FAUX car il manque de éléments de l'état ne sont pas mentionnés dans {cond}" )
        return False
    
    
if __name__ == '__main__':
    env = MazeGridWorld( "cheeze_maze.txt" )
    
