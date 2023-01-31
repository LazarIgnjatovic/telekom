import tkinter as tk 
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showinfo

class View(object):
    def __init__(self) -> None:
        self.root=tk.Tk()
        self.root.title("Nokia BTS Logic")
        self.frame=tk.Frame(self.root)

        self.frame.pack()

    def start(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = View()
    gui.start()
