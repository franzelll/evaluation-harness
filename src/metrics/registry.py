class MetricsRegistry:
    def __init__(self):
        self._fns = {}

    def register(self, name, fn):
        self._fns[name] = fn

    def names(self):
        return list(self._fns.keys())

    def compute_all(self, source: str, hypothesis: str, refs):
        return {name: fn(source, hypothesis, refs) for name, fn in self._fns.items()}
