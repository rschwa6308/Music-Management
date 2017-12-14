import tkinter as tk
from tkinter import font
from tkinter import ttk
import os
import pygame.mixer
from mutagen.easyid3 import EasyID3
from PIL import Image, ImageTk

from edit import edit
from search import search
from covert import convert
import utilities


class Manager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Music Manager")  # TODO: choose application name
        self.root.geometry("1100x800")  # TODO: choose window size

        self.alive = True
        self.root.protocol('WM_DELETE_WINDOW', self.quit)

        self.default_font = font.nametofont("TkDefaultFont").configure(size=12)

        self.tag_list = ["title", "artist", "album", "tracknumber", "date"]
        self.tag_list_keys = ['#t', '#r', '#a', '#n', '#d']

        ### File Widget ###
        self.library = "E:\Music"

        self.file_widget = ttk.Treeview(self.root)
        self.selected = None
        self.file_widget.heading("#0", text=self.library, anchor=tk.W)

        self.file_list = []
        self.file_tree = self.build_file_tree(self.library)

        ### Action Widget ###
        self.action_widget = ttk.Notebook(self.root)

        # Play Tab
        self.play_tab = ttk.Frame(self.action_widget)
        self.action_widget.add(self.play_tab, text='Play')

        pygame.mixer.init()  # initialize music mixer
        self.playing = False

        self.album_art = ImageTk.PhotoImage(Image.open("Assets/musical notes.png"))
        self.play_image = ImageTk.PhotoImage(Image.open("Assets/play.png"))
        self.pause_image = ImageTk.PhotoImage(Image.open("Assets/pause.png"))

        self.album_art_label = ttk.Label(self.play_tab, image=self.album_art)
        self.album_art_label.pack() # grid(row=0, column=0, columnspan=3)
        self.title_label = ttk.Label(self.play_tab, font=("Helvetica", 18))
        self.title_label.pack()
        self.play_button = tk.Button(self.play_tab, image=self.play_image, bd=0, command=self.play_toggle)
        self.play_button.pack() # grid(row=1, column=1)

        # Search Tab
        self.search_tab = ttk.Frame(self.action_widget)
        self.action_widget.add(self.search_tab, text='Search')

        self.search_entry = ttk.Entry(self.search_tab, font=("Arial", 12))
        self.search_entry.grid(row=0, column=0, columnspan=2)
        self.submit_button = ttk.Button(self.search_tab, text="go", command=self.search, width=3)
        self.submit_button.grid(row=0, column=2)

        tk.Label(self.search_tab, text="", width=60).grid(row=0, column=3)

        self.search_checkbutton_vars = {tag: tk.IntVar() for tag in self.tag_list}
        self.search_checkbuttons = {
            tag: tk.Checkbutton(self.search_tab, text=tag, variable=self.search_checkbutton_vars[tag]) for tag in
            self.tag_list}
        for i, checkbutton in enumerate(list(self.search_checkbuttons.values())[:3]):
            checkbutton.deselect()
            checkbutton.grid(row=1 + i, column=0, sticky=tk.W)
        for i, checkbutton in enumerate(list(self.search_checkbuttons.values())[3:]):
            checkbutton.deselect()
            checkbutton.grid(row=1 + i, column=1, sticky=tk.W)

        self.results_list = ttk.Treeview(self.search_tab)
        self.results_list.grid(row=4, column=0, columnspan=4, sticky=tk.W + tk.E + tk.N + tk.S)

        # Edit Tab
        self.metadata_tab = ttk.Frame(self.action_widget)
        self.action_widget.add(self.metadata_tab, text='Edit')
        self.tag_entries = {tag: ttk.Entry(self.metadata_tab, width=35) for tag in self.tag_list}
        for i, tag in enumerate(self.tag_list):
            ttk.Label(self.metadata_tab, text=tag.title()).grid(row=i, sticky=tk.W)
            self.tag_entries[tag].grid(row=i, column=1, sticky=tk.W)

        ttk.Button(self.metadata_tab, text="Save", command=self.save).grid(row=6, columnspan=2, sticky=tk.S)

        # Convert Tab
        self.convert_tab = ttk.Frame(self.action_widget)
        self.action_widget.add(self.convert_tab, text='Convert')
        self.filename_label = tk.Label(self.convert_tab)
        self.filename_label.grid(row=0, column=0, columnspan=10, sticky=tk.W)
        tk.Label(self.convert_tab, text="Convert to: ").grid(row=1, column=0)
        self.filetype_entry = ttk.Combobox(self.convert_tab, values=[".mp3", ".wav"])
        self.filetype_entry.grid(row=1, column=1)
        ttk.Button(self.convert_tab, text="go", width=8, command=self.convert).grid(row=2, column=0, columnspan=2)

        # Playlist Tab
        self.playlist_tab = ttk.Frame(self.action_widget)
        self.action_widget.add(self.playlist_tab, text='Playlists')

        # Pack widgets to root
        self.file_widget.pack(expand=1, side=tk.LEFT, fill="both")
        self.action_widget.pack(expand=0, side=tk.RIGHT, fill="both")

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
        # Edit Tab
        item_tags = {"title": "", "artist": "", "album": "", "tracknumber": "", "date": ""}
        path = self.get_selected_filename()
        if path and os.path.isfile(path):
            try:
                item_tags = EasyID3(path)
            except:
                pass
            for tag in self.tag_list:
                try:
                    self.tag_entries[tag].delete(0, tk.END)  # clears box
                    self.tag_entries[tag].insert(0, item_tags[tag][0])  # insert into box
                except:
                    pass
        elif path and os.path.isdir(path):
            for key, tag in zip(self.tag_list_keys, self.tag_list):
                try:
                    self.tag_entries[tag].delete(0, tk.END)
                    self.tag_entries[tag].insert(0, key)
                except:
                    pass

        if self.selected:
            # print(self.get_selected_filename().split("\\")[-1])
            self.filename_label["text"] = self.get_selected_filename().split("\\")[-1]

        # Play Tab
        if self.playing:
            self.play_button["image"] = self.pause_image
        else:
            self.play_button["image"] = self.play_image

        if not self.playing:
            if path:
                self.play_button["state"] = "normal"
            else:
                self.play_button["state"] = "disabled"

        if path:
            try:
                self.title_label["text"] = "\"" + item_tags["title"][0] + "\"" + ", by " + item_tags["artist"][0]
            except:
                pass
        else:
            self.title_label["text"] = ""


    def get_selected_filename(self):
        if len(self.selected) == 1:
            for id, path in self.file_list:
                if id == self.selected[0]:
                    return path

    def play_toggle(self):
        path = self.get_selected_filename()
        if path:
            if self.playing:
                pygame.mixer.music.pause()
            else:
                if os.path.isfile(path):
                    pygame.mixer.music.load(path)
                    pygame.mixer.music.play()
                elif os.path.isdir(path):
                    pass
            self.playing = not self.playing
            self.update_action_widget()

    def save(self):
        # print("saving!")
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
        results = search(self.search_entry.get(), keys, self.library)
        for result in results:
            self.results_list.insert("", "end", text=result.split(self.library + "\\")[-1])

    def convert(self):
        convert(self.get_selected_filename(), self.filetype_entry.get())

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
