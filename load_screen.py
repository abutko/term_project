# Andrew Butko, abutko, Section A
# 15-112 Spring 2013 Term Project - due 5/1/13 at 9 PM

# load_screen.py
# background image taken from
# http://4.bp.blogspot.com/-E9HKYf_hViQ/UWHB4dv3JgI/AAAAAAAAA8A/KMMIgjFS60U/s1600/chess%2314.jpg
# note that all magic numbers for locations on the frame were decidd by trial
# and error testing for aesthetics
from Tkinter import *
from PIL import Image, ImageTk
import os
import subprocess

def mousePressed(canvas, widgets, root, event):
    redrawAll(canvas,widgets, root)

def keyPressed(canvas, widgets, root, event):
    redrawAll(canvas, widgets, root)
    
def drawBackground(canvas, widgets, root):
    if canvas.data.instructions: # instructions menu
        img = Image.open('background_instructions.png')
        canvas.data.backgroundImg = ImageTk.PhotoImage(img)
        canvas.create_image(0,0, image = canvas.data.backgroundImg, anchor=NW)
    elif canvas.data.about: # about menu
        img = Image.open('background_about.png')
        canvas.data.backgroundImg = ImageTk.PhotoImage(img)
        canvas.create_image(0,0, image = canvas.data.backgroundImg, anchor=NW)
    else: # anything else
        img = Image.open('background_title.png')
        canvas.data.backgroundImg = ImageTk.PhotoImage(img)
        canvas.create_image(0,0, image = canvas.data.backgroundImg, anchor=NW)

def gameSelection(event, canvas, widgets, root):
    # will displayer new game options
    widgets.newGame.place_forget()
    widgets.loadGame.place_forget()
    widgets.instructions.place_forget()
    widgets.about.place_forget()
    widgets.back.place(x=0,y=350)
    widgets.PvP.place(x=50,y=120)
    widgets.PvAI.place(x=320,y=120)

def loadGame(event, canvas, widgets, root):
    pwd = os.getcwd() # current working directory
    path = os.path.join(pwd, 'pvp_load.py') # filename
    subprocess.Popen("python %s" % path, shell=True) # run file
    root.destroy()

def newGame(event, canvas, widgets, root):
    pwd = os.getcwd() # current working directory
    path = os.path.join(pwd, 'pvp_new.py') # filename
    subprocess.Popen("python %s" % path, shell=True) # run file
    root.destroy()
    
def newGameAI(event, canvas, widgets, root):
    pwd = os.getcwd() # current working directory
    path = os.path.join(pwd, 'pvai_new.py') # filename
    subprocess.Popen("python %s" % path, shell=True) # run file
    root.destroy()

def loadInstructions(event, canvas, widgets, root):
    canvas.data.instructions = True
    widgets.newGame.place_forget()
    widgets.loadGame.place_forget()
    widgets.instructions.place_forget()
    widgets.about.place_forget()
    widgets.back.place(x=0,y=350)
    redrawAll(canvas, widgets, root)
    
def loadAbout(event, canvas, widgets, root):
    canvas.data.about = True
    widgets.newGame.place_forget()
    widgets.loadGame.place_forget()
    widgets.instructions.place_forget()
    widgets.about.place_forget()
    widgets.back.place(x=0,y=350)
    redrawAll(canvas, widgets, root)
    
def main(event, canvas, widgets, root):
    # goes to the initial main menu screen
    widgets.back.place_forget()
    widgets.PvP.place_forget()
    widgets.PvAI.place_forget()
    
    init(canvas, widgets, root)
    
def redrawAll(canvas, widgets, root):
    canvas.delete(ALL)
    drawBackground(canvas, widgets, root)

def createLaunchScreenWidgets(canvas, widgets, root):
    # buttons shown when the game is opened
    widgets.newGame = Button(root, text="New Game", bd=0)
    widgets.newGame.bind('<Button-1>', lambda event:
                         newGame(event, canvas, widgets, root))
    widgets.newGame.place(x=50,y=120)
    widgets.loadGame = Button(root, text="Load Game", bd=0)
    widgets.loadGame.bind('<Button-1>', lambda event:
                          loadGame(event, canvas, widgets, root))
    widgets.loadGame.place(x=50,y=220)
    widgets.instructions = Button(root, text="Instructions", bd=0)
    widgets.instructions.bind('<Button-1>', lambda event:
                          loadInstructions(event, canvas, widgets, root))
    widgets.about = Button(root, text="About", bd=0, anchor=E)
    widgets.about.bind('<Button-1>', lambda event:
                          loadAbout(event, canvas, widgets, root))
    widgets.instructions.place(x=320,y=120)
    widgets.about.place(x=320,y=220)


    
def createNewGameWidgets(canvas, widgets, root):
    # buttons that appear when you select new game
    widgets.back = Button(root, text="Back", bd=0)
    widgets.back.bind('<Button-1>', lambda event:
                      main(event, canvas, widgets, root))
    widgets.PvP = Button(root, text='Player vs. Player', bd=0)
    widgets.PvP.bind('<Button-1>', lambda event:
                     newGame(event, canvas, widgets, root))
    widgets.PvAI = Button(root, text='Black Player vs. Computer', bd=0)
    widgets.PvAI.bind('<Button-1>', lambda event:
                     newGameAI(event, canvas, widgets, root))


def init(canvas, widgets, root):
    # initialize the buttons we will use
    createLaunchScreenWidgets(canvas, widgets, root)
    createNewGameWidgets(canvas, widgets, root)
    canvas.data.instructions = False
    canvas.data.about = False
    redrawAll(canvas, widgets, root)

def run():
    # general run function based on example in animation notes
    root = Tk()
    root.title("CHESS in Python")
    # frame to create multiple widgets
    frame = Frame(root, width = 506, height = 380)
    frame.pack()
    canvas = Canvas(frame, width = 506, height = 380)
    canvas.pack()
    root.resizable(width=0, height=0)
    root.canvas = canvas.canvas = canvas
    class Struct: pass
    widgets = Struct()
    canvas.data = Struct()
    canvas.data.canvasWidth = 506
    canvas.data.canvasHeight = 380
    init(canvas, widgets, root)
    root.bind("<Button-1>", lambda event: mousePressed(canvas, widgets, root, event))
    root.bind("<Key>", lambda event: keyPressed(canvas, widgets, root, event))
    root.mainloop()
    
run()