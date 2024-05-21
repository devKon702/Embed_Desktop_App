from tkinter import Button, FLAT


class CustomButton(Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config(
            relief=FLAT,
            bd=0,
            highlightthickness=0,
            padx=10,
            pady=5,
            font=("Arial", 12),
            foreground="white",
            background="orange",
        )
        # Bind events
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)

    def on_hover(self, event):
        self.config(background="lightblue")

    def on_leave(self, event):
        self.config(background="green")


def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")