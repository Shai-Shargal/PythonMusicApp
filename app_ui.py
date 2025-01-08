import tkinter as tk
import webbrowser
from tkinter import filedialog, ttk, messagebox
import pygame
from config import GENIUS_API_TOKEN
from app_logic import MusicLogic
from music_library import MusicLibrary
from song_finder import SongFinder
import os
from tkinterdnd2 import TkinterDnD, DND_FILES
import shutil
import requests
import io


class ImageTk:
    pass


class MusicApp:
    def __init__(self):
        self.volume_slider = None
        self.library = MusicLibrary()
        self.logic = MusicLogic()
        self.song_finder = SongFinder(GENIUS_API_TOKEN)

        self.root = TkinterDnD.Tk()  # Use TkinterDnD for drag-and-drop support
        self.root.title("Music Library")
        self.root.geometry("900x700")

        self.song_play_count = {}  # Track the play count of each song
        self.selected_folder = None

        self.setup_ui()
        self.enable_drag_and_drop()

    def setup_ui(self):
        # Header Label
        self.header_label = tk.Label(self.root, text="My Music Library", font=("Arial", 24))
        self.header_label.pack(pady=10)

        # Song Image Label
        self.song_image_label = tk.Label(self.root, text="No Image", bg="gray")
        self.song_image_label.pack(pady=10)

        # Song Treeview
        self.song_tree = ttk.Treeview(self.root, columns=("Title", "Duration", "Play Count"), show="headings", height=15)
        self.song_tree.heading("Title", text="Title")
        self.song_tree.heading("Duration", text="Duration")
        self.song_tree.heading("Play Count", text="Play Count")
        self.song_tree.column("Title", width=400)
        self.song_tree.column("Duration", width=100)
        self.song_tree.column("Play Count", width=100)
        self.song_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.song_tree.bind("<Double-1>", self.on_song_double_click)

        # Now Playing and Timer Frame
        now_playing_frame = tk.Frame(self.root, bg="black")
        now_playing_frame.pack(pady=5, padx=20, fill=tk.X)

        self.current_song_label = tk.Label(
            now_playing_frame,
            text="Now Playing: None",
            font=("Arial", 14),
            bg="black",
            fg="white",
            anchor="w"  # Align text to the left
        )
        self.current_song_label.pack(side=tk.LEFT, padx=10)

        self.time_label = tk.Label(
            now_playing_frame,
            text="00:00 / 00:00",
            font=("Arial", 14),
            bg="black",
            fg="white"
        )
        self.time_label.pack(side=tk.RIGHT, padx=10)

        # Control Buttons
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        for i, (text, command) in enumerate([
            ("Previous", self.previous_song),
            ("Play", self.play_song),
            ("Pause", self.pause_song),
            ("Stop", self.stop_song),
            ("Next", self.next_song),
            ("Shuffle", self.shuffle_playlist),
        ]):
            tk.Button(control_frame, text=text, command=command).grid(row=0, column=i, padx=5)

        # Bottom Buttons and Volume
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, pady=10)

        tk.Button(bottom_frame, text="Select Folder", command=self.select_folder).grid(row=0, column=0, padx=5)
        tk.Button(bottom_frame, text="Download Music", command=self.download_music).grid(row=0, column=1, padx=5)

        self.volume_slider = tk.Scale(bottom_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=self.set_volume)
        self.volume_slider.set(50)
        self.volume_slider.grid(row=0, column=2, padx=5)

        tk.Button(bottom_frame, text="Genius Search", command=self.search_lyrics).grid(row=0, column=3, padx=5)

    def update_song_image(self, image_url):
        """Update the song's artwork."""
        if not image_url:
            self.song_image_label.config(image=None, text="No Image", bg="gray")
            return

        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()

            img_data = response.content
            image = tk.Image.open(io.BytesIO(img_data))
            image = image.resize((150, 150))  # Resize to fit the label
            photo = ImageTk.PhotoImage(image)

            self.song_image_label.config(image=photo, text="")
            self.song_image_label.image = photo  # Keep reference to prevent garbage collection
        except Exception as e:
            print(f"Error loading image: {e}")
            self.song_image_label.config(image=None, text="No Image", bg="gray")

    def select_folder(self):
        """Allows the user to select a folder and load songs."""
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.selected_folder = folder_path
            songs = self.library.load_songs_from_folder(folder_path)
            if songs:
                self.logic.songs = songs
                self.update_song_list(songs)
            else:
                messagebox.showinfo("No Songs", "No songs found in the selected folder.")
        else:
            messagebox.showerror("Error", "No folder selected.")

    def update_song_list(self, songs):
        """Update the TreeView with the current playlist."""
        self.song_tree.delete(*self.song_tree.get_children())  # Clear the treeview
        for song in songs:
            title = os.path.basename(song)
            duration = self.logic.get_song_duration(song)  # MM:SS format
            play_count = self.song_play_count.get(song, 0)
            self.song_tree.insert("", tk.END, values=(title, duration, play_count))

    def play_song(self):
        selection = self.song_tree.selection()
        if selection:
            self.logic.current_song_index = int(self.song_tree.index(selection[0]))
            song_path = self.logic.songs[self.logic.current_song_index]

            if song_path not in self.song_play_count:
                self.song_play_count[song_path] = 0

            self.logic.play_song(song_path)

            current_song_title = os.path.basename(song_path)
            self.current_song_label.config(text=f"Now Playing: {current_song_title}")

            try:
                song_info = self.song_finder.search_song(current_song_title)
                if song_info and "art_image_url" in song_info[0]:
                    self.update_song_image(song_info[0]["art_image_url"])
                else:
                    self.update_song_image(None)  # No image found
            except Exception as e:
                print(f"Error fetching song image: {e}")
                self.update_song_image(None)

            self.update_timer()

    def pause_song(self):
        self.logic.pause_song()

    def stop_song(self):
        self.logic.stop_song()
        self.time_label.config(text="00:00 / 00:00")

    def next_song(self):
        if self.logic.songs:
            self.logic.next_song()
            current_song_path = self.logic.songs[self.logic.current_song_index]
            current_song_title = os.path.basename(current_song_path)
            self.current_song_label.config(text=f"Now Playing: {current_song_title}")
            self.update_timer()

    def previous_song(self):
        self.logic.previous_song()
        self.update_timer()

    def shuffle_playlist(self):
        self.logic.shuffle_playlist()
        self.update_song_list(self.logic.songs)

    def set_volume(self, volume):
        self.logic.set_volume(volume)

    def download_music(self):
        if not self.selected_folder:
            messagebox.showerror("Error", "Please select a folder first.")
            return
        webbrowser.open("https://y2mate.nu/en-9le1/")
        messagebox.showinfo("Info", f"Downloaded music will be saved to:\n{self.selected_folder}")

    def search_lyrics(self):
        lyrics_snippet = tk.simpledialog.askstring("Search Lyrics", "Enter lyrics snippet:")
        if not lyrics_snippet:
            messagebox.showerror("Error", "Please enter lyrics to search.")
            return

        results = self.song_finder.search_song(lyrics_snippet)
        if results:
            # Create a new Toplevel window for better display
            result_window = tk.Toplevel(self.root)
            result_window.title("Genius Search Results")
            result_window.geometry("600x400")

            # Add a scrollable Text widget to display results
            text_widget = tk.Text(result_window, wrap=tk.WORD, font=("Arial", 12))
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            scrollbar = tk.Scrollbar(text_widget, command=text_widget.yview)
            text_widget.config(yscrollcommand=scrollbar.set)

            # Display each result in a better format
            for i, song in enumerate(results):
                text_widget.insert(tk.END, f"{i + 1}. {song['title']} by {song['artist']}\n")
                text_widget.insert(tk.END, f"URL: {song['url']}\n\n")

            text_widget.config(state=tk.DISABLED)  # Make the text read-only
        else:
            messagebox.showinfo("No Songs Found", "No songs matched your lyrics snippet.")

    def on_song_double_click(self, event):
        self.play_song()

    def update_timer(self):
        """Update the timer, handle song end, and trigger next song."""
        if self.logic.timer_running:
            current_time_ms = self.logic.get_current_time()
            self.logic.current_time = int(current_time_ms / 1000)

            mins, secs = divmod(self.logic.current_time, 60)
            total_mins, total_secs = divmod(int(self.logic.song_length), 60)
            self.time_label.config(text=f"{mins:02}:{secs:02} / {total_mins:02}:{total_secs:02}")

            if not pygame.mixer.music.get_busy():
                self.logic.timer_running = False
                current_song = self.logic.songs[self.logic.current_song_index]
                self.song_play_count[current_song] += 1
                self.update_song_list(self.logic.songs)
                self.next_song()
            else:
                self.root.after(1000, self.update_timer)

    def enable_drag_and_drop(self):
        """Enable drag-and-drop for MP3 files."""
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.handle_file_drop)

    def handle_file_drop(self, event):
        """Handle dropped MP3 files and copy them to the selected folder."""
        if not self.selected_folder:
            messagebox.showerror("Error", "Please select a folder before dragging and dropping files.")
            return

        dropped_files = self.root.tk.splitlist(event.data)  # Get the list of dropped files
        added_files = 0

        for file in dropped_files:
            if file.lower().endswith('.mp3'):
                destination_path = os.path.join(self.selected_folder, os.path.basename(file))

                try:
                    if not os.path.exists(destination_path):
                        shutil.copy(file, destination_path)
                        print(f"Copied {file} to {destination_path}")
                    else:
                        print(f"{file} already exists in {self.selected_folder}")

                    if destination_path not in self.logic.songs:
                        self.logic.songs.append(destination_path)
                        self.song_play_count[destination_path] = 0
                        added_files += 1
                except Exception as e:
                    print(f"Error copying {file} to {destination_path}: {e}")

        if added_files:
            self.update_song_list(self.logic.songs)
            print(f"Added {added_files} MP3 file(s) to the playlist.")
        else:
            print("No new MP3 files were added.")

    def run(self):
        self.root.mainloop()
