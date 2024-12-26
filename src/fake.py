from digitalio import Pull, DriveMode, Direction
try:
    from typing import Optional,Union,List,Tuple
except:
    pass

class DigitalInOut:
    def __init__(self):
        self.Direction = Direction.INPUT
        self.value = False
    def deinit(self) -> None:
        pass
    def __enter__(self):
        return self
    def __exit__(self) -> None:
        pass
    def __call__(self, *args, **kwds):
        return self.value
    def switch_to_output(self, value: bool = False, drive_mode: DriveMode = DriveMode.PUSH_PULL) -> None:
        self.value = value
        self.Direction = Direction.OUTPUT
        self.drive_mode = drive_mode
    def switch_to_input(self, pull: Optional[Pull] = None) -> None:
        self.Direction = Direction.INPUT
        self.pull = pull
    direction: Direction
    value: bool
    drive_mode: DriveMode
    pull: Optional[Pull]

class IncrementalEncoder:
    def __init__(self):
        self._position = 0
        pass
    @property
    def position(self):
        return self._position
    @position.setter
    def position(self, value):
        self._position = value

class HT16K33:
    def __init__(self) -> None:
        self._blink_rate = 0
        self._brightness = 1.0
        self._auto_write = True
    @property
    def blink_rate(self) -> int:
        return self._blink_rate
    @blink_rate.setter
    def blink_rate(self, rate: int) -> None:
        self._blink_rate = rate
    @property
    def brightness(self) -> float:
        return self._brightness
    @brightness.setter
    def brightness(self, brightness: float) -> None:
        self._brightness = brightness
    @property
    def auto_write(self) -> bool:
        return self._auto_write
    @auto_write.setter
    def auto_write(self, auto_write: bool) -> None:
        self._auto_write = auto_write
    def show(self) -> None:
        pass
    def fill(self, color: bool) -> None:
        pass

class Seg14x4(HT16K33):
    def __init__(self):
        super().__init__()
    def print(self, value: Union[str, float], decimal: int = 0) -> None:
        pass
    def print_hex(self, value: Union[int, str]) -> None:
        pass
    def __setitem__(self, key: int, value: str) -> None:
        pass
    def scroll(self, count: int = 1) -> None:
        pass
    def set_digit_raw(self, index: int, bitmask: Union[int, List[int], Tuple[int, int]]) -> None:
        pass
    def non_blocking_marquee(self, text: str, delay: float = 0.25, loop: bool = True, space_between: bool = False) -> bool:
        return False
    def marquee(self, text: str, delay: float = 0.25, loop: bool = True, space_between=False) -> None:
        pass