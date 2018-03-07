'''
John Jefferson III, Michael Patel
December 2017

version: Python 3.6.3

File Description:
    Main class and method definitions file for the simulation.
    This creates the main window for the GUI.
    Run 'python simulation.py' in terminal to start GUI.
'''

# imports
import numpy as np
from scipy.io import wavfile
import os
import matplotlib.pyplot as plt
from detect_peaks import detect_peaks
from datetime import datetime
from scipy.fftpack import *
from matplotlib.backends.backend_pdf import PdfPages
from defs import *
from tkinter import * # Tkinter is a widely used Python package for GUIs
from PIL import ImageTk
from gui import *

class Simulation(object):
    def __init__(self):
        root = Tk()  # initializes Tkinter with a root widget. Only 1 root widget per program.
        root.iconbitmap(str(RES_DIR + PYTHON_ICON))  # set icon of root window
        root.title('Simulation')  # set title of root window
        root.configure(background='white')
        #root.wm_attributes('-transparentcolor', 'white')
        gui = GUI(root)
        root.mainloop()  # make window appear to the user. Program will stay here until the window is closed.

# end of class Simulation
sim = Simulation()