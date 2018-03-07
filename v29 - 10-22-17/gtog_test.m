clear all; close all;
frameLength = 4096;
afr = dsp.AudioFileReader('GuitarE4.wav', 'SamplesPerFrame', frameLength);
afw = dsp.AudioFileWriter('test.wav', 'SampleRate', afr.SampleRate);
FFTY = dsp.FFT;
MAXER = dsp.MovingMaximum('SpecifyWindowLength', true, 'WindowLength', 20);
scope = dsp.TimeScope('SampleRate',afr.SampleRate,'TimeSpan',0.01, 'YLimits', [-1 1]);

%variables for oscillator
sine1 = dsp.SineWave;
sine2 = dsp.SineWave;
sine3 = dsp.SineWave;

window = 1;

while ~isDone(afr)
    g = afr();
    Fsg = afr.SampleRate;
    Gf = abs(FFTY(g(:,1))); %make sure to only look at one channel
    
    Gfpks = Gf(1:length(Gf)/2);
    gMovingMax = MAXER(Gfpks);
    gThresh = mean(gMovingMax); %figure out this threshold with SNR
    [gPeaks, gFreqs] = findpeaks(gMovingMax, 'MinPeakProminence', gThresh);
    newPeaks = Gfpks/max(gPeaks);
    gfdisc = round(mean(diff(gFreqs)));
    gF0 = round(gfdisc * Fsg / length(g));
    window = window + 1;
    
    scope(g);
end

sine1.Frequency = gF0;
%sine1.Amplitude = newPeaks(1);
sine1.SamplesPerFrame = 4096*window;
%sine1.
sine1.SampleRate = 44100;
s1 = sine1();

sine2.Frequency = gF0*2;
%sine2.Amplitude = newPeaks(2);
sine2.SamplesPerFrame = 4096*window;
sine2.SampleRate = 44100;
s2 = sine2();

sine3.Frequency = gF0*3;
%sine3.Amplitude = newPeaks(3);
sine3.SamplesPerFrame = 4096*window;
sine3.SampleRate = 44100;
s3 = sine3();

newSine = s1 + s2 + s3;
afw(newSine); 

release(sine1);
release(sine2);
release(sine3);

subplot(311);
plot(g);
subplot(312);
plot(Gfpks);
subplot(313);
plot(newSine);

release(afr);
release(afw);