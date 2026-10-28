class StreamStatsError(Exception):
    pass

class IncorrectFormat(StreamStatsError):
    pass

class InvalidEvent(StreamStatsError):
    pass

class InvalidTimestamp(StreamStatsError):
    pass
