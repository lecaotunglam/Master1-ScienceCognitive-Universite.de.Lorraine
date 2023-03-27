# -*- coding: utf-8 -*-

"""
A generic MazedWorld using *CONTINUOUS* space, action and sensors.

Lit un fichier avec
size: row x col
Puis, une ligne par 'row' avec soit un numéro de cell, soit X pour obstacle

Eventuellement, une liste d'élements dans le monde, avec sa position (0x0 est
en haut à gauche)
light: 2 x 2
"""

import math
import numpy as np
import random
import tkinter as tk

from pyai.core import Agent, Module, DecisionModule
from pyai.tk_console import TkConsole
from pyai.utils import (intersect, intersect_dir_segment,
                        _xscreen, _yscreen )


# ******************************************************************************
# ********************************************************************** Movable
# ******************************************************************************
class Movable:
    """ Stores info about moveable object
    """
    def __init__(self, py_object, posx=0, posy=0, orient=0):
        self.py_object = py_object
        self.posx = posx
        self.posy = posy
        self.orient = orient
    def __str__(self):
        ang_deg = self.orient / math.pi * 180.0
        msg = str(self.py_object)+f" ({self.posx}, {self.posy}, {ang_deg})"
        return msg

# ******************************************************************************
# **************************************************************** MazeRealWorld
# ******************************************************************************
class MazeRealWorld(object):
    """
    Continuous Environment
        - get_position( Moveable )
        - possible_move( Agent, dx, dy, da ) => allowed
        - init_draw() : 
        - draw() : walls as line, cells as rectangles, agent.draw()
        - 

    agent [core.Agent] : crée et dote de capacités
        - perception_module = PerceptionReal
        - action_module = ActionReal
        - decision_module = DecisionReal
    - wall_l [ (x,y, xx,yy) ]
    - cell_matrix[idrow][idcol]= str(id) OR 'X'
    - element_m [ ['elem', posx, posy ] ]
    - movable_l = [Movable] dont Movable(self.agent)
    """

    def __init__(self, filename):
        """
        Read filename to determine size, wall positions, cells pos and numbers,
        elements, etc
        """
        self.cell_matrix = []
        self.wall_l = []
        self.element_l = []
        self.movable_l = []
        
        self.read_file(filename)
        print( "self.cell_matrix", self.cell_matrix )
        print( "self.wall_l", self.wall_l )
        print( "self.elements_l", self.element_l )
        print( "self.movable_l", self.movable_l )
        
        self.dimx = self.nbcol
        self.dimy = self.nbrow
        
        ## List of movable 'Object' (Agent are movable :o) )
        self.agent = Agent( self )
        self.tkagent = TkAgent( self.agent )
        self.movable_agent = Movable( self.agent, 0, 0 )
        self.movable_l.append( self.movable_agent )

        ## Actions and Decision using appropriate Modules
        self.agent.perception_module.add_module( PerceptionReal( self.agent ))
        self.agent.action_module.add_module( ActionReal( self.agent ))
        self.agent.decision_module = DecisionReal( self.agent )

        self.reset()

        self.agent.perceive()

    def __str__(self):
        msg = "W="
        ## Agent position
        msg += " Agent=({:5.2f}, {:5.2f} to {:3.0f})".format( self.movable_agent.posx, self.movable_agent.posy, self.movable_agent.orient/math.pi*180.0 )

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
            self.element_l = []
            #idl += 1
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
                self.element_l.append( [line[:iddp], idc+0.5, idr+0.5] )
                self.movable_l.append( Movable( [line[:iddp], idc+0.5, idr+0.5],
                                                idc+0.5, idr+0.5 ))
                #idl += 1
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
        # need to be a valid cell !
        idr = random.randrange( self.nbrow )
        idc = random.randrange( self.nbcol )
        while self.cell_matrix[idr][idc] == 'X':
            idr = random.randrange( self.nbrow )
            idc = random.randrange( self.nbcol )
        self.movable_agent.posx = 0.5+1.0*idc
        self.movable_agent.posy = 0.5+1.0*idr
        self.movable_agent.orient = random.random() * math.pi * 2.0

    def get_elem( self, name ):
        for e in self.element_l:
            if e[0] == name:
                return e
        return None
    def get_movable( self, elem ):
        for mov in self.movable_l:
            if mov.py_object == elem:
                return mov
        return None
    def get_position( self, mov ):
        return mov.posx, mov.posy, mov.orient

    def get_rowcol( self, mov ):
        scrx, scry = self.get_position( mov )
        return round(scry-0.5), round(scrx-0.5)
    
    def possible_move( self, srcx, srcy, srco, deltax, deltay, deltao ):
        """
        x,y,o = x, y, orient
        
        Is Move from (srcx, srcy, srco) of (desx, desy, deso) possible: ie, no collision with wall
        Return allowed, destx, desty, destà
        """
        desx = srcx + deltax
        desy = srcy + deltay
        deso = srco + deltao
        
        allowed = True
        for wall in self.wall_l:
            allowed = allowed and not intersect( srcx, srcy, desx, desy,
                                                 *wall )
        # if allowed:
        #     self.movable_agent.posx = desx
        #     self.movable_agent.posy = desy
        return allowed, desx, desy, deso

    def move(self, elem, deltax, deltay, deltao):
        ## Check valid element
        mov = self.get_movable( elem )
        if mov:
            srcx,srcy,srco = self.get_position( mov )
            possible, newx, newy, newo = self.possible_move( srcx, srcy, srco,
                                                             deltax, deltay, deltao )
            if possible:
                mov.posx = newx
                mov.posy = newy
                mov.orient = newo
            
    
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
        pass
        
    def draw(self, canvas ):
        canvas.delete( tk.ALL )
        for wall in self.wall_l:
            canvas.create_line( _xscreen(wall[0]), _yscreen(wall[1]),
                                _xscreen(wall[2]), _yscreen(wall[3]),
                                width=3 )
        
        ## Agent
        self.tkagent.draw( canvas,
                           self.movable_agent.posx,
                           self.movable_agent.posy,
                           self.movable_agent.orient )

        ## Elements
        for elem, posx, posy in self.element_l:
            self._draw_element( canvas, elem, posx, posy )

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
# *************************************************************** PerceptionReal
# ******************************************************************************
class PerceptionReal(Module):
    """
    Définit des senseurs
    - Dist Sensor (orient, max_dist) => self.dist = []
    - Light Sensor (offset, pos) => self.light = []

    describe() => str
    apply() => [self.dist, self.light]
    str_state( state=[] ) => str
    """
    def __init__(self, agent):
        self.agent = agent
        self.world = agent.env

        setattr( agent.perception_module, 'str_display', self.str_display )  
        
        ## Dist sensor : orientation
        self.orient = [ -math.pi/4.0, 0., math.pi/4.0 ]
        self.max_dist = 2
        self.dist = [ self.max_dist for sensor in self.orient ]
        ## add new method to agent
        setattr( agent, 'max_dist_perception', self.max_dist )
        setattr( agent, 'orient_perception', self.orient )        

        ## Light sensor : relative position
        self.offset = 0.3
        self.pos = [ -self.offset, self.offset ]
        self.light = [ 0.0 for sensor in self.pos ]
        setattr( agent, 'pos_perception', self.pos )        

        ## TODO : read sensor from file !

    def describe(self):
        print( "MOD DESCRIBE - PerceptionCont")
        msg = '- 3 capteurs de distance (max_dist={}, donne la distance à l\'obstacle le plus proche dans 3 directions "droite", "devant", "gauche")\n'.format(self.max_dist)
        msg += '- 2 capteurs de lumière (0: lumière est loin, 1: lumière toute proche)\n'
        ## TODO depends of file parameters

        return msg

    def apply(self):
        """
        Return:
        self.dist = [ distance at that orientation ]
        + self.light = [ 1/d^2 de la lumière ]
        """
        print( "MOD APPLY - PerceptionCont")
        perc = []
        ## Distance
        agx, agy, ago = self.world.get_position( self.world.get_movable( self.agent ))
        self.dist = [ self.dist_sensor_value( agx, agy, ago+c) for c in self.orient ]
        perc.extend( self.dist )
        ## Light
        self.light = []
        for light_s_offset in self.pos:
            # position of sensor
            sx = agx + light_s_offset * math.cos( ago - math.pi / 2.0 )
            sy = agy + light_s_offset * math.sin( ago - math.pi / 2.0 )
            self.light.append( self.light_sensor_value( sx, sy ) )
        perc.extend( self.light )

        print( "  perc=", perc )
        return perc

    def str_display(self, perception):
        """ Nicer output
        Hypothèse: perception est une liste de nombre
        """
        msg = "["
        
        for nb in perception[:-1]:
            msg += "{:.2f}, ".format( nb )
        msg += "{:.2f}] ".format( perception[-1] )
        return msg
        

    def dist_sensor_value(self, agx, agy, orient ):
        """
        Depends on the intersection with nearest wall in environment
        """
        cur_dist = self.max_dist * self.max_dist
        xi = None
        yi = None
        for wall in self.world.wall_l:
            inter,x,y = intersect_dir_segment( agx, agy,
                                               math.cos(orient), math.sin(orient),
                                               wall[0], wall[1], wall[2], wall[3],
                                               self.max_dist )
            msg = "Int {:5.2f}, {:5.2f} : {:3.0f}".format( agx,agy, orient/math.pi*180.0 )
            msg +=" to {:5.2f},{:5.2f} ~~ {:5.2f},{:5.2f}".format( wall[0], wall[1], wall[2], wall[3])
            msg +=" ==> {} at {:5.2f},{:5.2f}".format( inter, x, y )
            #print( msg )
            ## A new intersection
            dist = ((x-agx) * (x-agx) + (y-agy) * (y-agy))
            if inter and dist < cur_dist:
                xi = x
                yi = y
                cur_dist = dist
            #print( "  now {:5.2f} for {:5.2f},{:5.2f}".format( cur_dist, xi, yi ))
        return math.sqrt( cur_dist )

    def light_sensor_value(self, agx, agy ):
        """
        Compute distance of given sensor to light if no intersection.
        """
        # Pose of Light
        lx, ly, lo = self.world.get_position(
            self.world.get_movable( self.world.get_elem("light")))
        # A wall between light ? => return 0.0
        for wall in self.world.wall_l:
            inter = intersect( agx, agy, lx, ly,
                               wall[0], wall[1], wall[2], wall[3] )
            if inter:
                return 0.0

        # No wall, return 1/dist^2
        dist = (lx - agx) * (lx - agx) + (ly - agy) * (ly - agy)
        return min(1.0/dist, 1.0)

