from scipy.io import wavfile as wav
import numpy as np
from librosa import core
from librosa.feature import tempogram
from librosa.util.exceptions import ParameterError
import mir_eval
import os
from prettytable import PrettyTable
import madmom

DEBUG = True

def madMom(useMadmom, useDownBeat, f):
    if not useDownBeat:
        proc = madmom.features.beats.BeatTrackingProcessor(fps=100)
        act = madmom.features.beats.RNNBeatProcessor()(f)
        timetag = proc(act)
    if useDownBeat:
        proc = madmom.features.downbeats.DBNDownBeatTrackingProcessor(beats_per_bar=[3, 4], fps=100)
        act = madmom.features.downbeats.RNNDownBeatProcessor()(f)
        timetag = np.array(proc(act))
        timetag = np.delete(timetag, np.s_[1::], 1).flatten()
    return proc, act, timetag


def getResultQ1Q3(GENRE, genres_p, genres_ALOTC):
    resultTB, overallResultTB = PrettyTable(), PrettyTable()
    resultTB.field_names = ['Genre', 'P-score', 'ALOTC score']
    if not DEBUG:
        for g in range(len(GENRE)):
            resultTB.add_row(['{:13s}'.format(GENRE[g]), '{:.2%}'.format(
                genres_p[g]), '{:.2%}'.format(genres_ALOTC[g])])
    elif DEBUG:
        for g in range(1):
            resultTB.add_row(['{:13s}'.format(GENRE[g]), '{:.2%}'.format(
                genres_p[g]), '{:.2%}'.format(genres_ALOTC[g])])

    overallResultTB.add_column('Overall P-score',
                               ['{:.2%}'.format(sum(genres_p)/len(genres_p))])
    overallResultTB.add_column('Overall ALOTC score',
                               ['{:.2%}'.format(sum(genres_ALOTC)/len(genres_ALOTC))])
    print(resultTB)
    print(overallResultTB)


def getResultQ4Q6(GENRE, genres_F):
    resultTB, overallResultTB = PrettyTable(), PrettyTable()
    resultTB.field_names = ['Genre', 'F-score']
    if not DEBUG:
        for g in range(len(GENRE)):
            resultTB.add_row(['{:13s}'.format(GENRE[g]), '{:.2%}'.format(
                genres_F[g])])
    elif DEBUG:
        for g in range(1):
            resultTB.add_row(['{:13s}'.format(GENRE[g]), '{:.2%}'.format(
                genres_F[g])])

    overallResultTB.add_column('Overall F-score',
                               ['{:.2%}'.format(sum(genres_F)/len(genres_F))])
    print(resultTB)
    print(overallResultTB)


def read_tempofile(DB, f):
    genre = f.split('/')[2]
    file_name = f.split('/')[3].replace('wav', 'bpm')
    tempo_file = DB + '/key_tempo/' + genre + '/' + file_name
    # print(tempo_file)
    with open(tempo_file, 'r') as f2:
        tempo = f2.read()
    return tempo


def read_beatfile(DB, f):
    global reference_beats

    if DB == 'Ballroom':
        genre = f.split('/')[2]
        file_name = f.split('/')[3].replace('wav', 'beats')
        beat_file = DB + '/key_beat/' + genre + '/' + file_name
        # print(beat_file)
        reference_beats, _ = mir_eval.io.load_labeled_events(beat_file)
        reference_beats = mir_eval.beat.trim_beats(reference_beats)
    elif DB == 'SMC':
        dirPath = r"SMC/SMC_MIREX_Annotations"
        result = [f for f in os.listdir(
            dirPath) if os.path.isfile(os.path.join(dirPath, f))]
        for i in range(len(result)):
            if f.split('SMC/SMC_MIREX_Audio/')[1].split('.wav')[0] in result[i]:
                reference_beats = mir_eval.io.load_events(
                    dirPath + '/' + result[i])
                break
    elif DB == 'JCS':
        dirPath = r"JCS/annotations"
        result = [f for f in os.listdir(
            dirPath) if os.path.isfile(os.path.join(dirPath, f))]
        for i in range(len(result)):
            if f.split('JCS/JCS_audio/')[1].split('.wav')[0] in result[i]:
                # print(result[i])
                reference_beats, _ = mir_eval.io.load_labeled_events(
                    dirPath + '/' + result[i])
                reference_beats = mir_eval.beat.trim_beats(reference_beats)
                break
    return reference_beats


def read_meterfile(DB, f, g_beats_len):
    if DB == 'JCS':
        dirPath = r"JCS/annotations"
        result = [f for f in os.listdir(
            dirPath) if os.path.isfile(os.path.join(dirPath, f))]
        for i in range(len(result)):
            if f.split('JCS/JCS_audio/')[1].split('.wav')[0] in result[i]:
                _, meters = mir_eval.io.load_labeled_events(
                    dirPath + '/' + result[i])
                break
        # fit the length of "mir_eval.beat.trim_beats"
        start_idx = len(meters) - g_beats_len
        return meters[start_idx:len(meters)]
    else:
        print('No use on this dataset.')


