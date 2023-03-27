# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter.scrolledtext import ScrolledText

# ******************************************************************************
# ******************************************************************** TkConsole
# ******************************************************************************
class TkConsole:
    """
    Display msg in a scrolled text
    
    display(), clear()
    """
    def __init__(self, main_window, row=0, col=0):
        self.main_window = main_window

        # Create a ScrolledText Wdget
        self.frame = tk.LabelFrame( main_window, text="Console",
                                    bd=5, relief=tk.GROOVE )
        self.frame.grid( row=row, column=col,
                         rowspan=1, columnspan=1,
                         padx=5, pady=5,
                         sticky=(tk.N, tk.E, tk.W, tk.S))
        self.frame.rowconfigure( 0, weight=1 )
        self.frame.columnconfigure( 0, weight=1 )
        self.scrolled_text = ScrolledText(self.frame,
                                          state='disabled', height=10)
        self.scrolled_text.grid(row=0, column=0,
                                sticky=(tk.N, tk.S, tk.W, tk.E))
        self.scrolled_text.configure(font='TkFixedFont')
        
    def display(self, msg):
        self.scrolled_text.configure(state='normal')
        self.scrolled_text.insert(tk.END, msg + '\n' )
        self.scrolled_text.configure(state='disabled')
        # Autoscroll to the bottom
        self.scrolled_text.yview(tk.END)

    def clear(self):
        self.scrolled_text.configure(state='normal')
        self.scrolled_text.delete( 1.0, tk.END )
        self.scrolled_text.configure(state='disabled')

    def set_height(self, nbrow ):
        self.scrolled_text.configure( height=nbrow )
# ******************************************************************************

    