# ******************************************************************************
# ******************************************************************* ActionReal
# ******************************************************************************
class ActionReal(Module):
    """
    Définit des actions :
    Crée agent.set_speed() = Action.set_speed

    describe() => str
    set_speed( left, right ) => Environment.possible_move( agent, dx, dy, da)
    """
    def __init__(self, agent):
        self.agent = agent
        self.world = agent.env
        self.size = 0.15
        
        ## add new method to agent
        setattr( agent, 'set_speed', self.set_speed )
        setattr( agent, 'str_act', self.str_display )

    def describe(self):
        msg = """- "set_speed( vLeft, vRight )" : détermine la vitesse de chaque roue ( <0 en marche arrière, 0 stop, >0 en marche avant).\n"""
        return msg

    def set_speed(self, spd_left, spd_right, delta_t=0.1 ):
        """
        - left and right are wheel speeds, in unit/s
        """
        ## TODO delta_t from simulator, non ?
        agx,agy,orient = self.world.get_position( self.world.get_movable( self.agent ))
        delta_spd = (spd_left + spd_right) / 2.0 * delta_t
        delta_ang = (spd_right - spd_left) / self.size * delta_t
        
        return self.world.move( self.agent,
                                delta_spd * math.cos(orient),
                                delta_spd * math.sin(orient),
                                delta_ang )

    def str_display(self):
        """
        Hypothesis: self.agent.action is ['set_speed( X, Y )']
        """
        msg_orig = self.agent.action[0]
        nb_start = msg_orig.find( '(' )
        nb_end = msg_orig.find( ')' )
        tok = msg_orig[nb_start+1:nb_end].split(',')
        spd_left = "{:.2f}".format( float( tok[0] ))
        spd_right = "{:.2f}".format( float( tok[1] ))
        return "['set_speed( '"+spd_left+", "+spd_right+")']"
