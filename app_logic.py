import pygame
import random


class MusicLogic:
    def __init__(self):
        pygame.mixer.init()
        self.songs = []
        self.current_song_index = -1
        self.current_time = 0
        self.song_length = 0
        self.timer_running = False

    def load_song(self, song_path):
        """Load a song into the mixer and update its length."""
        try:
            pygame.mixer.music.load(song_path)
            self.song_length = pygame.mixer.Sound(song_path).get_length()
        except Exception as e:
            print(f"Error loading song {song_path}: {e}")
            self.song_length = 0

    def play_song(self, song_path):
        """Play the selected song."""
        self.load_song(song_path)
        pygame.mixer.music.play()
        self.timer_running = True

    def pause_song(self):
        """Pause the currently playing song."""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.timer_running = False

    def stop_song(self):
        """Stop the currently playing song."""
        pygame.mixer.music.stop()
        self.timer_running = False
        self.current_time = 0

    def next_song(self):
        """Play the next song in the playlist."""
        if self.songs:
            self.current_song_index = (self.current_song_index + 1) % len(self.songs)
            self.play_song(self.songs[self.current_song_index])

    def previous_song(self):
        """Play the previous song in the playlist."""
        if self.songs:
            self.current_song_index = (self.current_song_index - 1) % len(self.songs)
            self.play_song(self.songs[self.current_song_index])

    def shuffle_playlist(self):
        """Shuffle the playlist."""
        random.shuffle(self.songs)
        self.current_song_index = 0  # Reset to the first song after shuffling

    def set_volume(self, volume):
        """Set the volume of the music player."""
        pygame.mixer.music.set_volume(float(volume) / 100)

    def get_current_time(self):
        """Get the current playback position in milliseconds."""
        return pygame.mixer.music.get_pos()

    def seek_to(self, new_time):
        """Seek to a specific position in the song."""
        pygame.mixer.music.stop()
        pygame.mixer.music.play(start=new_time / 1000.0)  # Convert to seconds

    def get_song_duration(self, song_path):
        """Get song duration in MM:SS format."""
        try:
            song_length = self.load_song_length(song_path)
            minutes = int(song_length) // 60
            seconds = int(song_length) % 60
            return f"{minutes}:{seconds:02}"  # Format as MM:SS
        except Exception as e:
            print(f"Error getting duration for {song_path}: {e}")
            return "00:00"

    def load_song_length(self, song_path):
        """Load the length of the song in seconds."""
        try:
            sound = pygame.mixer.Sound(song_path)
            return sound.get_length()
        except Exception as e:
            print(f"Error loading song length for {song_path}: {e}")
            return 0.0
