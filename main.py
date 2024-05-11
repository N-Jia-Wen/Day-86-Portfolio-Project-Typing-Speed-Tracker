from tkinter import Tk, Label, Text, Canvas, Button, END
import requests
from ctypes import windll
import pyglet

# To fix blurry tkinter font AND blurry pop-up box when uploading img file. Taken from https://stackoverflow.com
# /questions/41315873/attempting-to-resolve-blurred-tkinter-text-scaling-on-windows-10-high-dpi-disp/43046744#43046744
windll.shcore.SetProcessDpiAwareness(1)

# Rendering custom fonts. Taken from https://stackoverflow.com/questions/11993290/truly-custom-font-in-tkinter
pyglet.font.add_file("./fonts/Open_Sans/OpenSans-VariableFont_wdth,wght.ttf")

# Random quotes used to test typing speed is from Luke Peavey's API:
# https://github.com/lukePeavey/quotable?tab=readme-ov-file#get-random-quote

parameters = {
    "minLength": 201,
    "maxLength": 250
}


response = requests.get("https://api.quotable.io/quotes/random", params=parameters)
response.raise_for_status()
data = response.json()[0]

quote = data.get("content").strip()
author = data.get("author")


class TypingSpeedTracker:

    def __init__(self, quote, author):
        self.counting_down = True
        self.quote = quote
        self.author = author

        self.window = Tk()
        self.window.title("Typing Speed Tracker!")
        self.window.minsize(width=1500, height=1000)
        self.window.config(padx=20, pady=20)

        self.title_label = Label(text="Welcome to the Typing Speed Tracker!",
                                 font=("Open Sans Light", 30, "bold"))
        self.title_label.config(pady=50)
        self.title_label.pack()

        # width=50 sets 50 characters per line
        self.quote_text = Text(self.window, wrap="word", height=7, width=50, font=("Calibri", 24, "normal"))
        self.quote_text.insert(END, f"{self.quote}\n\nQuote by: {author}")
        self.quote_text.config(state="disabled")
        self.quote_text.pack()

        # Whitespace separator (empty Label widget)
        whitespace_1 = Label(self.window, height=2)
        whitespace_1.pack()

        self.type_text = Text(self.window, wrap="word", height=5, width=50, font=("Calibri", 18, "normal"))
        self.type_text.bind("<KeyRelease>", self.check_answer)
        self.type_text.config(state="disabled")
        self.type_text.pack()

        self.typing_speed_label = Label(self.window, height=2, text="", font=("Open Sans Light", 14, "normal"))
        self.typing_speed_label.config(pady=2)
        self.typing_speed_label.pack()

        self.canvas = Canvas(width=250, height=75, bg="black")
        self.timer_display = self.canvas.create_text(125, 37.5, text="0", fill="#4AA03F",
                                                     font=("Calibri", 30, "bold"), tags=["text"])
        self.canvas.pack()
        self.timer_functionality = None

        # Whitespace separator (empty Label widget)
        whitespace_2 = Label(self.window, height=1)
        whitespace_2.pack()

        self.start_button = Button(text="Start test!", font=("Calibri", 16, "normal"), fg="white", bg="green",
                                   command=self.start_timer)
        self.start_button.pack()

        self.window.mainloop()

    def count_down(self, count: int):
        self.start_button.config(state="disabled", bg="white")

        # When timer first counts down to start:
        if count > 0 and self.counting_down is True:
            self.canvas.itemconfig(self.timer_display, text=count)
            # Timer ticks down every second
            self.timer_functionality = self.window.after(1000, self.count_down, count - 1)

        # When count down reaches zero, displays "Go!" for 5 seconds
        elif count == 0 and self.counting_down is True:
            self.canvas.itemconfig(self.timer_display, text="Go!")
            # Allows user to start typing
            self.type_text.config(state="normal")
            self.type_text.focus()

            self.timer_functionality = self.window.after(5000, self.count_down, count + 5)
            self.counting_down = False

        # After wards, starts timing time taken for user to type:
        elif self.counting_down is False:
            count_min = int(count // 60)
            count_sec = int(count % 60)
            count_dec = int(count % 1 * 10)
            formatted_min = "{:02d}".format(count_min)
            formatted_sec = "{:02d}".format(count_sec)
            formatted_sec = f"{formatted_sec}.{count_dec}"

            self.canvas.itemconfig(self.timer_display, text=f"{formatted_min}:{formatted_sec}")
            self.timer_functionality = self.window.after(100, self.count_down, count + 0.1)

    def start_timer(self):
        self.count_down(3)

    def get_canvas_text(self):
        # Find all text items on the canvas
        text_items = self.canvas.find_withtag("text")

        # Retrieve the text associated with the text item
        text = self.canvas.itemcget(text_items[0], "text")
        return text

    def check_answer(self, event):
        # Get the text entered by the user
        user_input = self.type_text.get("1.0", END).strip()
        if user_input == self.quote:
            self.type_text.config(state="disabled")
            self.window.after_cancel(self.timer_functionality)

            time = self.get_canvas_text()
            try:
                minute = float(time.split(":")[0])
                second = float(time.split(":")[1])
                time_min = minute + (second / 60)
            except ValueError:
                self.typing_speed_label.config(text="Hey! No cheating >:|")
            else:

                quote_words_num = len(self.quote.split(" "))
                words_per_min = quote_words_num / time_min
                self.typing_speed_label.config(text=f"Typing speed: {words_per_min:.0f} words per minute")


app = TypingSpeedTracker(quote, author)
