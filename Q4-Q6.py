from glob import glob
import librosa
import mir_eval
import utils
from tqdm import tqdm

DB = 'Ballroom'
if DB == 'SMC':
    FILES = glob(DB + '/SMC_MIREX_Audio//*.wav')
elif DB == 'JCS':
    FILES = glob(DB + '/JCS_audio//*.wav')

useMadmom = True
useDownBeat = True

if __name__ == '__main__':
    fScore = list()
    sum_f = 0.0
    cnt_f = 0.0
    if DB == 'Ballroom':
        GENRE = [g.split('/')[2] for g in glob(DB + '/wav/*')]

        for g in tqdm(GENRE):
            FILES = glob(DB + '/wav/' + g + '/*.wav')

            for f in FILES:
                f = f.replace('\\', '/')

                # Read the labeled tempo
                if not useDownBeat:
                    g_beats = utils.read_beatfile(DB, f)
                elif useDownBeat:
                    event_times, label = utils.read_downbeatfile(DB, f)

                # Beat tracking
                if useMadmom:
                    proc, act, timetag = utils.madMom(
                        useMadmom, useDownBeat, f)
                elif not useMadmom:
                    sr, y = utils.read_wav(f)
                    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
                    timetag = librosa.frames_to_time(beats, sr=sr)

                # F score
                if not useDownBeat:
                    f_measure = mir_eval.beat.f_measure(g_beats, timetag, 0.07)
                elif useDownBeat:
                    f_measure = mir_eval.beat.f_measure(event_times, timetag, 0.07)
                sum_f += f_measure
                cnt_f += 1.0

            fScore.append(sum_f/cnt_f)

        utils.getResultQ4Q6(GENRE, fScore)

    elif DB == 'SMC' or DB == 'JCS':

        for f in tqdm(FILES):
            f = f.replace('\\', '/')

            # Beat tracking
            if not useDownBeat:
                g_beats = utils.read_beatfile(DB, f)
            elif useDownBeat:
                event_times, labels = utils.read_downbeatfile(DB, f)

            if useMadmom:
                proc, act, timetag = utils.madMom(
                    useMadmom, useDownBeat, f)
            elif not useMadmom:
                sr, y = utils.read_wav(f)
                tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
                timetag = librosa.frames_to_time(beats, sr=sr)

            # F score
            if not useDownBeat:
                f_measure = mir_eval.beat.f_measure(g_beats, timetag, 0.07)
            elif useDownBeat:
                f_measure = mir_eval.beat.f_measure(event_times, timetag, 0.07)
            sum_f += f_measure
            cnt_f += 1.0

        fScore = sum_f/cnt_f

        print('F-score\t{:.2%}'.format(fScore))
