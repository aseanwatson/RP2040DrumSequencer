import rotaryio

class relative_encoder:
    """relative_encoder: wraps an rotaryio.IncrementalEncoder to get relative adjustments"""
    def __init__(self, encoder: rotaryio.IncrementalEncoder) -> None:
        self.encoder = encoder
        self.position = encoder.position
    
    def read_value(self) -> int:
        """relative_encoder: wraps an rotaryio.IncrementalEncoder to get relative adjustments
        
        This calls encoder.position to poll the encoder; so it should be called frequently."""
        old_position = self.position
        self.position = self.encoder.position
        return self.position - old_position
