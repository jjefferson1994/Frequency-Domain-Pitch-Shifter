'''
John Jefferson III, Michael Patel
December 2017

version: Python 3.6.3

File Description:
    Class and method definitions related to the simulation algorithm itself.
    This includes reading in the .wav input sound files, performing the FFTs,
    pitch detection, IFFTs and writing to a .wav output sound file.

Inputs:
    - String arguments related to the names of the 2 .wav input sound files
        as selected from the GUI

Outputs:
    - .wav output sound file
    - a PDF of the generated plots
    - return the sampling rates of the guitar and recorded for the GUI
    - return the fundamental frequencies of the guitar and recorded for the GUI

High-level overview of the algorithm:
    - set up the I/O
    - read in .wav files
    - perform FFT
    - set up the parameters for pitch detection
    - get the fundamental frequency (pitch detection) and harmonic information
    - normalize the amplitudes
    - perform the substitution necessary to construct the new signal
    - perform IFFT
    - write to .wav file
'''

# imports
from defs import *
import numpy as np
from scipy.fftpack import *
from scipy.io import wavfile
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from detect_peaks import detect_peaks
from datetime import datetime

class Algorithm(object):

    def __init__(self, guitar, recorded):
        self.guitar = guitar
        self.recorded = recorded
        #print('\nalgGuitar: ' + str(self.guitar))
        #print('\nalgRec: ' + str(self.recorded))

        # Sampling rates and fundamental frequencies for guitar and recorded are returned for the GUI
        self.Fsg = 0
        self.Fsr = 0
        self.gF0 = 0
        self.rF0 = 0

    def getGUIvalues(self): # Sampling rates and fundamental frequencies for guitar and recorded are returned for the GUI
        return self.gF0, self.Fsg, self.rF0, self.Fsr

    def run(self):
        # SETUP
        start = datetime.now() # get the initial time when simulation is running; this will be used to determine the total time that it takes to run simulation
        gFile, rFile, nFile = self.setupIOfiles(self.guitar, self.recorded) # sets up the input and output file structure
        #print('\ngfile: ' + str(gFile))
        #print('\nrfile: ' + str(rFile))

        # read the input .wav files
        self.Fsg, g = wavfile.read(GUITAR_DIR + gFile)
        self.Fsr, r = wavfile.read(RECORDED_DIR + rFile)
        #print('\nFsg: ' + str(self.Fsg))
        #print('\nFsr: ' + str(self.Fsr))

        Gf, Rf1, Rf2 = self.doFFT(g, r) # perform the FFT on the input data

        heightFactor, distanceFactor = self.setupPitchDetection() # set up parameters for pitch detection

        # get the continuous and discrete fundamental frequencies for the guitar and recorded
        self.gF0, gdisc, gContFreqs, gFreqs, self.rF0, rdisc1, rContFreqs1, rFreqs1, rdisc2, rContFreqs2, rFreqs2 = self.getFundamentalAndHarmonics(g, Gf, r, Rf1, Rf2, heightFactor, distanceFactor)

        # get the normalized amplitude values of the guitar and recorded
        # also writes the frequency and amplitude information to text files located in OUTPUT directory
        gAmps, rAmps1, rAmps2 = self.normalizeAmplitudes(Gf, gContFreqs, gFreqs, Rf1, rContFreqs1, rFreqs1, Rf2, rContFreqs2, rFreqs2)

        #print('\ngAmps: ' + str(gAmps))
        #print('\rrAmps1: ' + str(rAmps1))
        #print('\nrAmps2: ' + str(rAmps2))

        Nf1, Nf2 = self.doSubstitution(Gf, Rf1, Rf2, gdisc, rdisc1, rdisc2) # create the new signal's spectrum

        new_sound = self.doIFFT(Nf1, Nf2) # perform the IFFT on the new signal spectrum

        self.writeToWAV(nFile, new_sound) # write the new signal to a .wav output sound file

        self.writePlots(g, r, new_sound, Gf, Rf1, Rf2, Nf1, Nf2) # create plots for the guitar, recorded and new sound in time and frequency domains

        end = datetime.now()
        diff = end - start
        print('\nTotal time: ' + str(diff)) # prints total time that it took to do the algorithm

    def setupIOfiles(self, guitar, recorded): # create the tags for the guitar, recorded and new sound files
        guitar_wavFile = guitar + '.wav'
        recorded_wavFile = recorded + '.wav'
        new_wavFile = SOUND_DIR + 'New_' + str(guitar) + '_' + str(recorded) + '.wav'
        return guitar_wavFile, recorded_wavFile, new_wavFile # return file tags for guitar, recorded and new sound

    def doFFT(self, g, r): # perform FFT
        Gf = np.abs(fft(g[:, 0]))
        if len(np.shape(r)) == 1:  # checks if recorded sound is 1-channel (is mono)
            Rf1 = np.abs(fft(r))  # first channel of stereo
            Rf2 = np.abs(fft(r))  # second channel of stereo
        else: # recorded sound has 2-channels (is stereo)
            Rf1 = np.abs(fft(r[:, 0]))  # first channel of stereo
            Rf2 = np.abs(fft(r[:, 1]))  # second channel of stereo

        return Gf, Rf1, Rf2 # return FFTs of the guitar and each channel of the recorded

    def setupPitchDetection(self): # parameters necessary for pitch detection
        heightFactor = 0.1
        distanceFactor = 0.9
        return heightFactor, distanceFactor # return height and distance parameters

    def getFundamentalAndHarmonics(self, g, Gf, r, Rf1, Rf2, heightFactor, distanceFactor):
        # performs the pitch detection to find the fundamental frequencies using detect_peaks call (see 'detect_peaks.py')
        # also finds the frequencies of the harmonics by calling detect_peaks a second time

        # guitar
        tempGf = Gf[0:int(len(Gf) / 2)]  # use half-spectrum
        gFreqs = detect_peaks(tempGf, mph=heightFactor * np.max(np.abs(tempGf)))
        gdisc = gFreqs[0]  # use this for calculating fundamental as it is the discrete fundamental frequency
        gF0 = gdisc * self.Fsg / len(g)  # this is the continuous fundamental frequency
        gFreqs = detect_peaks(tempGf, mph=np.mean(tempGf), mpd=gdisc * distanceFactor)
        gContFreqs = gFreqs * self.Fsg / len(g)  # list of the continuous frequencies

        # recorded channel 1
        tempRf1 = Rf1[0:int(len(Rf1) / 2)] # use half-spectrum
        rFreqs1 = detect_peaks(tempRf1, mph=heightFactor * np.max(np.abs(tempRf1)))
        rdisc1 = rFreqs1[0] # use this for calculating fundamental as it is the discrete fundamental frequency
        rF0 = rdisc1 * self.Fsr / len(r) # this is the continuous fundamental frequency
        rFreqs1 = detect_peaks(tempRf1, mph=np.mean(tempRf1), mpd=rdisc1 * distanceFactor)
        rContFreqs1 = rFreqs1 * self.Fsr / len(r) # list of the continuous frequencies

        # recorded channel 2
        tempRf2 = Rf2[0:int(len(Rf2) / 2)] # use half-spectrum
        rFreqs2 = detect_peaks(tempRf2, mph=heightFactor * np.max(np.abs(tempRf2)))
        rdisc2 = rFreqs2[0] # use this for calculating fundamental as it is the discrete fundamental frequency
        rF0_2 = rdisc2 * self.Fsr / len(r) # this is the continuous fundamental frequency
        rFreqs2 = detect_peaks(tempRf2, mph=np.mean(tempRf2), mpd=rdisc2 * distanceFactor)
        rContFreqs2 = rFreqs2 * self.Fsr / len(r) # list of the continuous frequencies

        return gF0, gdisc, gContFreqs, gFreqs, rF0, rdisc1, rContFreqs1, rFreqs1, rdisc2, rContFreqs2, rFreqs2 # return frequency information

    def normalizeAmplitudes(self, Gf, gContFreqs, gFreqs, Rf1, rContFreqs1, rFreqs1, Rf2, rContFreqs2, rFreqs2):
        # normalizes the amplitudes
        # also writes the frequencies and amplitudes to text files in OUTPUT directory

        # guitar
        gPeaks = np.zeros((len(gFreqs))) # initialize an amplitudes object
        for i in range(len(gFreqs)):
            gPeaks[i] = Gf[gFreqs[i]]
        gPeaks = gPeaks / np.max(np.abs(gPeaks))  # normalized

        # write guitar frequencies to text file
        with open(FREQ_DIR + str(self.guitar) + '_Freqs.txt', 'w') as file:
            for freq in gContFreqs:
                file.write(str(freq) + '\n')

        # write guitar normalized amplitudes to text file
        with open(AMP_DIR + str(self.guitar) + '_NormalizedAmps.txt', 'w') as file:
            for amp in gPeaks:
                file.write(str(amp) + '\n')

        # recorded channel 1
        rPeaks1 = np.zeros((len(rFreqs1))) # initialize an amplitudes object
        for j in range(len(rFreqs1)):
            rPeaks1[j] = Rf1[rFreqs1[j]]
        rPeaks1 = rPeaks1 / np.max(np.abs(rPeaks1))  # normalized

        # recorded channel 2
        rPeaks2 = np.zeros((len(rFreqs2))) # initialize an amplitudes object
        for k in range(len(rFreqs2)):
            rPeaks2[k] = Rf2[rFreqs2[k]]
        rPeaks2 = rPeaks2 / np.max(np.abs(rPeaks2))  # normalized

        # write recorded frequencies to text file
        with open(FREQ_DIR + str(self.recorded) + '_Freqs.txt', 'w') as file:
            for freq in rContFreqs1:
                file.write(str(freq) + '\n')

        # write recorded normalized amplitudes to text file
        with open(AMP_DIR + str(self.recorded) + '_NormalizedAmps.txt', 'w') as file:
            for amp in rPeaks1:
                file.write(str(amp) + '\n')

        return gPeaks, rPeaks1, rPeaks2 # return the normalized amplitudes of the guitar and each channel of the recorded

    def doSubstitution(self, Gf, Rf1, Rf2, gdisc, rdisc1, rdisc2):
        # channel 1
        fundamentalBandwidth1 = int(np.minimum(gdisc / 2, rdisc1 / 2)) # width around the frequency spikes
        termRf = int(np.round(len(Rf1) / rdisc1))
        termGf = int(np.round(len(Gf) / gdisc))
        loopTerminator = np.minimum(termGf, termRf) # value used to determine how many frequency spikes are used to create the new signal

        Nf1 = np.zeros((np.maximum(len(Gf), len(Rf1)))) # initialize a new sound frequency object for channel 1

        # for-loop used to build the new sound frequency object for channel 1
        for n in range(1, loopTerminator):
            Nf1[n * gdisc - fundamentalBandwidth1: n * gdisc + fundamentalBandwidth1] = Rf1[
                                                                                        n * rdisc1 - fundamentalBandwidth1: n * rdisc1 + fundamentalBandwidth1]

        # channel 2
        fundamentalBandwidth2 = int(np.minimum(gdisc / 2, rdisc2 / 2)) # width around the frequency spikes
        termRf2 = int(np.round(len(Rf2) / rdisc2))
        termGf2 = int(np.round(len(Gf) / gdisc))
        loopTerminator2 = np.minimum(termGf2, termRf2) # value used to determine how many frequency spikes are used to create the new signal

        Nf2 = np.zeros((np.maximum(len(Gf), len(Rf2)))) # initialize a new sound frequency object for channel 2

        # for-loop used to build the new sound frequency object for channel 2
        for m in range(1, loopTerminator2):
            Nf2[m * gdisc - fundamentalBandwidth2: m * gdisc + fundamentalBandwidth2] = Rf2[
                                                                                        m * rdisc2 - fundamentalBandwidth2: m * rdisc2 + fundamentalBandwidth2]

        #print('\nfundBW1: ' + str(fundamentalBandwidth1))
        #print('\nfundBW2: ' + str(fundamentalBandwidth2))
        #print('\nLoopTerm: ' + str(loopTerminator) + '_' + str(loopTerminator2))
        return Nf1, Nf2 # return FFTs of the new sound for each channel

    def doIFFT(self, Nf1, Nf2): # performs the IFFT on the new sound
        new1 = np.real(ifft(Nf1)) # channel 1
        new2 = np.real(ifft(Nf2)) # channel 2
        new_sound = np.array(np.vstack((new1, new2))).T  # combine stereo channels
        #print('\ntypeNewSound: ' + str(type(new_sound)))
        return new_sound # return the new sound

    def writeToWAV(self, nFile, new_sound): # write the new sound to a .wav output sound file
        #print('\ntypeNewSound: ' + str(type(new_sound)))
        new_sound = new_sound[0:int(len(new_sound) / 2)] # use half of the new sound b/c of the mirroring

        new_sound = new_sound.astype(np.int16) # writing to 16-bit PCM .wav format
        wavfile.write(nFile, self.Fsg, new_sound)  # using guitar sampling rate

    def writePlots(self, g, r, new_sound, Gf, Rf1, Rf2, Nf1, Nf2): # create a PDF of the plots
        pp = PdfPages(PLOT_DIR + 'PLOTS_' + str(self.guitar) + '_' + str(self.recorded) + '.pdf') # create PDF object

        # PLOTs
        # time
        plt.plot(g)
        plt.title('TIME - Guitar')
        plt.ylabel('Normalized PSD')
        plt.xlabel('# of samples - Fs = 48000')
        # plt.axis([0, 0.1, -35000, 35000])
        pp.savefig()
        # plt.savefig('TIME - Guitar.pdf')
        plt.clf()

        plt.plot(r)
        plt.title('TIME - Recorded')
        plt.ylabel('Normalized PSD')
        plt.xlabel('# of samples - Fs = 44100')
        pp.savefig()
        # plt.savefig('TIME - Recorded.png')
        plt.clf()

        plt.plot(new_sound[0:int(len(new_sound)/2)])
        plt.title('TIME - New Sound')
        plt.ylabel('Normalized PSD')
        plt.xlabel('# of samples - Fs = 48000')
        pp.savefig()
        # plt.savefig('TIME - New Sound.png')
        plt.clf()

        # freq
        plt.plot(Gf)
        plt.title('FREQ - Guitar')
        plt.ylabel('Normalized PSD')
        plt.xlabel('# of samples - Fs = 48000')
        #plt.axis([0, 70000, 0, 1.1])
        pp.savefig()
        # plt.savefig('FREQ - Guitar.pdf')
        plt.clf()

        plt.plot(Rf1)
        plt.title('FREQ - Recorded Channel 1')
        plt.ylabel('')
        plt.xlabel('')
        pp.savefig()
        # plt.savefig('FREQ - Recorded Channel 1.png')
        plt.clf()

        plt.plot(Rf2)
        plt.title('FREQ - Recorded')
        plt.ylabel('Normalized PSD')
        plt.xlabel('# of samples - Fs = 44100')
        #plt.axis([0, 15000, 0, 1.1])
        pp.savefig()
        # plt.savefig('FREQ - Recorded Channel 2.png')
        plt.clf()

        plt.plot(Nf1)
        plt.title('FREQ - New Sound Channel 1')
        pp.savefig()
        # plt.savefig('FREQ - New Sound Channel 1.png')
        plt.clf()

        plt.plot(Nf2)
        plt.title('FREQ - New Sound')
        plt.ylabel('Normalized PSD')
        plt.xlabel('# of samples - Fs = 48000')
        #plt.axis([0, 70000, 0, 1.1])
        pp.savefig()
        # plt.savefig('FREQ - New Sound Channel 2.png')
        plt.clf()

        pp.close()