%% Alpha 
% v1
% 
% really try to narrow it down to 8k not 48k
% fixed point vs. floating point
% create an oscillator to create the sound and just shift the amplitude and
% frequency
% trapezoidal interpolation going 50ms then move another 12.5 ms
% implement a hamming or hanning window
% at smaller time windows auto correlation will be faster
% matlab shifts the frequency to the next radix 
%down sample the 48k after filtering
% assume recorded sound is in stereo format (2-channel)
% pitch detection based on discrete frequency
% heights used for MinPeakProminence are hard-coded
% Too large of a width size lets in noise
% Keeping a small width size of 20 - 125
% still work on the scaling
% see if the fft is padding to 65535
% 50ms should be a 2000ish should have 10hz of resolution
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
clear all; close all;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% READ in sound files
guitarFile = 'GuitarE4.wav';
recordFile = 'PianoE.wav';
filename = 'new_sound_2_channel_piano.wav';
[g, Fsg] = audioread(guitarFile); % guitar
[r, Fsr] = audioread(recordFile); % recorded

% r(:,2) = r(:,1); assume stereo
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% FFT
Gf = abs(fft(g(:,1)));
Rf_1 = abs(fft(r(:,1))); % channel 1
Rf_2 = abs(fft(r(:,2))); % channel 2

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% FUNDAMENTAL - findpeaks(), pitch detection
% guitar
gHeight = max(Gf)/8;
[gPeaks, gFreqs, gwidths, gproms] = findpeaks(Gf, 'MinPeakProminence', gHeight, 'WidthReference','halfheight');
gfdisc = gFreqs(1); % discrete frequency
gF0 = gfdisc * Fsg / length(g); % continuous frequency
%
% recorded sound channel 1
rHeight_1 = max(Rf_1)/8;
[rPeaks_1, rFreqs_1, rwidths_1, rproms_1] = findpeaks(Rf_1, 'MinPeakProminence', rHeight_1);
rfdisc_1 = rFreqs_1(1); % discrete frequency
rF0_1 = round( rfdisc_1 * Fsr / length(r) ); % continuous frequency
%
%recorded sound channel 2
rHeight_2 = max(Rf_2)/8;
[rPeaks_2, rFreqs_2, rwidths_2, rproms_2] = findpeaks(Rf_2, 'MinPeakProminence', rHeight_2);
rfdisc_2 = rFreqs_2(1); % discrete frequency
rF0_2 = round( rfdisc_2 * Fsr / length(r) ); % continous frequency

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% SUBSTITUTION
% width @ base of peaks
width = round( (Fsr/2)/rfdisc_1 ); % channel 1

for n=1:round(length(Rf_1)/rfdisc_1)-1 % channel 1
   Nf_1( n*gfdisc-width : n*gfdisc+width ) = Rf_1( n*rfdisc_1-width : n*rfdisc_1+width );
   Nf_2( n*gfdisc-width : n*gfdisc+width ) = Rf_2( n*rfdisc_2-width : n*rfdisc_2+width );
end

Nf_1 = 5.*Nf_1; % amplify volume for channel 1
Nf_2 = 5.*Nf_2; % amplify volume for channel 2

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% WRITE out sound file
new_sound_1 = real(ifft(Nf_1));
new_sound_2 = real(ifft(Nf_2));
new_sound = [new_sound_1(:), new_sound_2(:)]; % combine channels

cutoff = min(length(Nf_1)*(length(Nf_1)/length(Rf_1)), length(Rf_1)); % channel 1 - determine duration of new sound
new_sound = new_sound(1:cutoff,:); % resize duration of new sound

audiowrite(filename, new_sound, Fsr);

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
axis([0 8e3 0 1.25*max(gPeaks)]);
xlabel('G(k)');

subplot(324);
plot(Rf_1, 'LineWidth', 1.5); % recorded sound
grid on
title('FREQUENCY: Recorded Sound');
axis([0 8e3 0 1.25*max(Rf_1)]);
xlabel('R(k)');

subplot(326);
plot(Nf_1, 'LineWidth', 1.5); % new sound
grid on
title('FREQUENCY: New Sound');
axis([0 8e3 0 1.25*max(Nf_1)]);
xlabel('N(k)');