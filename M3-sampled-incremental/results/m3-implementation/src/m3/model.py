from time import perf_counter

from river import drift, tree

from m3.naive_bayes import likelihood


class OnlineDetector:
    def __init__(self, config):
        self.model = tree.HoeffdingAdaptiveTreeClassifier(
            grace_period=config.grace_period,
            seed=config.seed,
            drift_detector=drift.ADWIN(delta=config.drift_delta),
            nominal_attributes=["Proto"],
            max_size=100,
        )
        self.monitor = drift.ADWIN(delta=config.drift_delta)
        self.threshold = config.threshold
        self.naive_bayes = config.naive_bayes

    def predict(self, features):
        started = perf_counter()
        with likelihood(self.naive_bayes):
            probabilities = self.model.predict_proba_one(features)
        score = float(probabilities.get(1, 0.0))
        return int(score >= self.threshold), score, (perf_counter() - started) * 1000

    def learn(self, features, label, predicted, monitor=True):
        detected = False
        if monitor:
            self.monitor.update(int(label != predicted))
            detected = self.monitor.drift_detected
        with likelihood(self.naive_bayes):
            self.model.learn_one(features, label)
        return detected
