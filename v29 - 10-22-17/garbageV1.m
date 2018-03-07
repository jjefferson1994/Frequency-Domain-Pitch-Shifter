%% 
% CHANGES:
% - replaced audioRead() => dsp.AudioFileReader()
% - dsp.AudioFileWriter()
% - used while-loop
% - normalized rPeaks values to prevent clipping?
%
% THINGS TO CONSIDER:
% - still need to consider how to generate new sound for preparation to DAC
% - frameLength
% - heightFactor
% - amplification Factor
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
clear all; close all;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% READ in sound files
guitarFile = 'GuitarE4.wav';
recordFile = 'PianoE.wav';
newFile = 'new_PianoE_GuitarE4.wav';
% [g, Fsg] = audioread(guitarFile); % guitar
% [r, Fsr] = audioread(recordFile); % recorded

frameLength = 1024*2^8; % NEED TO ADJUST FRAMELENGTH
% Look at the ringing in time domain of new sound plot

% CREATE dsp system objects (needed for R/W audio)
gafr = dsp.AudioFileReader(guitarFile, 'SamplesPerFrame', frameLength); % guitar
rafr = dsp.AudioFileReader(recordFile, 'SamplesPerFrame', frameLength); % recorded
nafw = dsp.AudioFileWriter(newFile, 'SampleRate', rafr.SampleRate); % new sound
adw = audioDeviceWriter('SampleRate', rafr.SampleRate); % play to sound card

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
while (~isDone(gafr) && ~isDone(rafr))
    g = gafr();
    Fsg = gafr.SampleRate; % guitar sampling rate
    
    r = rafr();
    Fsr = rafr.SampleRate; % recorded sample rate
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % FFT
    Gf = abs(fft(g(:,1)));
    Rf1 = abs(fft(r(:,1))); % channel 1, assume stereo
    Rf2 = abs(fft(r(:,2))); % channel 2
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % FUNDAMENTAL - findpeaks(), pitch detection
    heightFactor = 1/10;

    % guitar
    gHeight = max(Gf)*heightFactor;
    [gPeaks, gFreqs] = findpeaks(Gf, 'MinPeakProminence', gHeight);
    gfdisc = gFreqs(1); % discrete frequency
    gF0 = gfdisc * Fsg / length(g); % continuous frequency

    % recorded sound channel 1
    rHeight1 = max(Rf1)*heightFactor;
    [rPeaks1, rFreqs1] = findpeaks(Rf1, 'MinPeakProminence', rHeight1);
    rfdisc1 = rFreqs1(1); % discrete frequency
    rF0_1 = round( rfdisc1 * Fsr / length(r) ); % continuous frequency
    rPeaks1 = rPeaks1 ./ max(rPeaks1); % normalized

    %recorded sound channel 2
    rHeight2 = max(Rf2)*heightFactor;
    [rPeaks2, rFreqs2, rwidths2, rproms2] = findpeaks(Rf2, 'MinPeakProminence', rHeight2);
    rfdisc2 = rFreqs2(1); % discrete frequency
    rF0_2 = round( rfdisc2 * Fsr / length(r) ); % continous frequency
    rPeaks2 = rPeaks2 ./ max(rPeaks2); % normalized

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % SUBSTITUTION
    % width @ base of peaks
    width = round( (Fsr/2)/rfdisc1 ); % channel 1

    for n=1:round(length(Rf1)/rfdisc1)-1 % channel 1
       Nf1( n*gfdisc-width : n*gfdisc+width ) = Rf1( n*rfdisc1-width : n*rfdisc1+width );
       Nf2( n*gfdisc-width : n*gfdisc+width ) = Rf2( n*rfdisc2-width : n*rfdisc2+width );
    end

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % AMPLIFY
    amplify = 5; % MAY NEED TO SET = 1 FOR CONVERTING TO C, prevent clipping
    Nf1 = amplify.*Nf1; % amplify volume for channel 1
    Nf2 = amplify.*Nf2; % amplify volume for channel 2

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % WRITE out sound file
    new1 = real(ifft(Nf1));
    new2 = real(ifft(Nf2));
    new_sound = [new1(:), new2(:)]; % combine channels

    cutoff = round(min(length(Nf1)*(length(Nf1)/length(Rf1)), length(Rf1))); % channel 1 - determine duration of new sound
    new_sound = new_sound(1:cutoff,:); % resize duration of new sound

    nafw(new_sound); % write out to audio file (.wav)
    %adw(new_sound);

end % end while-loop

audiowrite('new_audiowrite.wav', new_sound, Fsr);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% RELEASE dsp system objects
release(gafr);
release(rafr);
release(nafw);
release(adw);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% PLOTS
% time
subplot(321);
plot(g); % guitar
grid on
title('TIME: Guitar');
xlabel('g(t)');

subplot(323);
plot(r); % recorded sound
grid on
title('TIME: Recorded Sound');
xlabel('r(t)');

subplot(325);
plot(new_sound); % new sound
grid on
title('TIME: New Sound');
xlabel('n(t)');

% discrete frequency
subplot(322);
plot(Gf, 'LineWidth', 1.5); % guitar
grid on
title('FREQUENCY: Guitar');
axis([0 12e3 0 1.25*max(gPeaks)]);
xlabel('G(k)');

subplot(324);
plot(Rf1, 'LineWidth', 1.5); % recorded sound
grid on
title('FREQUENCY: Recorded Sound');
axis([0 12e3 0 1.25*max(Rf1)]);
xlabel('R(k)');

subplot(326);
plot(Nf1, 'LineWidth', 1.5); % new sound
grid on
title('FREQUENCY: New Sound');
axis([0 12e3 0 1.25*max(Nf1)]);
xlabel('N(k)');