'''
John Jefferson III, Michael Patel
December 2017

version: Python 3.6.3

File Description:
    The GUI class and method definitions for the simulation. This includes making the
    necessary output directory structure, GUI features and interactions with the end user.
    The GUI layout is flattened.
'''

# imports
from defs import *
from tkinter import * # Tkinter is a widely used Python package for GUIs
from PIL import ImageTk
import errno
from winsound import *
from algorithm import *

class GUI(object):
    def __init__(self, master):

        self.makeOutputDir() # create the output directory necessary for storing output files of the simulation

        # Images - create image references
        self.playButtonImage = self.getImage(PLAY)
        self.runImage = self.getImage(RUN)
        self.dropArrowImage = self.getImage(DROP_ARROW)

        # Columns
        # 5 frame objects arranged in grid fashion (dir, colLeft, colMid, colRight, run)
        self.dirFrame = Frame(master, background='white') # top label
        self.colLeftFrame = Frame(master, background='white') # guitar - left column
        self.colMidFrame = Frame(master, background='white') # recorded - middle column
        self.colRightFrame = Frame(master, background='white') # new sound - right column
        self.runFrame = Frame(master, background='white') # bottom button

        # Top Label
        self.topLabel = self.createTopLabel(self.dirFrame) # create the top label which lists where the OUTPUT directory is located

        # Title - create title labels at the top of each column for guitar, recorded and new sound
        # guitar
        self.gTitle = Label(self.colLeftFrame, text='Guitar', background='white', font=(FONT_STYLE, FONT_SIZE_LARGE), pady=ROW_PADDING)
        self.gTitle.pack()

        self.rTitle = Label(self.colMidFrame, text='Recorded', background='white', font=(FONT_STYLE, FONT_SIZE_LARGE), pady=ROW_PADDING)
        self.rTitle.pack()

        self.nTitle = Label(self.colRightFrame, text='New Sound', background='white', font=(FONT_STYLE, FONT_SIZE_LARGE), pady=ROW_PADDING)
        self.nTitle.grid(row=0)


        # Menu selected option string object variables - these will track as the user selects between different drop-down options
        self.gOption = StringVar()
        self.rOption = StringVar()
        self.nOption = StringVar()

        # Menu - drop down menu
        # guitar
        self.gMenu = OptionMenu('', '', '')
        self.gChoices = [] # drop-down choices, drop-down options
        for file in os.listdir(GUITAR_DIR): # build list of drop-down choices
            if(file.endswith('.wav')):
                self.gChoices.append(self.getFilename(file))

        self.setGoption(self.gChoices[0]) # set default drop-down choice
        self.gMenu = OptionMenu(self.colLeftFrame, self.gOption, *self.gChoices, command=self.setGoption)
        self.gMenu.config(indicatoron=0, image=self.dropArrowImage, compound='right', background='white', font=(FONT_STYLE, FONT_SIZE_MEDIUM), pady=ROW_PADDING)
        self.gMenu['border'] = '0' # make transparent
        self.gMenu.pack()

        # recorded
        self.rMenu = OptionMenu('', '', '')
        self.rChoices = [] # drop-down choices, drop-down options
        for file in os.listdir(RECORDED_DIR): # build list of drop-down choices
            if(file.endswith('.wav')):
                self.rChoices.append(self.getFilename(file))
        self.setRoption(self.rChoices[0]) # set default drop-down choice
        self.rMenu = OptionMenu(self.colMidFrame, self.rOption, *self.rChoices, command=self.setRoption)
        self.rMenu.config(indicatoron=0, image=self.dropArrowImage, compound='right', background='white', font=(FONT_STYLE, FONT_SIZE_MEDIUM), pady=ROW_PADDING)
        self.rMenu['border'] = '0' # make transparent
        self.rMenu.pack()

        # new sound
        self.nMenu = OptionMenu('', '', '')
        self.nChoices = [] # drop-down choices, drop-down options
        try:
            for file in os.listdir(OUTPUT_DIR): # build list of drop-down choices
                if(file.endswith('.wav')):
                    self.nChoices.append(self.getFilename(file))
            self.nOption.set(self.nChoices[0]) # set default drop-down choice
        except:  # broad exception
            self.nChoices.append('None available')
            self.nOption.set(self.nChoices[0]) # set default drop-down choice
        #self.nOption.set(self.nChoices[0])
        self.nMenu = OptionMenu(self.colRightFrame, self.nOption, *self.nChoices, command=self.setNoption)
        self.nMenu.config(indicatoron=0, image=self.dropArrowImage, compound='right', background='white', font=(FONT_STYLE, FONT_SIZE_MEDIUM), pady=ROW_PADDING)
        self.nMenu['border'] = '0' # make transparent
        self.nMenu.after(TWO_SECONDS, self.updateNMenu) # update this particular menu every 2s
        self.nMenu.grid(row=1)

        # Text for Fundamental - string object variables - these will track the fundamental frequencies as they change for different sounds
        self.gF0text = StringVar()
        self.rF0text = StringVar()
        self.nF0text = StringVar()

        # Fundamental Labels
        # guitar
        self.gF0Label = Label(self.colLeftFrame, text='Fundamental: ' + str(self.gF0text.get()), font=(FONT_STYLE, FONT_SIZE_MEDIUM), pady=ROW_PADDING, background='white')
        self.gF0Label.after(HALF_SECOND, self.updateGF0Label)
        self.gF0Label.pack()

        # recorded
        self.rF0Label = Label(self.colMidFrame, text='Fundamental: ' + str(self.rF0text.get()), font=(FONT_STYLE, FONT_SIZE_MEDIUM), pady=ROW_PADDING, background='white')
        self.rF0Label.after(HALF_SECOND, self.updateRF0Label)
        self.rF0Label.pack()

        # new sound
        self.nF0Label = Label(self.colRightFrame, text='Fundamental: ' + str(self.nF0text.get()), font=(FONT_STYLE, FONT_SIZE_MEDIUM), pady=ROW_PADDING, background='white')
        self.nF0Label.after(HALF_SECOND, self.updateNF0Label)
        self.nF0Label.grid(row=2)

        # Text for Sampling Rate - string object variables - these will track the sampling rates as they change for different sounds
        self.gFstext = StringVar()
        self.rFstext = StringVar()
        self.nFstext = StringVar()

        # Sampling Rate Labels
        # guitar
        self.gFsLabel = Label(self.colLeftFrame, text='Sampling Rate: ' + str(self.gFstext.get()), font=(FONT_STYLE, FONT_SIZE_MEDIUM), pady=ROW_PADDING, background='white')
        self.gFsLabel.after(HALF_SECOND, self.updateGFSLabel)
        self.gFsLabel.pack()

        # recorded
        self.rFsLabel = Label(self.colMidFrame, text='Sampling Rate: ' + str(self.rFstext.get()), font=(FONT_STYLE, FONT_SIZE_MEDIUM), pady=ROW_PADDING, background='white')
        self.rFsLabel.after(HALF_SECOND, self.updateRFSLabel)
        self.rFsLabel.pack()

        # new sound
        self.nFsLabel = Label(self.colRightFrame, text='Sampling Rate: ' + str(self.nFstext.get()), font=(FONT_STYLE, FONT_SIZE_MEDIUM), pady=ROW_PADDING, background='white')
        self.nFsLabel.after(HALF_SECOND, self.updateNFSLabel)
        self.nFsLabel.grid(row=3)

        # Play Buttons - for playing the different sounds depending on which drop-down choice was selected
        # guitar
        self.gPlayButton = Button(self.colLeftFrame, image=self.playButtonImage, background='white', command=self.playGuitar)
        self.gPlayButton['border'] = '0' # make transparent
        self.gPlayButton.pack()

        # recorded
        self.rPlayButton = Button(self.colMidFrame, image=self.playButtonImage, background='white', command=self.playRecorded)
        self.rPlayButton['border'] = '0' # make transparent
        self.rPlayButton.pack()

        # new sound
        self.nPlayButton = Button(self.colRightFrame, image=self.playButtonImage, background='white', command=self.playNew)
        self.nPlayButton['border'] = '0' # make transparent
        self.nPlayButton.grid(row=4)

        # create Run button that launches the simulation algorithm to create a new sound
        self.runButton = self.createRunButton(self.runFrame)

        # layout structure for the main GUI
        self.dirFrame.grid(row=0, column=0, columnspan=3, sticky='nsew', pady=TOP_FRAME_PADDING)
        self.colLeftFrame.grid(row=1, column=0, sticky='nsew', padx=COLUMN_PADDING)
        self.colMidFrame.grid(row=1, column=1, sticky='nsew', padx=COLUMN_PADDING)
        self.colRightFrame.grid(row=1, column=2, sticky='nsew', padx=COLUMN_PADDING)
        self.runFrame.grid(row=2, column=0, columnspan=3, sticky='nsew', pady=BOTTOM_FRAME_PADDING)

        # make column widths even
        master.grid_columnconfigure(0, weight=1, uniform='a')
        master.grid_columnconfigure(1, weight=1, uniform='a')
        master.grid_columnconfigure(2, weight=1, uniform='a')

    def createTopLabel(self, location): # the top label displays the OUTPUT directory for .wav files, plot PDFs, .txt files, etc.
        label = Label(location, text=str('Simulation outputs created in: ' + OUTPUT_DIR), font=(FONT_STYLE, FONT_SIZE_MEDIUM), foreground='white', background='red')
        label.pack()
        return label

    def createRunButton(self, location): # create the Run button GUI object
        button = Button(location, image=self.runImage, background='white')
        button.config(command=self.runSim)
        button['border'] = '0' # make transparent
        button.pack()
        return button

    def runSim(self): # runs the simulation algorithm
        # create a toplevel display message that says 'Running...' while algorithm runs in the background
        toplevel = Toplevel(background='white')
        toplevel.iconbitmap(str(RES_DIR + PYTHON_ICON))
        w = toplevel.winfo_screenwidth() / 6 # set the width size
        h = toplevel.winfo_screenheight() / 10 # set the height size
        toplevel.geometry('%dx%d' % (w,h))
        toplevel.title('New Sound Simulation')
        message = Label(toplevel, text='Running...', font=(FONT_STYLE, FONT_SIZE_MEDIUM), background='white', pady=toplevel.winfo_reqheight())
        message.pack()
        toplevel.update()

        g = self.gOption.get() # get current drop-down choice for guitar
        r = self.rOption.get() # get current drop-down choice for recorded
        alg = Algorithm(g, r)
        alg.run()
        gF0, Fsg, rF0, Fsr = alg.getGUIvalues() # get the sampling rate and fundamental frequency info

        # update the sampling rate and fundamental frequency info on the GUI
        self.gF0text.set(str(gF0))
        self.gFstext.set(str(Fsg))
        self.rF0text.set(str(rF0))
        self.rFstext.set(str(Fsr))
        self.nF0text.set(str(gF0))
        self.nFstext.set(str(Fsg))

        toplevel.withdraw() # finished running the simulation, close the display message

    def playGuitar(self): # plays the current drop-down choice for guitar
        file = GUITAR_DIR + str(self.gOption.get())
        print('\nfile: ' + file)
        return PlaySound(file, SND_ASYNC)

    def playRecorded(self): # plays the current drop-down choice for recorded
        file = RECORDED_DIR + str(self.rOption.get())
        print('\nfile: ' + file)
        return PlaySound(file, SND_ASYNC)

    def playNew(self): # plays the current drop-down choice for new sound
        file = OUTPUT_DIR + str(self.nOption.get())
        print('\nfile: ' + file)
        return PlaySound(file, SND_ASYNC)

    def setGoption(self, value):
        self.gOption.set(value)
        #print('\ngOption: ' + str(self.gOption.get()))

    def setRoption(self, value):
        self.rOption.set(value)
        #print('\nrOption: ' + str(self.rOption.get()))

    def setNoption(self, value):
        self.nOption.set(value)
        #print('\nnOption: ' + str(self.nOption.get()))

    def updateNMenu(self): # update the drop-down menu for the new sound
        last = self.nOption.get() # get the current drop-down choice
        #print('\n' + str(last))
        self.nMenu.destroy() # remove the drop-down menu for the new sound
        self.nChoices = [] # drop-down choices, drop-down options
        for file in os.listdir(SOUND_DIR): # build list of drop-down choices
            if(file.endswith('.wav')):
                self.nChoices.append(self.getFilename(file))
        self.nOption.set(last) # set the default drop-down choice to the last known choice
        self.nMenu = OptionMenu(self.colRightFrame, self.nOption, *self.nChoices, command=self.setNoption)
        self.nMenu.config(indicatoron=0, image=self.dropArrowImage, compound='right', background='white',
                          font=(FONT_STYLE, FONT_SIZE_MEDIUM), pady=ROW_PADDING)
        self.nMenu['border'] = '0' # make transparent
        self.nMenu.after(TWO_SECONDS, self.updateNMenu) # update this particular menu every 2s
        self.nMenu.grid(row=1)

    def updateGF0Label(self): # update the fundamental frequency for guitar
        self.gF0Label.config(text='Fundamental: ' + str(self.gF0text.get()))
        self.gF0Label.after(HALF_SECOND, self.updateGF0Label)

    def updateRF0Label(self): # update the fundamental frequency for recorded
        self.rF0Label.config(text='Fundamental: ' + str(self.rF0text.get()))
        self.rF0Label.after(HALF_SECOND, self.updateRF0Label)

    def updateNF0Label(self): # update the fundamental frequency for new sound
        self.nF0Label.config(text='Fundamental: ' + str(self.nF0text.get()))
        self.nF0Label.after(HALF_SECOND, self.updateNF0Label)

    def updateGFSLabel(self): # update the sampling rate for guitar
        self.gFsLabel.config(text='Sampling Rate: ' + str(self.gFstext.get()))
        self.gFsLabel.after(HALF_SECOND, self.updateGFSLabel)

    def updateRFSLabel(self): # update the sampling rate for recorded
        self.rFsLabel.config(text='Sampling Rate: ' + str(self.rFstext.get()))
        self.rFsLabel.after(HALF_SECOND, self.updateRFSLabel)

    def updateNFSLabel(self): # update the sampling rate for new sound
        self.nFsLabel.config(text='Sampling Rate: ' + str(self.nFstext.get()))
        self.nFsLabel.after(HALF_SECOND, self.updateNFSLabel)

    def makeOutputDir(self): # creates the directory structure for the OUTPUT files
        dirList = [OUTPUT_DIR, FREQ_DIR, AMP_DIR, SOUND_DIR, PLOT_DIR]
        for i in range(len(dirList)):
            try:
                os.makedirs(dirList[i])
            except OSError as e:
                if e.errno == errno.EEXIST and os.path.isdir(dirList[i]):
                    pass
                else:
                    raise

    def getFilename(self, file): # returns the filename portion of a given file
        filename, extension = os.path.splitext(file)
        return filename

    def getImage(self, key): # returns an image resource
        image = ImageTk.PhotoImage(file=str(RES_DIR + key))  # create an image with a 'play' icon
        return image

# end of class GUI
#