def read_downbeatfile(DB, f):
    if DB == 'JCS':
        dirPath = r"JCS/annotations"
        result = [f for f in os.listdir(
            dirPath) if os.path.isfile(os.path.join(dirPath, f))]
        for i in range(len(result)):
            if f.split('JCS/JCS_audio/')[1].split('.wav')[0] in result[i]:
                event_times, labels = mir_eval.io.load_labeled_events(
                    dirPath + '/' + result[i])
    elif DB == 'Ballroom':
        genre = f.split('/')[2]
        file_name = f.split('/')[3].replace('wav', 'beats')
        beat_file = DB + '/key_beat/' + genre + '/' + file_name
        event_times, labels = mir_eval.io.load_labeled_events(beat_file)
    return event_times, labels


def read_wav(f):
    """Read wav audio and reformat type.
    Read in wav file and reformat the data type to 32-bit floating-point. And
    then, flatten to mono if it was stereo.
    Args:
        f: The audio filename.
    Returns:
        sr: Sampling rate of wav file.
        y: Data read from wav file.
    """
    sr, y = wav.read(f)

    if y.dtype == np.int16:
        y = y / 2 ** (16 - 1)
    elif y.dtype == np.int32:
        y = y / 2 ** (32 - 1)
    elif y.dtype == np.int8:
        y = (y - 2 ** (8 - 1)) / 2 ** (8 - 1)

    if y.ndim == 2:
        y = y.mean(axis=1)
    return (sr, y)


def P_score(t, gt):
    if abs((gt - t) / gt) <= 0.08:
        p = 1.0
    else:
        p = 0.0
    return p


def ALOTC(t_1, t_2, gt):
    if abs((gt - t_1) / gt) <= 0.08 or abs((gt - t_2) / gt) <= 0.08:
        p = 1.0
    else:
        p = 0.0
    return p


def tempo(y=None, sr=22050, onset_envelope=None, hop_length=512, start_bpm=120,
          std_bpm=1.0, ac_size=8.0, max_tempo=320.0, aggregate=np.mean):

    if start_bpm <= 0:
        raise ParameterError('start_bpm must be strictly positive')

    win_length = np.asscalar(core.time_to_frames(ac_size, sr=sr,
                                                 hop_length=hop_length))

    tg = tempogram(y=y, sr=sr,
                   onset_envelope=onset_envelope,
                   hop_length=hop_length,
                   win_length=win_length)

    # Eventually, we want this to work for time-varying tempo
    if aggregate is not None:
        tg = aggregate(tg, axis=1, keepdims=True)

    # Get the BPM values for each bin, skipping the 0-lag bin
    bpms = core.tempo_frequencies(tg.shape[0], hop_length=hop_length, sr=sr)

    # Weight the autocorrelation by a log-normal distribution
    prior = np.exp(-0.5 * ((np.log2(bpms) - np.log2(start_bpm)) / std_bpm)**2)

    prior2 = np.argsort(prior, axis=0)
    prior2_idx = prior2[-2]

    # Kill everything above the max tempo
    if max_tempo is not None:
        max_idx = np.argmax(bpms < max_tempo)
        prior[:max_idx] = 0

    period = tg * prior[:, np.newaxis]
    best_period = np.argmax(period, axis=0)
    best_2 = np.argsort(period, axis=0)
    prior2_idx = best_2[-2]

    second_period = prior2_idx
    tempi = bpms[best_period]
    tempi2 = bpms[second_period]

    tempi[best_period == 0] = start_bpm
    tempi2[second_period == 0] = start_bpm
    return (tempi2.astype(float)[0].item(), tempi.astype(float)[0].item())


def trim_beatperbar(beat_and_bar):
    bar_idx = list((np.argwhere(beat_and_bar[:, 1] == '1')))

    start_idx = int(bar_idx[0])
    end_idx = int(bar_idx[-1])-1

    bar = beat_and_bar[start_idx:end_idx+1, 1]
    beat = beat_and_bar[start_idx:end_idx+1, 0]
    # print(bar)
    A = np.array(beat)[:, np.newaxis]
    B = np.array(bar)[:, np.newaxis]
    new_beat_and_bar = np.hstack((A, B))

    return new_beat_and_bar


def dynamic_beatperbar(beat_and_bar):
    bar_idx = np.argwhere(beat_and_bar[:, 1] == '1')
    bar_idx = bar_idx[:, 0]
    print(bar_idx)
    beat_per_bar = list()
    for i in range(len(bar_idx)-1):
        distance = bar_idx[i+1]-bar_idx[i]
        beat_per_bar.append(distance)
    print(beat_per_bar)
    return beat_per_bar
