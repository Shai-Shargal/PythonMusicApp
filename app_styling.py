import customtkinter as ctk


class AppStyling:
    def __init__(self):
        ctk.set_appearance_mode("System")  # Use system settings (Light/Dark)
        ctk.set_default_color_theme("blue")  # Default color theme

    def style_button(self, parent, text, command):
        """Return a styled button."""
        return ctk.CTkButton(parent, text=text, command=command, width=100, height=32)

    def style_slider(self, parent, command=None):
        """Return a styled slider."""
        return ctk.CTkSlider(parent, from_=0, to=100, command=command, width=200)

    def style_label(self, parent, text, font=("Arial", 12)):
        """Return a styled label."""
        return ctk.CTkLabel(parent, text=text, font=font)

    def style_listbox(self, parent):
        """Return a styled listbox."""
        return ctk.CTkTextbox(parent, width=600, height=200, wrap="none")
