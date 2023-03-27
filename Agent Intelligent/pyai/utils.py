# -*- coding: utf-8 -*-

import math

# ******************************************************** Environment to Canvas
def _xscreen( x, scale=100, offset=10):
    return offset + x*scale
def _yscreen( y, scale=100, offset=10):
    return offset + y*scale
# ******************************************************** Canvas to Environment
def _xenv( x, scale=100, offset=10):
    return (x - offset) / scale
def _yenv( y, scale=100, offset=10):
    return (y - offset) / scale

# ******************************************************************** INTERSECT
def intersect( p_startx, p_starty, p_endx, p_endy,
               q_startx, q_starty, q_endx, q_endy ):
    """
    Check intersection betwen segment p and q
    https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect

    Return:
    - boolean
    """
    
    px = p_startx
    py = p_starty
    rx = p_endx - p_startx
    ry = p_endy - p_starty

    qx = q_startx
    qy = q_starty
    sx = q_endx - q_startx
    sy = q_endy - q_starty

    is_inter, x, y = intersect_dir_segment( px, py, rx, ry,
                                            q_startx, q_starty, q_endx, q_endy,
                                            math.sqrt( rx*rx + ry*ry ))
    return is_inter

def intersect_dir_segment( p_startx, p_starty, p_dirx, p_diry,
                           q_startx, q_starty, q_endx, q_endy,
                           max_dir = 100.0):
    # log = "  ids( {},{} -> {},{}".format( p_startx, p_starty, p_dirx, p_diry)
    # log +=" with {},{} ~~ {},{}".format( q_startx, q_starty, q_endx, q_endy )
    # log +=" max_dir={} )".format( max_dir )
    # print( log )
    
    px = p_startx
    py = p_starty
    rx = p_dirx 
    ry = p_diry
    rnorm = math.sqrt( rx * rx + ry * ry)
    if rnorm > 0.0000000001:
        rx = p_dirx * max_dir / rnorm
        ry = p_diry * max_dir / rnorm
    else:
        rx = 0
        ry = 0

    qx = q_startx
    qy = q_starty
    sx = q_endx - q_startx
    sy = q_endy - q_starty

    r_s = rx * sy - ry * sx
    qmp_s = ((qx-px) * sy - (qy-py) * sx)
    qmp_r = (qx-px) * ry - (qy-py) * rx

    # log = "  p={},{} r={},{}".format( px,py, rx,ry)
    # log +=" q={},{} s={},{}".format( qx,qy, sx,sy )
    # log +="\n  r_s={} qmp_s={} qmp_r={}".format( r_s, qmp_s, qmp_r)
    # print( log )
    
    ## r_s == 0 and qmp_r == O : colinear
    if abs(r_s) < 0.0000000001 and abs(qmp_r) < 0.0000000001:
        ## express q = p +t0.r and s = p + t1.r
        rr = rx *rx + ry * ry
        ## p is only a point, in q ?
        if abs(rr) < 0.0000000001:
            qq = qx * qx + ry * ry
            ## q is only a point, same as p
            if abs(qq) < 0.0000000001:
                if abs(px-qx) < 0.0000000001 and abs(py-qy) < 0.0000000001:
                    return True, px, py
                return False, 0, 0
            ## abcisse of p relative to q -> s
            l = (px - qx) * qx + (py - qy) * qy / qq
            if 0 <= l <= 1:
                return True, qx+l*sx, qy+l*sy
            ## otherwise,
            return False, 0, 0
        t0 = ((qx - px ) * rx + (qy - py) * ry) / rr
        t1 = ((qx+sx-px) * rx + (qy+sy-py) * ry) / rr
        ## segment in opposite directions
        mint = min(t0,t1)
        maxt = max(t0,t1)
        if 0 <= mint <= maxt <= 1:
            return True, px+mint*rx, py+mint*ry
        if mint <= 0 <= maxt:
            return True, px, py
        if mint <= 1 <= maxt:
            return True, px+mint*rx, py+mint*ry
        return False, 0, 0
    ## both are parallel
    elif abs( r_s ) < 0.0000000001:
        return False, 0, 0
    ## r_s != 0 and 0<=t<=1 and 0<=u<=1 : intersect TRUE
    ## meet at p + t.r = q + u.s
    elif abs(r_s) > 0.0000000001:
        t = qmp_s / r_s
        u = qmp_r / r_s
        if ( 0 <= t <= 1) and (0 <= u <= 1):
            return True, px+t*rx, py+t*ry
    ## otherwise, no intersection
    return False, 0, 0

