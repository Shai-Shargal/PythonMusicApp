import os
from pygame import mixer


class MusicLibrary:
    def __init__(self):
        self.songs = []

    def load_songs_from_folder(self, folder_path):
        """
        Loads all the MP3 files from the specified folder into the music library.
        """
        self.songs = []
        if not os.path.exists(folder_path):
            print(f"Folder path '{folder_path}' does not exist.")
            return []

        for file in os.listdir(folder_path):
            if file.endswith(".mp3"):
                full_path = os.path.join(folder_path, file)
                self.songs.append(full_path)

        return self.songs

    def get_song_duration(self, song_path):
        """
        Get the duration of a song in the given path.

        Parameters:
        - song_path (str): The full path to the song file.

        Returns:
        - str: The formatted duration in "MM:SS".
        """
        try:
            mixer.init()
            mixer.music.load(song_path)
            duration_sec = mixer.Sound(song_path).get_length()
            minutes = int(duration_sec // 60)
            seconds = int(duration_sec % 60)
            return f"{minutes:02}:{seconds:02}"
        except Exception as e:
            print(f"Error getting song duration: {e}")
            return "00:00"
