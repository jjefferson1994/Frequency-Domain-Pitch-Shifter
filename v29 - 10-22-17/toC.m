clear all;

guitarFile = 'GuitarE4.wav';
recordFile = 'PianoE.wav';
newFile = 'new_PianoE_GuitarE4.wav';
frameLength = 4096;

%book-keeping variables for oscillator
df = 0.5; % Frequency resolution = 0.05 Hz
minSFDR = 80; % Spurious free dynamic range >= 96 dB
Ts = 1/48000; % Sample rate 4K
dphi = pi/2; % Desired phase offset = pi/2;
Nacc = ceil(log2(1/(df*Ts))); %calculates bits for freq resolution
actdf = 1/(Ts*2^Nacc);  %resolution achieved
Nqacc = ceil((minSFDR-12)/6); %calculate quantized bits
phOffset = 2^Nacc*dphi/(2*pi); %calculate phase offset

% DSP system objects
%reading audio system objects
gafr = dsp.AudioFileReader('GuitarE4.wav', 'SamplesPerFrame', frameLength);
rafr = dsp.AudioFileReader('PianoE.wav', 'SamplesPerFrame', frameLength);
nafw = dsp.AudioFileWriter(newFile, 'SampleRate', rafr.SampleRate);
dw = audioDeviceWriter('SampleRate', rafr.SampleRate);
scope = dsp.TimeScope('SampleRate',rafr.SampleRate,'TimeSpan',0.1);

% FFT system objects
FFTY = dsp.FFT;
IFFTY = dsp.IFFT('FFTImplementation','Auto');
PEAKER = dsp.PeakFinder('PeakType', 'Maxima',...
    'PeakIndicesOutputPort', true,...
    'PeakValuesOutputPort', true,...
    'IgnoreSmallPeaks', true,...
    'PeakThreshold', 1);
MAXER = dsp.MovingMaximum('SpecifyWindowLength', true, 'WindowLength', 20);

%this is the oscillator system object
OSC = dsp.NCO('PhaseOffset', phOffset,...
    'NumDitherBits', 4, ...
    'NumQuantizerAccumulatorBits', Nqacc,...
    'SamplesPerFrame', 1/Ts, ...
    'CustomAccumulatorDataType', numerictype([],Nacc),...
    'SamplesPerFrame', frameLength);

%sends input signal to a specan
SAN = dsp.SpectrumAnalyzer('SampleRate', 1/Ts, ...
    'PlotAsTwoSidedSpectrum', false);

%book-keeping for the oscillator
window = 1;

while (~isDone(gafr) && ~isDone(rafr))
    % SETUP
    g = gafr();
    Fsg = gafr.SampleRate;
    r = rafr();
    Fsr = rafr.SampleRate;
    
    % FFT
    Gf = abs(FFTY(g(:,1)));    
    Rf = abs(FFTY(r));
    Rf1 = abs(FFTY(r(:,1)));    
    Rf2 = abs(FFTY(r(:,2)));    
    
    % HALF-SPECTRUMs used for pitch detection
    Gfpks = Gf(1:length(Gf)/2);
    Rfpks = Rf(1:length(Rf)/2);
    Rf1pks = Rf1(1:length(Rf1)/2);
    Rf2pks = Rf2(1:length(Rf2)/2);
    
    % FUNDAMENTAL / pitch detection
    gMovingMax = MAXER(Gfpks);
    gThresh = mean(gMovingMax); %figure out this threshold with SNR
    [gPeaks, gFreqs] = findpeaks(gMovingMax, 'MinPeakProminence', gThresh);
    gfdisc = round(mean(diff(gFreqs)));
    gF0 = round(gfdisc * Fsg / length(g));
    gF1 = round(gFreqs(2) * Fsg / length(g));
    gF2 = round(gFreqs(3) * Fsg / length(g));
    
%     [gCnt, gIdx, gVal] = PEAKER(Gfpks);
%     gfdisc_dup = round(mean(diff(gIdx)));
%     gF0_dup = round(gfdisc_dup * Fsg / length(g));
        
    rMovingMax = MAXER(Rf1pks);
    rThresh = mean(rMovingMax);
    [rPeaks, rFreqs] = findpeaks(rMovingMax, 'MinPeakProminence', rThresh);
    rfdisc = round(mean(diff(rFreqs)));
    rF0 = round(rfdisc * Fsr / length(r));
    
%     [rCnt, rIdx, rVal] = PEAKER(Rf1pks);
%     rfdisc_dup = round(mean(diff(rIdx)));
%     rF0_dup = round(rfdisc_dup * Fsr / length(r));

    % SUBSTITUTION & WRITE out
    %need to figure out how to control amplitude
    %need to figure out how to control time length of each harmonic
    F0 = int32(round(gF0*Ts*2^Nacc));
    H0 = gPeaks(1)*OSC(F0);
    
    F1 = int32(round(gF1*Ts*2^Nacc));
    H1 = gPeaks(2)*OSC(F1);
    
    F2 = int32(round(gF2*Ts*2^Nacc));
    H2 = gPeaks(3)*OSC(F2);
    
    Hsum(window:window+frameLength-1) = H0 + H1 + H2;
    window = window + frameLength;
end

%writes the audio
audiowrite(newFile, double(Hsum), Fsr);

release(FFTY); %this is needed to show the fft plot
test = abs(FFTY(Hsum));
figure(1)
plot(test);
figure(2)
plot(Hsum);

release(gafr);
release(rafr);
release(nafw);

% PLOTS
% time
% subplot(321);
% plot(g); % guitar
% grid on
% title('TIME: Guitar');
% xlabel('g(t)');
% 
% subplot(323);
% plot(r); % recorded sound
% grid on
% title('TIME: Recorded Sound');
% xlabel('r(t)');
% 
% subplot(325);
% plot(new); % new sound
% grid on
% title('TIME: New Sound');
% xlabel('n(t)');
% 
% % discrete frequency
% subplot(322);
% plot(Gf, 'LineWidth', 1.5); % guitar
% grid on
% title('FREQUENCY: Guitar');
% axis([0 8e3 0 1.25*max(gPeaks)]);
% xlabel('G(k)');
% 
% subplot(324);
% plot(Rf, 'LineWidth', 1.5); % recorded sound
% grid on
% title('FREQUENCY: Recorded Sound');
% axis([0 8e3 0 1.25*max(Rf1)]);
% xlabel('R(k)');
% 
% subplot(326);
% plot(Nf, 'LineWidth', 1.5); % new sound
% grid on
% title('FREQUENCY: New Sound');
% axis([0 8e3 0 1.25*max(Nf1)]);
% xlabel('N(k)');