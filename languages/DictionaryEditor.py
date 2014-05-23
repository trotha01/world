#!/usr/bin/python
""" A Gui for creating and editing the language dictionaries for audio files """
import sys
sys.path.insert(0, '../sound/')

from gi.repository import Gtk
from os.path import expanduser
import imp
import play

# For debugging
import logging

HOME = expanduser("~")
WORLD = expanduser("~/Documents/try/python/pygame/world")
AUDIO_DIR = '../sound/'

# TODO: use current directory

def add_filters(dialog):
    """ Filters file search """
    # TODO: only search for .ogg files

    filter_text = Gtk.FileFilter()
    filter_text.set_name("Text files")
    filter_text.add_mime_type("text/plain")
    # dialog.add_filter(filter_text)

    filter_py = Gtk.FileFilter()
    filter_py.set_name("Python files")
    filter_py.add_mime_type("text/x-python")
    # dialog.add_filter(filter_py)

    filter_any = Gtk.FileFilter()
    filter_any.set_name("Any files")
    filter_any.add_pattern("*")
    dialog.add_filter(filter_any)

def file_dialog(window):
    """ Opens dialog for file selection """
    filename = None

    dialog = Gtk.FileChooserDialog("Please choose a file", window,
        Gtk.FileChooserAction.OPEN,
        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
         Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
    dialog.set_current_folder(WORLD)

    add_filters(dialog)

    response = dialog.run()
    if response == Gtk.ResponseType.OK:
        filename = dialog.get_filename()
        print "File selected: " + filename

    elif response == Gtk.ResponseType.CANCEL:
        print "Cancel clicked"

    dialog.destroy()
    return filename

class GridRow(object):
    """ A specified row on a grid """

    def __init__(self, grid, row):
        self.grid    = None
        self.row     = None
        self.col     = 0
        self.widgets = []
        self.grid    = grid
        self.row     = row

    def destroy(self, widget=None):
        """ Destroys all widgets in the row """
        for widget in self.widgets:
            widget.destroy()

    def append(self, widget):
        """ Append a widget to the row """
        self.widgets.append(widget)
        self.grid.attach(widget, self.col, self.row, 1, 1)
        self.col += 1

class DictionaryWordRow(GridRow):
    """ A translate row for audio file """
    def __init__(self, block, row):
        self.block = block
        GridRow.__init__(self, block.grid, row)

        # Text boxes for user input
        self.start       = Gtk.Entry()
        self.length      = Gtk.Entry()
        self.word        = Gtk.Entry()
        self.translation = Gtk.Entry()

        # Buttons for audio control
        play_button = Gtk.Button("Play")
        stop_button = Gtk.Button("Stop")
        play_button.connect("clicked", self.play_audio)
        stop_button.connect("clicked", self.stop_audio)
        # Button for row deletion
        del_button = Gtk.Button("-")
        del_button.connect("clicked", self.destroy)

        # Add all widgets to row
        self.append(del_button       ) 
        self.append(self.start       ) 
        self.append(self.length      ) 
        self.append(self.word        ) 
        self.append(self.translation ) 
        self.append(play_button      ) 
        self.append(stop_button      ) 

    def play_audio(self, widget):
        """ Plays a portion of the audio file """
        _ = widget
        start  = self.start. get_text()
        length = self.length.get_text()
        self.block.play_audio(start, length)

    def stop_audio(self, widget):
        """ Stops playingthe audio file """
        pass

class DictionaryAudioBlock(object):
    """ A translate grid for audio file """

    def __init__(self, container, translate_window, block_id):
        self.grid       = Gtk.Grid()
        self.container  = container 
        self.tr_window = translate_window
        self.block_id   = block_id
        self.audio_file = None
        self.row_count  = 0
        self.info_rows  = []

        # Add block buttons and labels
        self._top_row_buttons()
        self._label_row()

        # Add a couple blank rows
        self.add_info_row(None)
        self.add_info_row(None)

        # Add grid to container
        container.pack_start(self.grid, True, True, 0)

    def _top_row_buttons(self):
        """ Adds audio add/delete block buttons """
        # Audio file button
        file_button = Gtk.Button("Choose Audio File")
        file_button.connect("clicked", self.load_audio_file)
        self.grid.attach(file_button, 0, self.row_count, 1, 1)

        # Button to add more rows
        plus_button = Gtk.Button("Add Row")
        plus_button.connect("clicked", self.add_info_row)
        self.grid.attach(plus_button, 1, self.row_count, 1, 1)

        # Button to delete block
        del_button = Gtk.Button("Delete Block")
        del_button.connect("clicked", self.destroy)
        self.grid.attach(del_button, 2, self.row_count, 1, 1)

        self.row_count += 1

    def _label_row(self):
        """ Adds info labels """
        label_row    = GridRow(self.grid, self.row_count)

        del_label    = Gtk.Label("Delete")
        start_label  = Gtk.Label("Start")
        length_label = Gtk.Label("Length")
        word_label   = Gtk.Label("Word")
        transl_label = Gtk.Label("Translation")

        label_row.append( del_label    ) 
        label_row.append( start_label  ) 
        label_row.append( length_label ) 
        label_row.append( word_label   ) 
        label_row.append( transl_label ) 

        self.row_count += 1

    def __str__(self):
        dict_str = ""
        if self.audio_file is None:
            return dict_str
        for row in self.info_rows:
            dict_str += "'"
            dict_str += row.word.get_text()
            dict_str += "' : {'audiofile': '"
            dict_str += self.audio_file.get_text()
            dict_str += "',\n"
            dict_str += "'start':"
            dict_str += row.start.get_text()
            dict_str += ", 'length':"
            dict_str += row.length.get_text()
            dict_str += ",\n"
            dict_str += "'word': '"
            dict_str += row.translation.get_text()
            dict_str += "'},\n"


            #row.word.get_text()
        return  dict_str

    def _destroy_rows(self):
        """ Destroy all info rows in block """
        # Remove all info rows
        for row in self.info_rows:
            row.destroy()
            self.row_count -= 1
        self.info_rows = []

    def import_words(self, translations, audio_file):
        """ Imports a translation dictionary, and fills in boxes """
        self._use_audio_file(audio_file)

        self._destroy_rows()

        for word in translations:
            row = self.add_info_row(None)
            row.word.       set_text(word)
            row.start.      set_text(str(translations[word]['start' ]))
            row.length.     set_text(str(translations[word]['length']))
            row.translation.set_text(translations[word]['word'  ])

    def is_savable(self):
        """ Call to check for errors before saving """
        # Check audio file exists
        # Check no empty cells
        pass
    # TODO: save_as, need a name to save file

    def save_dictionary(self, widget):
        """ Creates a translation dictionary from the filled out boxes """
        _ = widget
        d_file = open("dictionary.py", "wb")

        d_file.write('""" Spanish dictionary with audio clip locations """\n')
        d_file.write("TRANSLATE = {\n")
        for row in self.info_rows:
            d_file.write("'" + 
                    row.word.get_text() +
                    "' : {'audiofile': '" +
                    self.audio_file.get_text() + "',\n")
            d_file.write("'start':"+
                    row.start.get_text()+
                    ", 'length':"+
                    row.length.get_text()+
                    ",\n")
            d_file.write("'word': '"+
                    row.translation.get_text() +
                    "'},\n")

        d_file.write("}\n")

    def add_info_row(self, widget):
        """ Adds an info play/pause row to the grid """
        _ = widget
        twr = DictionaryWordRow(self, self.row_count)
        self.info_rows.append(twr)
        self.grid.show_all()
        self.row_count += 1
        return twr

    def play_audio(self, start, length):
        """ Plays audio file starting at 'start' for 'length' seconds """
        if self.audio_file is not None:
            play.play_audio(self.audio_file.get_text(), start, length)

    def _use_audio_file(self, audio_file):
        """ Sets the audio file for this Dictionary Block """
        if self.audio_file is None:
            audio_label = Gtk.Label()
            audio_label.set_text(audio_file)
            self.grid.attach(audio_label  , 3 , 0, 3 , 2)
            self.grid.show_all()
        else:
            self.audio_file.set_text(audio_file)

        self.audio_file = audio_label

    def load_audio_file(self, widget):
        """ Handles file finding """
        _ = widget

        filename = file_dialog(self.tr_window.window)
        if filename is not None:
            self._use_audio_file(filename)

    def destroy(self, widget):
        """ Remove all info rows """
        _ = widget
        self.tr_window.rem_block(self.block_id)
        self.grid.destroy()

class DictionaryEditorWindow(object):
    """ Main window for all audio translation widgets """
    def __init__(self):
        self.window          = None
        self.vbox            = None
        self.dictionary_file = ""
        # Container to hold all audio translation blocks
        self.blocks = []

        # Initialize window
        self.window = Gtk.Window()
        self.window.set_title('Dictionary Editor')
        # Add quit to window
        self.window.connect("delete-event", Gtk.main_quit)

        # Create vertical box container
        self.vbox = Gtk.VBox()

        # Add top buttons (load/save)
        self.top_row_buttons()

        # Add some translation blocks to vertical box
        self.add_block()
        self.add_block()

        # Add vertical box to window
        self.window.add(self.vbox)

        # Show window
        self.window.show_all()
        Gtk.main()

    def top_row_buttons(self):
        """ Add top row buttons to the window """
        # Container for load/save/add buttons
        ls_container = Gtk.Box()

        # Import dictionary button
        import_button = Gtk.Button("Import dictionary")
        import_button.connect("clicked", self.import_dictionary)
        # Save dictionary button
        create_button = Gtk.Button("Save dictionary")
        create_button.connect("clicked", self.save_dictionary)
        # Button to add block
        add_button = Gtk.Button("Add Block")
        add_button.connect("clicked", self.add_block)

        # add buttons to load/save/add container
        ls_container.add(import_button)
        ls_container.add(create_button)
        ls_container.add(add_button   )
        # add load/save container to vertical box
        self.vbox.add(ls_container)

    def import_dictionary(self, widget):
        """ Imports dictionary from a file """
        _ = widget
        dictionary_file = file_dialog(self.window)
        trl = imp.load_source('dict', dictionary_file)
        translations = trl.TRANSLATE

        # Separate 'translations' by audio file
        audio_files = []
        translation_values = translations.values()
        for value in translation_values:
            audio_files.append(value['audiofile'])
        audio_files = set(audio_files)

        max_blocks = len(self.blocks)
        block = 0
        for audio_file in audio_files:
            # Create new dictionary with words that use the audio_file
            d = dict((k, v) for k, v in translations.iteritems() if v['audiofile'] == audio_file)
            # Import into a specific block
            self.blocks[block].import_words(d, AUDIO_DIR + audio_file)
            block += 1
            if block >= max_blocks:
                self.add_block()

    def save_dictionary(self, widget):
        """ Saves the dictionary to file """
        _ = widget

        dict_str = '""" Translations with audio clip locations """\n'
        dict_str += "TRANSLATE = {\n"

        for block in self.blocks:
            dict_str += str(block)

        dict_str += "}"

        print "File saved"
        d_file = open("dictionary.py", "wb")
        d_file.write(dict_str)

    def add_block(self, widget=None):
        """ Adds a block for a single audio file to the window """
        _ = widget
        self.blocks.append(
                DictionaryAudioBlock(self.vbox, self, len(self.blocks)))

    def rem_block(self, block_id):
        """ Removes a block for a single audio file to the window """
        # TODO: look-up a better way to do this
        self.blocks.remove(self.blocks[block_id])


if __name__ == "__main__":
    # For debugging
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    # init audio methods
    play.play_init()

    DictionaryEditorWindow()
