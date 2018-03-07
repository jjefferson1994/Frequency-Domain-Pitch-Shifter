clear all;

guitarFile = 'GuitarE4.wav';
recordFile = 'PianoE.wav';
newFile = 'new_PianoE_GuitarE4.wav';
frameLength = 4096;

%variables for oscillator
sine1 = dsp.SineWave;
sine2 = dsp.SineWave;
sine3 = dsp.SineWave;

% DSP system objects
%reading audio system objects
gafr = dsp.AudioFileReader('GuitarE4.wav', 'SamplesPerFrame', frameLength);
rafr = dsp.AudioFileReader('PianoE.wav', 'SamplesPerFrame', frameLength);
afw = dsp.AudioFileWriter(newFile, 'SampleRate', rafr.SampleRate);
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
%     F0 = int32(round(gF0*Ts*2^Nacc));
%     H0 = rPeaks(1)*OSC(F0);
%     
%     F1 = int32(round(gF1*Ts*2^Nacc));
%     H1 = rPeaks(2)*OSC(F1);
%     
%     F2 = int32(round(gF2*Ts*2^Nacc));
%     H2 = rPeaks(3)*OSC(F2);
%     
%     Hsum(window:window+frameLength-1) = H0 + H1 + H2;
%     window = window + frameLength;
    window = window + 1;
end

sine1.Frequency = gF0;
sine1.Amplitude = rPeaks(1);
sine1.SamplesPerFrame = 4096*window;
sine1.SampleRate = 44100;
s1 = sine1();

sine2.Frequency = gF1;
sine2.Amplitude = rPeaks(2);
sine2.SamplesPerFrame = 4096*window;
sine2.SampleRate = 44100;
s2 = sine2();

sine3.Frequency = gF2;
sine3.Amplitude = rPeaks(3);
sine3.SamplesPerFrame = 4096*window;
sine3.SampleRate = 44100;
s3 = sine3();

newSine = s2;
afw(newSine); 

release(sine1);
release(sine2);
release(sine3);

%writes the audio
%audiowrite(newFile, double(Hsum), Fsr);
    
figure(1)
plot(newSine);

release(gafr);
release(rafr);
release(afw);

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