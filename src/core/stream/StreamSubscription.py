class StreamSubscription:
    def __init__(self, stream, callback):
        self.cancelled = False
        self.stream = stream
        self.callback = callback

    def send(self, data):
        if self.cancelled:
            return
        self.callback(data)

    def cancel(self):
        self.cancelled = True
        self.stream.subscriptions.remove(self)