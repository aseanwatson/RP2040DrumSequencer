from adafruit_ticks import ticks_ms, ticks_add, ticks_less

class ticker:
    """The ticker class handles converting beats-per-minute into something you can poll for

    Example:
        myTicker = ticker(bpm = 60) # that will make a step every 250ms; 4 steps per beat

        myTicker.play()

        while True:
            if myTicker.advance():
                print("The beat goes on!")
    """
    # subdivide beats down to to 16th notes
    # Beat timing assumes 4/4 time signature, 
    # e.g. 4 beats per measure, 1/4 note gets the beat
    steps_per_beat = 4

    min_bpm = 10
    max_bpm = 400

    def __init__(self, bpm: int):
        self.set_bpm(bpm)
        self.playing = False

    def play(self) -> None:
        """Start playing. (Next call to advance() will return True.)"""
        if not self.playing():
            self.next_step = ticks_ms()
            self.playing = True

    def pause(self) -> None:
        """Stop playing."""
        self.playing = False

    def toggle_playing(self) -> None:
        """Toggle between playing/paused."""
        if self.playing:
            self.pause()
        else:
            self.play()

    def advance(self) -> bool:
        """If playing, see if it's time for the next step."""
        if not self.playing:
            return False

        if ticks_less(ticks_ms(), self.next_step):
            # it's not time to advance
            return False

        self.next_step = ticks_add(self.next_step, self.ms_per_step)
        return True

    def set_bpm(self, bpm: int) -> None:
        """Update the beat duration to match a certain beats-per-minute. 4 steps/beat."""
        self.bpm = min(max(bpm, ticker.min_bpm), ticker.max_bpm)
        seconds_per_beat = 60/bpm
        ms_per_beat = seconds_per_beat * 1000
        self.ms_per_step = ms_per_beat / ticker.steps_per_beat

    def adjust_bpm(self, adjustment: int) -> None:
        """Set the beats/minute in a relative way"""
        self.set_bpm(self.bpm + adjustment)

