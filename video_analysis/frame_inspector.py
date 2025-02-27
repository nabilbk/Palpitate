import numpy as np
from scipy import signal
from collections import deque

TIME_SECOND_WINDOW = 4
FRAME_RATE = 30

# import matplotlib.pyplot as plt

class FrameInspector(object):
    """This class inspects the frame of a video, then produces spectrograms of the
    desired features of the frame"""

    def __init__(self, heartrates, show_spectrograms=False):
        self.show_spectrograms = show_spectrograms
        self.heartrates = heartrates
        self.frames_processed = 0
        self.data = None
        self.window = []

    def extract(self, roi):
        """roi is the sliced pixel of the face"""
        self.frames_processed += 1
        # get the greenpixels
        self.window.append(roi[:, :, 1].mean())

        if self.frames_processed == (FRAME_RATE * TIME_SECOND_WINDOW):
            self.process_data()

    def done(self):
        """Called when processing of a video is finished, flushes the window"""
        self.frames_processed = 0
        self.window = []

    def flush(self):
        """flushes data"""
        self.data = None

    def get_data(self):
        return self.data

    def process_data(self):
        """makes the spectrigrams and adds it to data"""
        self.frames_processed = 0
        window = self.window
        self.window = []

        f, t, spectrogram = signal.spectrogram(window, 30, nperseg=10, nfft=50, noverlap=5)
        # if self.show_spectrograms:
            # plt.pcolormesh(t, f, spectrogram)
            # plt.ylabel('Frequency [Hz]')
            # plt.xlabel('Time [sec]')
            # plt.show()

        # heartrate_for_window = self.heartrates[0:4].mean()
        heartrate_for_window = self.heartrates[0:4]

        # saftey measure to make sure that ffmpeg doesnt analyse a slice too much
        if len(heartrate_for_window) != TIME_SECOND_WINDOW:
            return

        self.heartrates = self.heartrates[4:]
        if self.data is None:
            self.data =(
                np.array([spectrogram]),
                np.array([heartrate_for_window]),
                [window]
            )
        else:
            (spectrograms, heartrates, time_series) = self.data
            spectrograms = np.append(spectrograms, [spectrogram], axis=0)
            heartrates = np.append(heartrates, [heartrate_for_window])
            time_series += [self.window]
            self.data = (spectrograms, heartrates, time_series)
