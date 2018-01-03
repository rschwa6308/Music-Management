import os
import tkinter as tk
from tkinter import font
from tkinter import ttk

import mutagen
import pygame.mixer
from PIL import Image, ImageTk
from time import sleep
import datetime

from Helpers.covert import *
from Helpers.edit import *
from Helpers.search import *


class Manager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Music Manager")  # TODO: choose application name
        self.root.geometry("1100x800")  # TODO: choose window size

        self.alive = True
        self.root.protocol('WM_DELETE_WINDOW', self.quit)

        self.default_font = font.nametofont("TkDefaultFont").configure(size=12)

        s = ttk.Style()
        s.theme_use('clam')

        self.tag_list = ["title", "artist", "album", "tracknumber", "date"]
        self.tag_list_keys = ['#t', '#r', '#a', '#n', '#d']

        ### File Widget ###
        self.library = "E:\\Music"

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
        self.current_song = None
        self.queue_index = 0
        self.queued_song = None

        # self.album_art = ImageTk.PhotoImage(Image.open("Assets/musical notes.png"))
        self.play_image = ImageTk.PhotoImage(Image.open("Assets/play.png"))
        self.pause_image = ImageTk.PhotoImage(Image.open("Assets/pause.png"))
        self.back_image = ImageTk.PhotoImage(Image.open("Assets/previous.png"))
        self.next_image = ImageTk.PhotoImage(Image.open("Assets/next.png"))

        # self.album_art_label = ttk.Label(self.play_tab, image=self.album_art)
        # self.album_art_label.pack() # grid(row=0, column=0, columnspan=3)
        self.song_queue = ttk.Treeview(self.play_tab, height=10, selectmode="browse", show="tree")
        self.song_queue.column("#0", stretch=True)
        self.song_queue.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        self.title_label = ttk.Label(self.play_tab, font=("Helvetica", 18))
        self.title_label.pack(pady=15)

        # TODO: make into ttk buttons (needs custom theme to disable border)
        song_button_frame = ttk.Frame(self.play_tab)
        self.back_button = tk.Button(song_button_frame, image=self.back_image, bd=0, command=self.back_song)
        self.back_button.pack(side=tk.LEFT)
        self.play_button = tk.Button(song_button_frame, image=self.play_image, bd=0, command=self.play_toggle)
        self.play_button.pack(side=tk.LEFT)
        self.next_button = tk.Button(song_button_frame, image=self.next_image, bd=0, command=self.next_song)
        self.next_button.pack(side=tk.LEFT)
        song_button_frame.pack(pady=10)

        progress_frame = ttk.Frame(self.play_tab)
        # s.configure("blue.Horizontal.TProgressbar", foreground='blue', background='blue')
        self.progressbar = ttk.Progressbar(progress_frame, orient="horizontal", length=500, mode="determinate") # , style="blue.Horizontal.TProgressbar")
        self.progressbar.grid(row=0, column=0, columnspan=3)
        self.song_pos_label = ttk.Label(progress_frame, text="0:00")
        self.song_pos_label.grid(row=1, column=0, sticky=tk.W)
        self.song_length_label = ttk.Label(progress_frame, text="0:00")
        self.song_length_label.grid(row=1, column=2, sticky=tk.E)
        progress_frame.pack(pady=15)

        # Search Tab
        self.search_tab = ttk.Frame(self.action_widget)
        self.action_widget.add(self.search_tab, text='Search')

        search_entry_frame = ttk.Frame(self.search_tab)
        self.search_entry = ttk.Entry(search_entry_frame, font=("Arial", 12))
        self.search_entry.grid(row=0, column=0, columnspan=2)
        self.submit_button = ttk.Button(search_entry_frame, text="go", command=self.search, width=3)
        self.submit_button.grid(row=0, column=2)

        ttk.Label(search_entry_frame, text="", width=60).grid(row=0, column=3)

        self.search_checkbutton_vars = {tag: tk.IntVar() for tag in self.tag_list}
        self.search_checkbuttons = {
            tag: tk.Checkbutton(search_entry_frame, text=tag, variable=self.search_checkbutton_vars[tag]) for tag in
            self.tag_list}
        for i, checkbutton in enumerate(list(self.search_checkbuttons.values())[:3]):
            checkbutton.deselect()
            checkbutton.grid(row=1 + i, column=0, sticky=tk.W)
        for i, checkbutton in enumerate(list(self.search_checkbuttons.values())[3:]):
            checkbutton.deselect()
            checkbutton.grid(row=1 + i, column=1, sticky=tk.W)
        search_entry_frame.pack()

        self.results_list = ttk.Treeview(self.search_tab)
        self.results_list.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)

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
        self.filename_label = ttk.Label(self.convert_tab)
        self.filename_label.grid(row=0, column=0, columnspan=10, sticky=tk.W)
        ttk.Label(self.convert_tab, text="Convert to: ").grid(row=1, column=0)
        self.filetype_entry = ttk.Combobox(self.convert_tab, values=[".mp3", ".wav"])
        self.filetype_entry.grid(row=1, column=1)
        ttk.Button(self.convert_tab, text="go", width=8, command=self.convert).grid(row=2, column=0, columnspan=2)

        # Playlist Tab
        self.playlist_tab = ttk.Frame(self.action_widget)
        self.action_widget.add(self.playlist_tab, text='Playlists')

        # Pack widgets to root
        self.file_widget.pack(expand=True, side=tk.LEFT, fill="both")
        self.action_widget.pack(expand=False, side=tk.RIGHT, fill="both")

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

        if path:
            # print(self.get_selected_filename().split("\\")[-1])
            self.filename_label["text"] = self.get_selected_filename().split("\\")[-1]

        # Play Tab
        # update song queue
        self.song_queue.delete(*self.song_queue.get_children())
        for item in self.file_widget.selection():
            if os.path.isfile(self.get_filename(item)):
                if item not in self.song_queue.get_children():
                    self.song_queue.insert("", "end", text=self.file_widget.item(item, option="text"), iid=item)
            else:
                for child in self.file_widget.get_children(item):
                    self.song_queue.insert("", "end", text=self.file_widget.item(child, option="text"), iid=child)

        if len(self.song_queue.get_children()) > 0:
            # highlight item item dictated by the queue index
            if self.queue_index >= len(self.song_queue.get_children()):
                self.queue_index = 0
            current_item = self.song_queue.get_children()[self.queue_index]
            self.song_queue.selection_set(current_item)

        # toggle play/pause image
        path = self.get_queued_filename()
        if self.playing:
            self.play_button["image"] = self.pause_image
        else:
            self.play_button["image"] = self.play_image

        # disables play button when queue is empty
        if not self.playing:
            if path:
                self.play_button["state"] = "normal"
                self.back_button["state"] = "normal"
                self.next_button["state"] = "normal"
            else:
                self.play_button["state"] = "disabled"
                self.back_button["state"] = "disabled"
                self.next_button["state"] = "disabled"

        # disables << and >> buttons at start and end of queue TODO: consider wrapping
        if path:
            if self.queue_index == 0:
                self.back_button["state"] = "disabled"
            else:
                self.back_button["state"] = "normal"

            if self.queue_index == len(self.song_queue.get_children()) - 1:
                self.next_button["state"] = "disabled"
            else:
                self.next_button["state"] = "normal"

        # update song info label and progress bar max length
        if path:
            if os.path.isfile(path):
                try:
                    item_tags = EasyID3(path)
                    length = round(mutagen.File(path).info.length)
                    self.progressbar["maximum"] = length
                    m, s = divmod(length, 60)
                    if s < 10:
                        s = "0" + str(s)
                    self.song_length_label["text"] = "{0}:{1}".format(m, s)
                except:
                    pass
            try:
                self.title_label["text"] = "\"" + item_tags["title"][0] + "\"" + ", by " + item_tags["artist"][0]
            except:
                pass
        else:
            self.title_label["text"] = ""

    def get_filename(self, iid):
        for id, path in self.file_list:
            if id == iid:
                return path

    def get_selected_filename(self):
        if len(self.selected) == 1:
            for id, path in self.file_list:
                if id == self.selected[0]:
                    return path

    def get_queued_filename(self):
        if len(self.song_queue.get_children()) == 0:
            return None
        item = self.song_queue.selection()[0] # self.song_queue.get_children()[self.queue_index]
        return self.get_filename(item)

    def play_toggle(self):
        if self.playing:
            pygame.mixer.music.pause()
        else:
            path = self.get_queued_filename()
            if path:
                if self.current_song == path:
                    pygame.mixer.music.unpause()
                else:
                    try:
                        pygame.mixer.music.load(path)
                        pygame.mixer.music.play()
                        self.current_song = path
                        # self.progressbar["value"] = 0
                    except:
                        pass

        self.playing = not self.playing
        self.update_action_widget()

    def back_song(self):
        self.play_toggle()
        self.queue_index -= 1
        self.update_action_widget()
        self.play_toggle()

    def next_song(self):
        self.play_toggle()
        self.queue_index += 1
        self.update_action_widget()
        self.play_toggle()

    def stop(self):
        self.playing = False
        pygame.mixer.music.stop()
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
        period = 1.0 / 60.0     # 60 fps
        while self.alive:
            sleep(period)
            if self.playing:
                # change song when finished
                if not pygame.mixer.music.get_busy():
                    print("song over")
                    if self.queue_index < len(self.song_queue.get_children()) - 1:
                        self.next_song()
                    else:
                        pygame.mixer.music.stop()
                        self.stop()
                # update progressbar
                else:
                    pos = pygame.mixer.music.get_pos() / 1000
                    self.progressbar["value"] = pos
                    m, s = divmod(round(pos), 60)
                    if s < 10:
                        s = "0" + str(s)
                    self.song_pos_label["text"] = "{0}:{1}".format(m, s)
            # update GUI when needed
            if self.file_widget.selection() != self.selected or self.queued_song != self.get_queued_filename():
                # print("update")
                self.selected = self.file_widget.selection()
                self.queued_song = self.get_queued_filename()
                if len(self.song_queue.get_children()) != 0:
                    self.queue_index = self.song_queue.get_children().index(self.song_queue.selection()[0])
                self.update_action_widget()
            self.root.update()

    def quit(self):
        self.alive = False
        self.root.destroy()


if __name__ == "__main__":
    manager = Manager()
    manager.run()
