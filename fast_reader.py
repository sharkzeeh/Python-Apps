
import tkinter as tk
import threading
from threading import Timer
from tkinter import filedialog

def browse_file():
    Reader.fname = tk.filedialog.askopenfilename()
    if Reader.fname not in Reader.pending:
        text_tmp = Reader.file_opener(Reader.fname)
        Reader.pending[Reader.fname] = [0, len(text_tmp), text_tmp]

class Reader:

    root = tk.Tk()
    root.title('Speed Reading')
    root.geometry('300x100')
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(2, weight=1)

    increment = 25
    default_speed = 60

    menubar = tk.Menu(root)
    root.config(menu=menubar)

    subMenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=subMenu)
    subMenu.add_command(label="Open", command=browse_file)
    subMenu.add_command(label="Exit", command=root.destroy)

    subMenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=subMenu)
    subMenu.add_command(label="About Us")

    txt = tk.StringVar()
    wpm_var = tk.StringVar()

    word_label = tk.Label(root, textvariable=txt, font=("Courier New", 20, "italic"))
    word_label.grid(row=1, column=0)

    f = tk.Frame(root)
    f.grid(row=1, column=2,sticky=tk.SE)
    wpm_label = tk.Label(f, textvariable=wpm_var).pack()

    pending = {}
    fname = None
    
    def __init__(self, fname="leo.txt", wpm=400):
        Reader.fname = fname
        text_tmp = Reader.file_opener(fname)
        Reader.pending[Reader.fname] = [0, len(text_tmp), text_tmp]
        Reader.pending[Reader.fname][1] = len(Reader.pending[Reader.fname][2])
        self._wpm = wpm
        Reader.wpm_var.set(str(self._wpm))
        Reader.root.bind("<Down>", lambda event: self.down())
        Reader.root.bind("<Up>", lambda event: self.up())
        Reader.root.bind("<Left>", lambda event: self.frame_left())
        Reader.root.bind("<Right>", lambda event: self.frame_right())
        Reader.root.bind('<space>', lambda event: self.pause())

        self.decay = 60 / self._wpm
        self.stopper = threading.Event() # для остановки

    def up(self):
        self._wpm += Reader.increment
    def down(self):
        self._wpm -= Reader.increment
    def pause(self):
        if self.stopper.is_set():
            self.reader()
            self.stopper.clear()
        else:
            self.clock.cancel()
            self.stopper.set()

    def frame_left(self):
        if self.stopper.is_set():
            if Reader.pending[Reader.fname][0]:
                Reader.pending[Reader.fname][0] -= 1
            words = Reader.pending[Reader.fname][2]
            cur_word = words[Reader.pending[Reader.fname][0]]
            self.text_set(cur_word)

    def frame_right(self):
        if self.stopper.is_set():
            if Reader.pending[Reader.fname][0] < Reader.pending[Reader.fname][1] - 1:
                Reader.pending[Reader.fname][0] += 1
            words = Reader.pending[Reader.fname][2]
            cur_word = words[Reader.pending[Reader.fname][0]]
            self.text_set(cur_word)
    
    @staticmethod
    def file_opener(file):
        """
        splits a given text into a bag of words
        """
        with open(file, 'r') as fh:
            words = fh.read().split()
            return words

    def text_set(self, word):
        """
        displays `word` in the frame
        """
        Reader.txt.set(word)
        Reader.wpm_var.set(str(self._wpm))

    def reader(self):
        if Reader.pending[Reader.fname][0] < Reader.pending[Reader.fname][1]:
            words = Reader.pending[Reader.fname][2]
            cur_word = words[Reader.pending[Reader.fname][0]]
            if len(cur_word) <= 2 and Reader.pending[Reader.fname][0] < Reader.pending[Reader.fname][1] - 1:
                next_word = words[Reader.pending[Reader.fname][0] + 1]
                s = cur_word + " " + next_word

                self.text_set(s)
                Reader.pending[Reader.fname][0] += 2
            else:
                self.text_set(cur_word)
                Reader.pending[Reader.fname][0] += 1
        else:
            Reader.txt.set("You've read the whole text")
        try:
            self.decay = 60 / self._wpm
        except ZeroDivisionError:
            self._wpm = Reader.default_speed
            self.decay = 60 / self._wpm
        self.clock = Timer(self.decay, self.reader)
        self.clock.start()


def kickstarter():
    Reader.root.mainloop()

if __name__ == "__main__":

    r = Reader(wpm=300)
    r.reader()
    kickstarter()