# ******************************************************************************
# ***************************************************************** DecisionReal
# ******************************************************************************
class DecisionReal(DecisionModule):
    """
    Définit une manière de choisir des Actions.
    
    La polotique est 'reactive'

    describe() => str
    apply( state ) =>  [str] décrivant une action "action()"

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
        #print( "__DECISION")
        ## On récupère la valeur des capteurs de distance: state[0] à state[2]
        ## et on normalise ces valeurs dans le tableau 'sn' pour avoir
        ## sn[i]=1 : obstacle tout proche dans cette direction 'i'
        ## sn[i]=0 : pas d'obstacle dans cette direction 'i'
        max_dist = self.agent.max_dist_perception
        sn = np.array( state[0:3], dtype=float )
        sn = 1 - (sn*sn) / (max_dist * max_dist) 
        #print( " sn={}".format(sn) )

        ## On calcule la vitesse à appliquer à chaque roue.
        ## vitesse Gauche = 1 - obstacle_proche_gauche - obstacle_proche_devant
        spd_left = 1 - 0.5*sn[0] - 0.5*sn[1]
        ## vitesse Droite = 1 - obstacle_proche_devant - obstacle_proche_droite
        spd_right = 1 - 0.5*sn[1] - 0.5*sn[2]
        #print( "  dist => {:6.3f}, {:6.3f}".format( spd_left, spd_right ))

        ## and now light sensors [ 1 -> 0 ]
        ## On utilise la valeur des capteurs de lumière (state[3] et state[4]
        ## pour attirer l'agent vers la lumièr
        ## vitesse Gauche multipliée par (1+lumière_proche_droite)
        spd_left = spd_left *   (1.0 + state[4])    # right sensor
        ## vitesse Droite multipliée par (1+lumière_proche_gauche)        
        spd_right = spd_right * (1.0 + state[3])    # left sensor

        ## On construit la commande
        self.act = "set_speed( "+str(spd_left)+", "+str(spd_right)+" )"
        #print( "  act="+self.act )
        return [self.act]

    def get_init_text(self):
        return """def apply(self, state):
        #print( "__DECISION")
        ## On récupère la valeur des capteurs de distance: state[0] à state[2]
        ## et on normalise ces valeurs dans le tableau 'sn' pour avoir
        ## sn[i]=1 : obstacle tout proche dans cette direction 'i'
        ## sn[i]=0 : pas d'obstacle dans cette direction 'i'
        max_dist = self.agent.max_dist_perception
        sn = np.array( state[0:3], dtype=float )
        sn = 1 - (sn*sn) / (max_dist * max_dist) 
        #print( " sn={}".format(sn) )

        ## On calcule la vitesse à appliquer à chaque roue.
        ## vitesse Gauche = 1 - obstacle_proche_gauche - obstacle_proche_devant
        spd_left = 1 - 0.5*sn[0] - 0.5*sn[1]
        ## vitesse Droite = 1 - obstacle_proche_devant - obstacle_proche_droite
        spd_right = 1 - 0.5*sn[1] - 0.5*sn[2]
        #print( "  dist => {:6.3f}, {:6.3f}".format( spd_left, spd_right ))

        ## and now light sensors [ 1 -> 0 ]
        ## On utilise la valeur des capteurs de lumière (state[3] et state[4]
        ## pour attirer l'agent vers la lumièr
        ## vitesse Gauche multipliée par (1+lumière_proche_droite)
        spd_left = spd_left *   (1.0 + state[4])    # right sensor
        ## vitesse Droite multipliée par (1+lumière_proche_gauche)        
        spd_right = spd_right * (1.0 + state[3])    # left sensor

        ## On construit la commande
        self.act = "set_speed( "+str(spd_left)+", "+str(spd_right)+" )"
        #print( "  act="+self.act )
        return [self.act]"""

# ******************************************************************************
# ********************************************************************** TkAgent
# ******************************************************************************
class TkAgent:
    """
    A blue triangle with 2 wheels, seen from above.
    Perception
    - black lines for Distance Sensors
    - green lines for Light Sensors

    draw( canvas, x, y, orient )
    
    """
    def __init__(self, agent):
        self.agent = agent
        self.size = 0.15
        size = self.size
        self.body = [ (-size, -size), (size,0), (-size, size) ]
        self.wheel_left = [ (-size, size), (0,size),
                            (0, size/2.0 ),
                            (-size, size/2.0) ]
        self.wheel_right = [ (-size, -size), (0,-size),
                             (0, -size/2.0 ),
                             (-size, -size/2.0) ]
        
    def rotate(self, x, y, angle):
        rx = x * math.cos( angle ) - y * math.sin( angle )
        ry = x * math.sin( angle ) + y * math.cos( angle )
        return rx,ry
    def to_screen(self, offx, offy, x, y):
        return _xscreen( x+offx ), _yscreen( y+offy )
    
    def draw(self, canvas, x, y, orient):
        """
        Params:
        - canvas : tk.Canvas
        - x, y: where to draw
        - orient (rad) : agent orientation
        """
        rbody = [ self.rotate( *pt, orient ) for pt in self.body ]
        sbody = [ self.to_screen( x, y, *pt) for pt in rbody]
        canvas.create_polygon( sbody, fill="", outline="blue", width=3)
        
        rwl = [ self.rotate( *pt, orient ) for pt in self.wheel_left ]
        swl = [ self.to_screen( x, y, *pt) for pt in rwl]
        canvas.create_polygon( swl, fill="blue", outline="blue", width=3)

        rwr = [ self.rotate( *pt, orient ) for pt in self.wheel_right ]
        swr = [ self.to_screen( x, y, *pt) for pt in rwr]
        canvas.create_polygon( swr, fill="blue", outline="blue", width=3)

        ## Sensors
        orient_perc = self.agent.orient_perception
        # dist to wall
        for ang,dist in zip(orient_perc, self.agent.state[0:3] ):
            sensx = x + dist * math.cos( orient + ang )
            sensy = y + dist * math.sin( orient + ang )
            canvas.create_line( _xscreen(x), _yscreen(y),
                                _xscreen(sensx), _yscreen(sensy),
                                fill="black" )
        # to light
        pos_perception = self.agent.pos_perception
        lx, ly, lo = self.agent.env.get_position(
            self.agent.env.get_movable( self.agent.env.get_elem("light")))
        for offset,light in zip( pos_perception, self.agent.state[3:5] ):
            # sensor position
            sx = x + offset * math.cos( orient - math.pi/2 )
            sy = y + offset * math.sin( orient - math.pi/2 )
            if light > 0.0001:
                canvas.create_line( _xscreen(sx), _yscreen(sy),
                                    _xscreen(lx), _yscreen(ly),
                                    fill="green" )
            else:
                canvas.create_line( _xscreen(sx), _yscreen(sy),
                                    _xscreen(lx), _yscreen(ly),
                                    fill="green", dash=(10,10) )
            tx = x + 0.8*offset * math.cos( orient - math.pi/2 )
            ty = y + 0.8*offset * math.sin( orient - math.pi/2 )
            canvas.create_text( _xscreen(tx), _yscreen(ty), fill="green",
                                text = "{:5.2f}".format( light ) )
    
if __name__ == '__main__':
    env = MazeRealWorld( "cheeze_maze.txt" )
    
