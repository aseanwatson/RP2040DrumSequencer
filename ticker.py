from adafruit_ticks import ticks_ms, ticks_add, ticks_less

class ticker:
    # subdivide beats down to to 16th notes
    # Beat timing assumes 4/4 time signature, 
    # e.g. 4 beats per measure, 1/4 note gets the beat
    steps_per_beat = 4

    min_bpm = 10
    max_bpm = 400

    def __init__(self, bpm: int):
        self.set_bpm(bpm)
        self.restart()
        self.playing = False

    def play(self):
        if not self.playing():
            self.playing = True
            self.restart()

    def pause(self):
        self.playing = False

    def toggle_playing(self):
        if self.playing:
            self.pause()
        else:
            self.play()

    def restart(self) -> None:
        self.next_step = ticks_ms()

    def set_step_time(self, step_ms: int) -> None:
        delta = step_ms - self.step_ms
        self.step_ms = step_ms
        self.next_step = ticks_add(self.next_step, delta)
        # TODO: what do we do if the next_time is now in the past?
    
    def advance(self) -> bool:
        if ticks_less(ticks_ms(), self.next_step):
            # it's not time to advance
            return False

        self.next_step = ticks_add(self.next_step, self.ms_per_step)
        return True

    def set_bpm(self, bpm: int) -> None:
        self.bpm = min(max(bpm, ticker.min_bpm), ticker.max_bpm)
        seconds_per_beat = 60/bpm
        ms_per_beat = seconds_per_beat * 1000
        self.ms_per_step = ms_per_beat / ticker.steps_per_beat

    def adjust_bpm(self, adjustment: int) -> None:
        self.set_bpm(self.bpm + adjustment)

