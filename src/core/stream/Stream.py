from StreamSubscription import StreamSubscription

class Stream:
    def __init__(self):
        self.open = True
        self.subscriptions = []

    def listen(self, callback):
        sub = StreamSubscription(self, callback)
        self.subscriptions.append(sub)

    def send(self, data):
        if not self.open:
            return
        for sub in self.subscriptions:
            sub.send(data)

    def close(self):
        for sub in self.subscriptions:
            sub.cancel()