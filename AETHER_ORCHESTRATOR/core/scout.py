import numpy as np
from sklearn.ensemble import IsolationForest
from astroquery.ipac.nexsci.nasaexoplanetarchive import NasaExoplanetArchive

class AetherScout:
    def __init__(self):
        self.detector = IsolationForest(contamination=0.005, random_state=42)
        # Load known planets to filter them out
        self.known_planets = NasaExoplanetArchive.query_criteria(table="pscomppars", select="hostname")

    def is_known(self, target_name):
        return target_name in self.known_planets['hostname']

    def extract_features(self, lc):
        """Extracts entropy-based features to find truly irregular signals."""
        flux = lc.flux.value
        diff = np.diff(flux) # Rate of change
        return np.array([[np.mean(flux), np.std(flux), np.max(diff), np.min(diff)]])

    def scan(self, target_name, lc):
        if self.is_known(target_name):
            return None # Skip already discovered facts

        features = self.extract_features(lc)
        score = self.detector.fit(features).decision_function(features)
        
        # Lower score = Higher Anomaly
        if score < -0.1: 
            return {"target": target_name, "anomaly_score": score[0]}
        return None
    