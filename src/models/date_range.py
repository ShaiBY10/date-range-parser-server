class DateRange:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def to_dict(self):
        return {
            "start": self.start.isoformat(),
            "end": self.end.isoformat()
        }