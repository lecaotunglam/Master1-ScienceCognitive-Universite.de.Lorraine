# -*- coding: utf-8 -*-

# TkEditor with
# - undo (Ctrl-Z), cut/copy/paste
# - smart indent (and smart-backspace)
# - un/comment region (Shif/Ctrl-D)
# - select-all (Ctrl-A), unselect (Esc)
# - syntax colorization
# - auto-complete, auto-extend
# - paren matching

import sys
import string
import tkinter as tk
from idlelib.config import idleConf
from idlelib.multicall import MultiCallCreator
from idlelib import pyparse

# The default tab setting for a Text widget, in average-width characters.
TK_TABWIDTH_DEFAULT = 8

# ******************************************************************************
# ********************************************************************* TkEditor
# ******************************************************************************
class TkEditor(object):
    from idlelib.percolator import Percolator
    from idlelib.colorizer import ColorDelegator, color_config
    from idlelib.undo import UndoDelegator
    from idlelib.statusbar import MultiStatusBar
    from idlelib import mainmenu
    from idlelib.autocomplete import AutoComplete
    from idlelib.autoexpand import AutoExpand
    from idlelib.parenmatch import ParenMatch
    
    
    def __init__(self, main_window):
        "docstring"
        self.main_window = main_window

        self.prompt_last_line = '' # Override in PyShell
        self.text_frame = text_frame = tk.Frame( main_window )
        self.vbar = vbar = tk.Scrollbar(text_frame, name='vbar')
        self.width = 80
        self.height= 40
        
        text_options = {
                'name': 'text',
                'padx': 5,
                'wrap': 'none',
                'highlightthickness': 0,
                'width': self.width,
                'height': self.height }
        self.text = text = MultiCallCreator(tk.Text)(text_frame, **text_options)

        self.set_status_bar()
        vbar['command'] = text.yview
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        text['yscrollcommand'] = vbar.set
        text['font'] = idleConf.GetFont(self.main_window,
                                        'main', 'EditorWindow')
        # print( "  Font={}".format( idleConf.GetFont(self.main_window,
        #                                             'main', 'EditorWindow') ))
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        text.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        text.focus_set()

        self.apply_bindings()

        text.bind('<MouseWheel>', self.mousescroll)
        text.bind('<Button-4>', self.mousescroll)
        text.bind('<Button-5>', self.mousescroll)
        
        text.bind("<<cut>>", self.cut)
        text.bind("<<copy>>", self.copy)
        text.bind("<<paste>>", self.paste)
        text.bind("<<center-insert>>", self.center_insert_event)

        text.bind("<<select-all>>", self.select_all)
        text.bind("<<remove-selection>>", self.remove_selection)
        
        text.bind("<<smart-backspace>>",self.smart_backspace_event)
        text.bind("<<newline-and-indent>>",self.newline_and_indent_event)
        text.bind("<<smart-indent>>",self.smart_indent_event)
        text.bind("<<comment-region>>",self.comment_region_event)
        text.bind("<<uncomment-region>>",self.uncomment_region_event)

        text.bind("<Left>", self.move_at_edge_if_selection(0))
        text.bind("<Right>", self.move_at_edge_if_selection(1))
        text.bind("<<beginning-of-line>>", self.home_callback)
        
        # usetabs true  -> literal tab characters are used by indent and
        #                  dedent cmds, possibly mixed with spaces if
        #                  indentwidth is not a multiple of tabwidth,
        #                  which will cause Tabnanny to nag!
        #         false -> tab characters are converted to spaces by indent
        #                  and dedent cmds, and ditto TAB keystrokes
        # Although use-spaces=0 can be configured manually in config-main.def,
        # configuration of tabs v. spaces is not supported in the configuration
        # dialog.  IDLE promotes the preferred Python indentation: use spaces!
        usespaces = True
        self.usetabs = not usespaces

        # tabwidth is the display width of a literal tab character.
        # CAUTION:  telling Tk to use anything other than its default
        # tab setting causes it to use an entirely different tabbing algorithm,
        # treating tab stops as fixed distances from the left margin.
        # Nobody expects this, so for now tabwidth should never be changed.
        self.tabwidth = 8    # must remain 8 until Tk is fixed.

        # indentwidth is the number of screen characters per indent level.
        # The recommended Python indentation is four spaces.
        self.indentwidth = self.tabwidth
        self.set_notabs_indentwidth()
        self.set_indentation_params(True, guess=False) ## indentation ON

        # If context_use_ps1 is true, parsing searches back for a ps1 line;
        # else searches for a popular (if, def, ...) Python stmt.
        self.context_use_ps1 = False
        
        # When searching backwards for a reliable place to begin parsing,
        # first start num_context_lines[0] lines back, then
        # num_context_lines[1] lines back if that didn't work, and so on.
        # The last value should be huge (larger than the # of lines in a
        # conceivable file).
        # Making the initial values larger slows things down more often.
        self.num_context_lines = 50, 500, 5000000
        self.per = per = self.Percolator(text)
        self.undo = undo = self.UndoDelegator()
        per.insertfilter(undo)
        text.undo_block_start = undo.undo_block_start
        text.undo_block_stop = undo.undo_block_stop

        ## IO and Color
        self.color = None # initialized below in self.ResetColorizer
        self.ResetColorizer()

        # Add pseudoevents for former extension fixed keys.
        # (This probably needs to be done once in the process.)
        text.event_add('<<autocomplete>>', '<Key-Tab>')
        text.event_add('<<try-open-completions>>', '<KeyRelease-period>',
                       '<KeyRelease-slash>', '<KeyRelease-backslash>')
        text.event_add('<<try-open-calltip>>', '<KeyRelease-parenleft>')
        text.event_add('<<refresh-calltip>>', '<KeyRelease-parenright>')
        text.event_add('<<paren-closed>>', '<KeyRelease-parenright>', '<KeyRelease-bracketright>', '<KeyRelease-braceright>')

        # Former extension bindings depends on frame.text being packed
        # (called from self.ResetColorizer()).
        autocomplete = self.AutoComplete(self)
        text.bind("<<autocomplete>>", autocomplete.autocomplete_event)
        text.bind("<<try-open-completions>>",
                  autocomplete.try_open_completions_event)
        text.bind("<<force-open-completions>>",
                  autocomplete.force_open_completions_event)
        text.bind("<<expand-word>>", self.AutoExpand(self).expand_word_event)
        text.event_add('<<paren-closed>>', '<KeyRelease-parenright>', '<KeyRelease-bracketright>', '<KeyRelease-braceright>')
        parenmatch = self.ParenMatch(self)
        text.bind("<<flash-paren>>", parenmatch.flash_paren_event)
        text.bind("<<paren-closed>>", parenmatch.paren_closed_event)
        
    def set_text(self, chars):
        ## Remove previous
        self.text.delete("1.0", "end")
        # TODO: self.set_filename(None)
        self.text.insert("1.0", chars)
        # TODO: self.reset_undo()
        # TODO: self.set_filename(filename)
        self.text.mark_set("insert", "1.0")
        self.text.yview("insert")
        # TODO: self.updaterecentfileslist(filename)
        return True

    def set_font(self, font):
        self.text['font'] = font
    def set_fontsize(self, fontsize):
        print( "Editor.Font={}".format( self.text['font'] ))
        current_font = self.text['font']
        new_font = (current_font[0], fontsize, current_font[2])
        self.text['font'] = new_font
        
        ##self.text.configure( size=fontsize )
    
    # --------------------------------------------------------------  status_bar
    def set_status_bar(self):
        self.status_bar = self.MultiStatusBar(self.main_window)
        sep = tk.Frame(self.main_window,
                       height=1, borderwidth=1, background='grey75')
        if sys.platform == "darwin":
            # Insert some padding to avoid obscuring some of the statusbar
            # by the resize widget.
            self.status_bar.set_label('_padding1', '    ', side=tk.RIGHT)
        self.status_bar.set_label('column', 'Col: ?', side=tk.RIGHT)
        self.status_bar.set_label('line', 'Ln: ?', side=tk.RIGHT)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        sep.pack(side=tk.BOTTOM, fill=tk.X)
        self.text.bind("<<set-line-and-column>>", self.set_line_and_column)
        self.text.event_add("<<set-line-and-column>>",
                            "<KeyRelease>", "<ButtonRelease>")
        self.text.after_idle(self.set_line_and_column)
        
    def set_line_and_column(self, event=None):
        line, column = self.text.index(tk.INSERT).split('.')
        self.status_bar.set_label('column', 'Col: %s' % column)
        self.status_bar.set_label('line', 'Ln: %s' % line)

    def set_notabs_indentwidth(self):
        "Update the indentwidth if changed and not using tabs in this window"
        # Called from configdialog.py
        if not self.usetabs:
            self.indentwidth = 4

    # ----------------------------------------------------------------- bindings
    def apply_bindings(self, keydefs=None):
        if keydefs is None:
            keydefs = self.mainmenu.default_keydefs
        text = self.text
        text.keydefs = keydefs
        for event, keylist in keydefs.items():
            if keylist:
                text.event_add(event, *keylist)

    # ----------------------------------------------------------- cut/copy/paste
    def cut(self,event):
        self.text.event_generate("<<Cut>>")
        return "break"

    def copy(self,event):
        if not self.text.tag_ranges("sel"):
            # There is no selection, so do nothing and maybe interrupt.
            return None
        self.text.event_generate("<<Copy>>")
        return "break"

    def paste(self,event):
        self.text.event_generate("<<Paste>>")
        self.text.see("insert")
        return "break"

    def center_insert_event(self, event):
        self.center()
        return "break"

    def center(self, mark="insert"):
        text = self.text
        top, bot = self.getwindowlines()
        lineno = self.getlineno(mark)
        height = bot - top
        newtop = max(1, lineno - height//2)
        text.yview(float(newtop))

    # --------------------------------------------------------------------- home
    def home_callback(self, event):
        if (event.state & 4) != 0 and event.keysym == "Home":
            # state&4==Control. If <Control-Home>, use the Tk binding.
            return None
        if self.text.index("iomark") and \
           self.text.compare("iomark", "<=", "insert lineend") and \
           self.text.compare("insert linestart", "<=", "iomark"):
            # In Shell on input line, go to just after prompt
            insertpt = int(self.text.index("iomark").split(".")[1])
        else:
            line = self.text.get("insert linestart", "insert lineend")
            for insertpt in range(len(line)):
                if line[insertpt] not in (' ','\t'):
                    break
            else:
                insertpt=len(line)
        lineat = int(self.text.index("insert").split('.')[1])
        if insertpt == lineat:
            insertpt = 0
        dest = "insert linestart+"+str(insertpt)+"c"
        if (event.state&1) == 0:
            # shift was not pressed
            self.text.tag_remove("sel", "1.0", "end")
        else:
            if not self.text.index("sel.first"):
                # there was no previous selection
                self.text.mark_set("my_anchor", "insert")
            else:
                if self.text.compare(self.text.index("sel.first"), "<",
                                     self.text.index("insert")):
                    self.text.mark_set("my_anchor", "sel.first") # extend back
                else:
                    self.text.mark_set("my_anchor", "sel.last") # extend forward
            first = self.text.index(dest)
            last = self.text.index("my_anchor")
            if self.text.compare(first,">",last):
                first,last = last,first
            self.text.tag_remove("sel", "1.0", "end")
            self.text.tag_add("sel", first, last)
        self.text.mark_set("insert", dest)
        self.text.see("insert")
        return "break"

    # ------------------------------------------------------------------- scroll
    def mousescroll(self, event):
        """Handle scrollwheel event.
        For wheel up, event.delta = 120*n on Windows, -1*n on darwin,
        where n can be > 1 if one scrolls fast.  Flicking the wheel
        generates up to maybe 20 events with n up to 10 or more 1.
        Macs use wheel down (delta = 1*n) to scroll up, so positive
        delta means to scroll up on both systems.
        X-11 sends Control-Button-4 event instead.
        """
        up = {tk.EventType.MouseWheel: event.delta > 0,
              tk.EventType.Button: event.num == 4}
        lines = -5 if up[event.type] else 5
        self.text.yview_scroll(lines, 'units')
        return 'break'

    # ------------------------------------------------------------------- select
    def select_all(self, event=None):
        self.text.tag_add("sel", "1.0", "end-1c")
        self.text.mark_set("insert", "1.0")
        self.text.see("insert")
        return "break"

    def remove_selection(self, event=None):
        self.text.tag_remove("sel", "1.0", "end")
        self.text.see("insert")
        return "break"
    
    def move_at_edge_if_selection(self, edge_index):
        """Cursor move begins at start or end of selection
        When a left/right cursor key is pressed create and return to Tkinter a
        function which causes a cursor move from the associated edge of the
        selection.
        """
        self_text_index = self.text.index
        self_text_mark_set = self.text.mark_set
        edges_table = ("sel.first+1c", "sel.last-1c")
        def move_at_edge(event):
            if (event.state & 5) == 0: # no shift(==1) or control(==4) pressed
                try:
                    self_text_index("sel.first")
                    self_text_mark_set("insert", edges_table[edge_index])
                except TclError:
                    pass
        return move_at_edge
    
    ### begin autoindent code ###  (configuration was moved to beginning of class)
    ###

    # Tk implementations of "virtual text methods" -- each platform
    # reusing IDLE's support code needs to define these for its GUI's
    # flavor of widget.

    # Is character at text_index in a Python string?  Return 0 for
    # "guaranteed no", true for anything else.  This info is expensive
    # to compute ab initio, but is probably already known by the
    # platform's colorizer.

    def is_char_in_string(self, text_index):
        if self.color:
            # Return true iff colorizer hasn't (re)gotten this far
            # yet, or the character is tagged as being in a string
            return self.text.tag_prevrange("TODO", text_index) or \
                   "STRING" in self.text.tag_names(text_index)
        else:
            # The colorizer is missing: assume the worst
            return 1

    # If a selection is defined in the text widget, return (start,
    # end) as Tkinter text indices, otherwise return (None, None)
    def get_selection_indices(self):
        try:
            first = self.text.index("sel.first")
            last = self.text.index("sel.last")
            return first, last
        except tk.TclError:
            return None, None
    
    # Return the text widget's current view of what a tab stop means
    # (equivalent width in spaces).

    def get_tk_tabwidth(self):
        current = self.text['tabs'] or TK_TABWIDTH_DEFAULT
        return int(current)
    
    # Set the text widget's current view of what a tab stop means.

    def set_tk_tabwidth(self, newtabwidth):
        text = self.text
        if self.get_tk_tabwidth() != newtabwidth:
            # Set text widget tab width
            pixels = text.tk.call("font", "measure", text["font"],
                                  "-displayof", text.master,
                                  "n" * newtabwidth)
            text.configure(tabs=pixels)
            
    def set_indentation_params(self, is_py_src, guess=True):
        if is_py_src and guess:
            i = self.guess_indent()
            if 2 <= i <= 8:
                self.indentwidth = i
            if self.indentwidth != self.tabwidth:
                self.usetabs = False
        self.set_tk_tabwidth(self.tabwidth)

    def smart_backspace_event(self, event):
        text = self.text
        first, last = self.get_selection_indices()
        if first and last:
            text.delete(first, last)
            text.mark_set("insert", first)
            return "break"
        # Delete whitespace left, until hitting a real char or closest
        # preceding virtual tab stop.
        chars = text.get("insert linestart", "insert")
        if chars == '':
            if text.compare("insert", ">", "1.0"):
                # easy: delete preceding newline
                text.delete("insert-1c")
            else:
                text.bell()     # at start of buffer
            return "break"
        if  chars[-1] not in " \t":
            # easy: delete preceding real char
            text.delete("insert-1c")
            return "break"
        # Ick.  It may require *inserting* spaces if we back up over a
        # tab character!  This is written to be clear, not fast.
        tabwidth = self.tabwidth
        have = len(chars.expandtabs(tabwidth))
        assert have > 0
        want = ((have - 1) // self.indentwidth) * self.indentwidth
        # Debug prompt is multilined....
        ncharsdeleted = 0
        while 1:
            if chars == self.prompt_last_line:  # '' unless PyShell
                break
            chars = chars[:-1]
            ncharsdeleted = ncharsdeleted + 1
            have = len(chars.expandtabs(tabwidth))
            if have <= want or chars[-1] not in " \t":
                break
        text.undo_block_start()
        text.delete("insert-%dc" % ncharsdeleted, "insert")
        if have < want:
            text.insert("insert", ' ' * (want - have))
        text.undo_block_stop()
        return "break"

    def smart_indent_event(self, event):
        # if intraline selection:
        #     delete it
        # elif multiline selection:
        #     do indent-region
        # else:
        #     indent one level
        text = self.text
        first, last = self.get_selection_indices()
        text.undo_block_start()
        try:
            if first and last:
                if index2line(first) != index2line(last):
                    return self.indent_region_event(event)
                text.delete(first, last)
                text.mark_set("insert", first)
            prefix = text.get("insert linestart", "insert")
            raw, effective = classifyws(prefix, self.tabwidth)
            if raw == len(prefix):
                # only whitespace to the left
                self.reindent_to(effective + self.indentwidth)
            else:
                # tab to the next 'stop' within or to right of line's text:
                if self.usetabs:
                    pad = '\t'
                else:
                    effective = len(prefix.expandtabs(self.tabwidth))
                    n = self.indentwidth
                    pad = ' ' * (n - effective % n)
                text.insert("insert", pad)
            text.see("insert")
            return "break"
        finally:
            text.undo_block_stop()

    def newline_and_indent_event(self, event):
        text = self.text
        first, last = self.get_selection_indices()
        text.undo_block_start()
        try:
            if first and last:
                text.delete(first, last)
                text.mark_set("insert", first)
            line = text.get("insert linestart", "insert")
            i, n = 0, len(line)
            while i < n and line[i] in " \t":
                i = i+1
            if i == n:
                # the cursor is in or at leading indentation in a continuation
                # line; just inject an empty line at the start
                text.insert("insert linestart", '\n')
                return "break"
            indent = line[:i]
            # strip whitespace before insert point unless it's in the prompt
            i = 0
            while line and line[-1] in " \t" and line != self.prompt_last_line:
                line = line[:-1]
                i = i+1
            if i:
                text.delete("insert - %d chars" % i, "insert")
            # strip whitespace after insert point
            while text.get("insert") in " \t":
                text.delete("insert")
            # start new line
            text.insert("insert", '\n')

            # adjust indentation for continuations and block
            # open/close first need to find the last stmt
            lno = index2line(text.index('insert'))
            y = pyparse.Parser(self.indentwidth, self.tabwidth)
            if not self.context_use_ps1:
                for context in self.num_context_lines:
                    startat = max(lno - context, 1)
                    startatindex = repr(startat) + ".0"
                    rawtext = text.get(startatindex, "insert")
                    y.set_code(rawtext)
                    bod = y.find_good_parse_start(
                              self.context_use_ps1,
                              self._build_char_in_string_func(startatindex))
                    if bod is not None or startat == 1:
                        break
                y.set_lo(bod or 0)
            else:
                r = text.tag_prevrange("console", "insert")
                if r:
                    startatindex = r[1]
                else:
                    startatindex = "1.0"
                rawtext = text.get(startatindex, "insert")
                y.set_code(rawtext)
                y.set_lo(0)

            c = y.get_continuation_type()
            if c != pyparse.C_NONE:
                # The current stmt hasn't ended yet.
                if c == pyparse.C_STRING_FIRST_LINE:
                    # after the first line of a string; do not indent at all
                    pass
                elif c == pyparse.C_STRING_NEXT_LINES:
                    # inside a string which started before this line;
                    # just mimic the current indent
                    text.insert("insert", indent)
                elif c == pyparse.C_BRACKET:
                    # line up with the first (if any) element of the
                    # last open bracket structure; else indent one
                    # level beyond the indent of the line with the
                    # last open bracket
                    self.reindent_to(y.compute_bracket_indent())
                elif c == pyparse.C_BACKSLASH:
                    # if more than one line in this stmt already, just
                    # mimic the current indent; else if initial line
                    # has a start on an assignment stmt, indent to
                    # beyond leftmost =; else to beyond first chunk of
                    # non-whitespace on initial line
                    if y.get_num_lines_in_stmt() > 1:
                        text.insert("insert", indent)
                    else:
                        self.reindent_to(y.compute_backslash_indent())
                else:
                    assert 0, "bogus continuation type %r" % (c,)
                return "break"

            # This line starts a brand new stmt; indent relative to
            # indentation of initial line of closest preceding
            # interesting stmt.
            indent = y.get_base_indent_string()
            text.insert("insert", indent)
            if y.is_block_opener():
                self.smart_indent_event(event)
            elif indent and y.is_block_closer():
                self.smart_backspace_event(event)
            return "break"
        finally:
            text.see("insert")
            text.undo_block_stop()

    # Our editwin provides an is_char_in_string function that works
    # with a Tk text index, but PyParse only knows about offsets into
    # a string. This builds a function for PyParse that accepts an
    # offset.

    def _build_char_in_string_func(self, startindex):
        def inner(offset, _startindex=startindex,
                  _icis=self.is_char_in_string):
            return _icis(_startindex + "+%dc" % offset)
        return inner

    # Make string that displays as n leading blanks.

    def _make_blanks(self, n):
        if self.usetabs:
            ntabs, nspaces = divmod(n, self.tabwidth)
            return '\t' * ntabs + ' ' * nspaces
        else:
            return ' ' * n

    # Delete from beginning of line to insert point, then reinsert
    # column logical (meaning use tabs if appropriate) spaces.

    def reindent_to(self, column):
        text = self.text
        text.undo_block_start()
        if text.compare("insert linestart", "!=", "insert"):
            text.delete("insert linestart", "insert")
        if column:
            text.insert("insert", self._make_blanks(column))
        text.undo_block_stop()

    # ------------------------------------------------------------------- region
    def get_region(self):
        text = self.text
        first, last = self.get_selection_indices()
        if first and last:
            head = text.index(first + " linestart")
            tail = text.index(last + "-1c lineend +1c")
        else:
            head = text.index("insert linestart")
            tail = text.index("insert lineend +1c")
        chars = text.get(head, tail)
        lines = chars.split("\n")
        return head, tail, chars, lines

    def set_region(self, head, tail, chars, lines):
        text = self.text
        newchars = "\n".join(lines)
        if newchars == chars:
            text.bell()
            return
        text.tag_remove("sel", "1.0", "end")
        text.mark_set("insert", head)
        text.undo_block_start()
        text.delete(head, tail)
        text.insert(head, newchars)
        text.undo_block_stop()
        text.tag_add("sel", head, "insert")
        
    # ------------------------------------------------------------------ comment
    def comment_region_event(self, event):
        head, tail, chars, lines = self.get_region()
        for pos in range(len(lines) - 1):
            line = lines[pos]
            lines[pos] = '##' + line
        self.set_region(head, tail, chars, lines)
        return "break"

    def uncomment_region_event(self, event):
        head, tail, chars, lines = self.get_region()
        for pos in range(len(lines)):
            line = lines[pos]
            if not line:
                continue
            if line[:2] == '##':
                line = line[2:]
            elif line[:1] == '#':
                line = line[1:]
            lines[pos] = line
        self.set_region(head, tail, chars, lines)
        return "break"

    # -------------------------------------------------------------------- color
    def _addcolorizer(self):
        if self.color:
            return
        #ALWAYS if self.ispythonsource(self.io.filename):
        self.color = self.ColorDelegator()
        # can add more colorizers here...
        if self.color:
            self.per.removefilter(self.undo)
            self.per.insertfilter(self.color)
            self.per.insertfilter(self.undo)

    def _rmcolorizer(self):
        if not self.color:
            return
        self.color.removecolors()
        self.per.removefilter(self.color)
        self.color = None

    def ResetColorizer(self):
        "Update the color theme"
        # Called from self.filename_change_hook and from configdialog.py
        self._rmcolorizer()
        self._addcolorizer()
        TkEditor.color_config(self.text)

    # ------------------------------------------------------------- syntax_error
    IDENTCHARS = string.ascii_letters + string.digits + "_"

    def colorize_syntax_error(self, text, pos):
        text.tag_add("ERROR", pos)
        char = text.get(pos)
        if char and char in self.IDENTCHARS:
            text.tag_add("ERROR", pos + " wordstart", pos)
        if '\n' == text.get(pos):   # error at line end
            text.mark_set("insert", pos)
        else:
            text.mark_set("insert", pos + "+1c")
        text.see(pos)

        
# ********************************************************************* TkEditor

# "line.col" -> line, as an int
def index2line(index):
    return int(float(index))
            
# Look at the leading whitespace in s.
# Return pair (# of leading ws characters,
#              effective # of leading blanks after expanding
#              tabs to width tabwidth)

def classifyws(s, tabwidth):
    raw = effective = 0
    for ch in s:
        if ch == ' ':
            raw = raw + 1
            effective = effective + 1
        elif ch == '\t':
            raw = raw + 1
            effective = (effective // tabwidth + 1) * tabwidth
        else:
            break
    return raw, effective       
# ******************************************************************************


if __name__ == '__main__':
    def execute():
        print( "*************" )
        print( editor.text.get(1.0, tk.END ))
        print( "-------------" )
        
    default_txt = \
"""def bizarre(self, vrac):
    vrac = vrac+".txt"
    print( "V={}.format( vrac ))
"""
    root = tk.Tk()
    btn_frame = tk.Frame( root, bd=5 )
    btn_frame.grid( row=0, column=0 )
    run_btn = tk.Button( btn_frame, text='Run',
                         command = execute )
    run_btn.grid( row=0, column=0, padx=5, pady=5 )

    editor_frame = tk.Frame( root, bd=5 )
    editor_frame.grid( row=1, column=0 )
    editor = TkEditor( editor_frame )
    editor.set_text( default_txt )
    #editor.colorize_syntax_error( editor.text, "3.17" )
    root.mainloop()
    

