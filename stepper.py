class stepper:
    """stepper class: Keeps track of which step we are on and what the range of steps are."""
    def __init__(self, num_steps: int):
        self.current_step = 0
        self.first_step = 0
        self.last_step = num_steps - 1
        self.stepping_forward = True
        self.num_steps = num_steps

    def advance_step(self) -> int:
        """advance_step(): moves to the next step (maybe backwards) and keeps the step in the allowed range."""
        if self.stepping_forward:
            if self.current_step < self.last_step:
                self.current_step = self.current_step + 1
            else:
                self.current_step = self.first_step
        else:
            if self.current_step > self.first_step:
                self.current_step = self.current_step - 1
            else:
                self.current_step = self.last_step
        return self.current_step

    def reverse(self) -> None:
        """reverse(): changes the direction we're stepping forward <==> backward."""
        self.stepping_forward = not self.stepping_forward

    def reset(self) -> None:
        """reset(): changes the direction we're stepping forward <==> backward."""
        self.current_step = self.first_step

    def adjust_range_start(self, adjustment: int) -> None:
        """adjust_range_start(adjustement): Updates the start of the range while keeping the number of steps constant.
        
        Ensures we keep the range valid; first_step can't be < 0 and last_step can't be >= num_steps."""
        adjustment = max(adjustment, -self.first_step)
        adjustment = min(adjustment, self.last_step - 1 - self.num_steps)
        self.first_step += adjustment
        self.last_step += adjustment
        # TODO: self.current_step might be out of range; leave that
        # as is; advance_step() will move it into the right range
        # eventually. We might want to revisit this.

    def adjust_range_length(self, adjustment: int) -> None:
        """adjust_range_start(adjustement): Updates the length of the range while keeping the first steps constant.
        
        Ensures we keep the range valid; last_step can't be < first_step and last_step can't be >= num_steps."""
        adjustment = max(adjustment, self.first_step - self.last_step)
        adjustment = min(adjustment, self.last_step - 1 - self.num_steps)
        self.last_step += adjustment
         # TODO: self.current_step might be out of range; leave that
        # as is; advance_step() will move it into the right range
        # eventually. We might want to revisit this.