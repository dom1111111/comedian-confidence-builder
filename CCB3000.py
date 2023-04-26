import tkinter
from tkinter import ttk
import os
import listen_laugh

m = listen_laugh.MeasureMicPlayAudio(os.path.join(os.path.dirname(__file__), 'laugh_tracks'))

class UseState:
    def __init__(self):
        self.state = False
    
    def toggle_state(self):
        self.state = not self.state
        if self.state:
            print('>>> show start')
            start_button.config(text='Stop Show')
            live_label.grid(row=0, column=0, sticky=("s",))     # make this widget appear
            m.start()
        else:
            print('>>> show stop')
            start_button.config(text='Start Show')
            live_label.grid_forget()                            # make this widget disapear
            m.stop()

us = UseState()

# for fun, I'm using the golden ratio for the screen dimensions
golden_ratio = (1+5**(1/2)) / 2
# `x ** (1/2)`, aka "x to the power of half" -> is equivalent to 'square root of x'

####################################

# create main window
root_window = tkinter.Tk()
root_window.title("Comedian Confidence Builder 3000")
#####
# following code needed to make it so that the window starts centered on the computer screen
window_width = 750
window_height = int(round(window_width * (golden_ratio - 1), 0))    # round is used to round to nearest whole number
screen_width = root_window.winfo_screenwidth()
screen_height = root_window.winfo_screenheight()
center_x = int(screen_width/2 - window_width/2)
center_y = int((screen_height/5 * 2) - window_height/2)             # this makes it so that the screen starts roughly in the middle top half of the screen
#####
root_window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
#root_window.geometry('400x300+50+50')        # the starting size of the window in pixels (width, height) and position on the computer screen (x, y)
root_window.minsize(250, 150)                # the same as above, but minimum size of window

# this is needed to change button font!
s = ttk.Style()
s.configure('TButton', font=("Arial", 18))

# create widgets
content_frame = ttk.Frame(root_window, padding=(12,12,12,12))
main_title_label = ttk.Label(content_frame, text="The Comedian Confidence Builder 3000!", font=("Arial", 25))
start_button = ttk.Button(content_frame, text="Start Show", command=us.toggle_state)
live_label = ttk.Label(content_frame, text="LIVE", font=("Arial", 25))

# place widgets within window using geometry manager (in this case `grid`)
content_frame.grid(row=0, column=0, sticky=('n','s','e','w'))
main_title_label.grid(row=0, column=0, sticky=("n",))
    # the `sticky` paramter makes it so that they gravitate towards which ever direction you provide
    # if you do multiple directions that are "beside" each other (ex: NE), then it will go in the respective corner
start_button.grid(row=0, column=0)

# so you need to do column and row configure to both the window and any frames if you want things to be resizeable
root_window.columnconfigure(0, weight=1)
root_window.rowconfigure(0, weight=1)
content_frame.columnconfigure(0, weight=1)
content_frame.rowconfigure(0, weight=1)

root_window.mainloop()