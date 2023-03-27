# -*- coding: utf-8 -*-

# Main level application, build gui of Simulateur in main_window.
# Can be run()

import tkinter as tk

# *********************************************************************** TkSimu
class TkSimu:
    """
    init() => set title and then use
    Simulateur : build_gui(), init_draw(), draw()
    """
    def __init__(self, simulator, title="Simulateur"):
        self.sim = simulator
        ## Graphic
        self.main_window = tk.Tk()
        named_fonts = tk.font.names()
        print( "FONTS = ", named_fonts )
        self.text_font = tk.font.nametofont("TkTextFont")
        print( "text_font={}", self.text_font )
        #text_font.configure(size=32)
        self.fixed_font = tk.font.nametofont( "TkFixedFont" )
        self.fixed_font.configure(size=8)
        self.default_font = tk.font.nametofont("TkDefaultFont")
        #default_font.configure(size=10)
        
        self.main_window.title( title )
        self.main_window.columnconfigure( 0, weight=1 )
        self.main_window.columnconfigure( 1, weight=1 )
        # self.main_window.rowconfigure( 0, weight=1 )
        self.main_window.rowconfigure( 1, weight=1 )
        self.main_window.rowconfigure( 2, weight=1 )
        self.main_window.rowconfigure( 3, weight=1 )        
        
        self.menubar = tk.Menu( self.main_window )
        ## Menu : commandes
        self.cmd_menu = tk.Menu( self.menubar, tearoff=0 )
        self.cmd_menu.add_command( label="Quit",
                                   command=self.main_window.destroy )
        self.menubar.add_cascade( label="Commandes", menu=self.cmd_menu )
        ## Menu : change Fonts
        self.font_menu = tk.Menu( self.menubar, tearoff=0 )
        for fsize in [6, 8, 10, 12, 14]:#, 16, 18, 20]:
            self.font_menu.add_command(
                label="FontSize {}".format( fsize ),
                command=lambda fs=fsize : self.set_fontsize(fs))
        self.menubar.add_cascade( label="Fonte Simu", menu=self.font_menu )

        ## Menu : change console size
        self.console_menu = tk.Menu( self.menubar, tearoff=0 )
        for fsize in [5, 10, 15, 20]:#, 16, 18, 20]:
            self.console_menu.add_command(
                label="Consolesize {}".format( fsize ),
                command=lambda fs=fsize : self.sim.console_frame.set_height(fs))
        self.menubar.add_cascade( label="Fonte Console", menu=self.console_menu )
        self.main_window.config( menu = self.menubar )

        ## Build GUI
        self.sim.build_gui( self.main_window )
        self.sim.editor.set_font( self.fixed_font )
        self.sim.init_draw()
        self.sim.draw()

        self.set_fontsize( 8 )
        
    def run(self):
        self.main_window.mainloop()

    def set_fontsize(self, fontsize):
        """ 
        Change Font size.
        BUG : do not change size in Editor !!
        """
        print( "setting FontSize={}".format( fontsize ))
        self.fixed_font.configure( size=fontsize )
        self.text_font.configure( size = fontsize )
        ##self.sim.editor.set_fontsize( fontsize )
        ##self.default_font.configure( size=fontsize )
        
# ******************************************************************************


        
    
