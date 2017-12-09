import tkinter as tk
from tkinter import font
from tkinter import ttk
import os

from mutagen.easyid3 import EasyID3
from pprint import pprint

from edit import edit
from search import search

import utilities
import codecs


class Manager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Music Manager")    # TODO: choose application name
        self.root.geometry("800x600")       # TODO: choose window size

        self.alive = True
        self.root.protocol('WM_DELETE_WINDOW', self.quit)

        self.default_font = font.nametofont("TkDefaultFont").configure(size=12)

        self.tag_list = ["title", "artist", "album", "tracknumber", "date"]
        self.tag_list_keys = ['#t', '#r', '#a', '#n', '#d']

        ### File Widget ###
        self.file_widget = ttk.Treeview(self.root)
        self.selected = None
        self.file_widget.heading("#0", text=os.path.abspath('Music'), anchor=tk.W)

        self.file_list = []
        self.file_tree = self.build_file_tree(os.path.abspath('Music'))

        ### Action Widget ###
        self.action_widget = ttk.Notebook(self.root)

        # Edit Tab
        self.metadata_tab = ttk.Frame(self.action_widget)
        self.action_widget.add(self.metadata_tab, text='Edit')
        self.tag_entries = {tag: ttk.Entry(self.metadata_tab, width=35) for tag in self.tag_list}
        for i, tag in enumerate(self.tag_list):
            ttk.Label(self.metadata_tab, text=tag.title()).grid(row=i, sticky=tk.W)
            self.tag_entries[tag].grid(row=i, column=1, sticky=tk.W)

        ttk.Button(self.metadata_tab, text="Save", command=self.save).grid(row=6, columnspan=2, sticky=tk.S)

        # Search Tab
        self.search_tab = ttk.Frame(self.action_widget)
        self.action_widget.add(self.search_tab, text='Search')

        self.search_entry = ttk.Entry(self.search_tab, font=("Arial", 12))
        self.search_entry.grid(row=0, column=0, columnspan=2)
        self.submit_button = ttk.Button(self.search_tab, text="go", command=self.search, width=3)
        self.submit_button.grid(row=0, column=2)

        tk.Label(self.search_tab, text="", width=60).grid(row=0, column=3)

        self.search_checkbutton_vars = {tag: tk.IntVar() for tag in self.tag_list}
        self.search_checkbuttons = {tag: tk.Checkbutton(self.search_tab, text=tag, variable=self.search_checkbutton_vars[tag]) for tag in self.tag_list}
        for i, checkbutton in enumerate(list(self.search_checkbuttons.values())[:3]):
            checkbutton.deselect()
            checkbutton.grid(row=1 + i, column=0, sticky=tk.W)
        for i, checkbutton in enumerate(list(self.search_checkbuttons.values())[3:]):
            checkbutton.deselect()
            checkbutton.grid(row=1 + i, column=1, sticky=tk.W)

        self.results_list = ttk.Treeview(self.search_tab)
        self.results_list.grid(row=4, column=0, columnspan=4, sticky=tk.W+tk.E+tk.N+tk.S)

        # Convert Tab
        self.convert_tab = ttk.Frame(self.action_widget)
        self.action_widget.add(self.convert_tab, text='Convert')
        self.filename_label = ttk.Label()

        # Pack widgets to root
        self.file_widget.pack(expand=1, side=tk.LEFT, fill="both")
        self.action_widget.pack(expand=1, side=tk.RIGHT, fill="both")

    def build_file_tree(self, top, parentid=""):
        tree = {top: []}
        for item in sorted(os.listdir(top), key=lambda x: x.split(".")[-1]):
            new_id = self.file_widget.insert(parentid, "end", text=item)
            item = os.path.join(top, item)
            # print(item)
            self.file_list.append((new_id, item))
            if os.path.isfile(item):
                tree[top].append(item)
            else:
                tree[top].append(self.build_file_tree(item, new_id))
        return tree

    def update_action_widget(self):
        item_tags = {"title": "", "artist": "", "album": "", "tracknumber": "", "date": ""}
        path = self.get_selected_filename()
        if path and os.path.isfile(path):
            item_tags = EasyID3(path)
            for tag in self.tag_list:
                try:
                    self.tag_entries[tag].delete(0, tk.END) #clears box
                    self.tag_entries[tag].insert(0, item_tags[tag][0]) #insert into box
                except:
                    pass
        elif path and os.path.isdir(path):
            for key, tag in zip(self.tag_list_keys, self.tag_list):
                self.tag_entries[tag].delete(0, tk.END)
                self.tag_entries[tag].insert(0, key)

    def get_selected_filename(self):
        if len(self.selected) == 1:
            for id, path in self.file_list:
                if id == self.selected[0]:
                    return path

    def save(self):
        print("saving!")
        # TODO: Mutagen code to actually write changes
        path = self.get_selected_filename()
        if path and os.path.isfile(path):
            for key in self.tag_list:
                edit(path, key, self.tag_entries[key].get())
        elif path and os.path.isdir(path):
            for file in utilities.walkMusicFiles(path):
                for key in self.tag_list:
                    edit(file, key, self.tag_entries[key].get())

    def search(self):
        self.results_list.delete(*self.results_list.get_children())
        keys = [tag for tag in self.tag_list if self.search_checkbutton_vars[tag].get()]
        results = search(self.search_entry.get(), keys, os.path.abspath('Music'))
        for result in results:
            self.results_list.insert("", "end", text=result.split("Music\\")[-1])

    def run(self):
        while self.alive:
            if self.file_widget.selection() != self.selected:
                self.selected = self.file_widget.selection()
                self.update_action_widget()
            self.root.update()

    def quit(self):
        self.alive = False
        self.root.destroy()


if __name__ == "__main__":
    manager = Manager()
    manager.run()
