import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from scipy.stats import entropy, skew
from scipy.fft import rfft


def spectral_entropy(signal):
    psd = np.abs(rfft(signal)) ** 2
    psd /= np.sum(psd) + 1e-12
    return entropy(psd)


def autocorr_decay(signal, threshold=0.2):
    signal = signal - np.mean(signal)
    corr = np.correlate(signal, signal, mode="full")
    corr = corr[corr.size // 2:]
    corr /= corr[0] + 1e-12
    return np.argmax(corr < threshold)


class AetherScout:
    def __init__(self):
        self.iso_forest = IsolationForest(
            contamination=0.005,
            n_estimators=300,
            random_state=42,
            n_jobs=-1
        )
        self.dbscan = DBSCAN(eps=0.7, min_samples=3)

        self._feature_buffer = []

    def calculate_entropy(self, flux):
        hist = np.histogram(flux, bins=32, density=True)[0] + 1e-12
        return entropy(hist)

    def extract_features(self, lc):
        flux = np.nan_to_num(lc.flux.value)

        diff = np.diff(flux)

        features = np.array([
            np.std(flux),
            skew(flux),
            np.std(diff),
            self.calculate_entropy(flux),
            spectral_entropy(flux),
            autocorr_decay(flux),
            np.var(flux - np.median(flux))
        ])

        return features

    def ingest(self, target_id, lc):
        features = self.extract_features(lc)
        self._feature_buffer.append((target_id, features))

    def finalize(self):
        ids, features = zip(*self._feature_buffer)
        X = np.vstack(features)

        iso_scores = -self.iso_forest.fit(X).decision_function(X)

        # Cluster validation: isolated but not clustered = interesting
        clusters = self.dbscan.fit_predict(X)

        results = []
        for i, score in enumerate(iso_scores):
            if score > np.percentile(iso_scores, 99) and clusters[i] == -1:
                results.append({
                    "id": ids[i],
                    "anomaly_score": float(score),
                    "classification": "APERIODIC_HIGH_ENTROPY_EVENT"
                })

        return results
