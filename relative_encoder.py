import rotaryio

class relative_encoder:
    def __init__(self, encoder: rotaryio.IncrementalEncoder) -> None:
        self.encoder = encoder
        self.position = encoder.position
    
    def read_value(self) -> int:
        old_position = self.position
        self.position = self.encoder.position
        return self.position - old_position
