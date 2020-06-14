from glob import glob
import librosa
import utils
import madmom

useMadmom = True
DB = 'Ballroom'

if __name__ == '__main__':
    GENRE = [g.split('/')[2] for g in glob(DB + '/wav/*')]
    genres_p, genres_ALOTC = list(), list()

    window_size = 2048
    lw_sr = 25

    for g in GENRE:
        label, pred_t1, pred_t2, p_score, ALOTC_score = list(), list(), list(), list(), list()
        FILES = glob(DB + '/wav/' + g + '/*.wav')

        for f in FILES:
            f = f.replace('\\', '/')
            # Read the labeled tempo
            bpm = float(utils.read_tempofile(DB, f))
            label.append(bpm)

            # Estimate a static tempo
            sr, y = utils.read_wav(f)
            hop_size = sr // lw_sr

            if not useMadmom:
                oenv = librosa.onset.onset_strength(
                    y=y, sr=sr, hop_length=hop_size, n_fft=8096, win_length=window_size)

                tempo1, tempo2 = utils.tempo(
                    onset_envelope=oenv, sr=sr, hop_length=hop_size)
                tempo1 = 3 * tempo1
                tempo2 = 3 * tempo2
                pred_t1.append(tempo1)
                pred_t2.append(tempo2)
            elif useMadmom:
                proc = madmom.features.tempo.TempoEstimationProcessor(fps=100)
                act = madmom.features.beats.RNNBeatProcessor()(f)
                tempo1 = (proc(act)).astype(float)[0][0].item()
                tempo2 = (proc(act)).astype(float)[1][0].item()

            # p score
            s1 = tempo1/(tempo1+tempo2)
            s2 = 1.0 - s1
            p = s1 * utils.P_score(tempo1, bpm) + s2 * \
                utils.P_score(tempo2, bpm)
            p_score.append(p)

            # ALOTC score
            ALOTC = utils.ALOTC(tempo1, tempo2, bpm)
            ALOTC_score.append(ALOTC)

        p_avg = sum(p_score)/len(p_score)
        ALOTC_avg = sum(ALOTC_score)/len(ALOTC_score)
        genres_p.append(p_avg)
        genres_ALOTC.append(ALOTC_avg)

    utils.getResultQ1Q3(GENRE, genres_p, genres_ALOTC)
