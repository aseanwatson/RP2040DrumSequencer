class stepper:
    def __init__(self, num_steps: int):
        self.current_step = 0
        self.first_step = 0
        self.last_step = num_steps - 1
        self.stepping_forward = True
        self.num_steps = num_steps

    def advance_step(self) -> int:
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
        self.stepping_forward = not self.stepping_forward

    def reset(self) -> None:
        self.current_step = self.first_step

    def adjust_range_start(self, adjustment: int) -> None:
        # keep adjustment in the range where self.first_step >= 0 and
        # self.last_step < self.num_steps
        adjustment = max(adjustment, -self.first_step)
        adjustment = min(adjustment, self.last_step - 1 - self.first_step)
        self.first_step += adjustment
        self.last_step += adjustment
        # TODO: self.current_step might be out of range; leave that
        # as is; advance_step() will move it into the right range
        # eventually. We might want to revisit this.

    def adjust_range_length(self, adjustment: int) -> None:
        # keep adjustment in the range where self.first_step <= self.last_step and
        # self.last_step < self.num_steps
        adjustment = max(adjustment, self.first_step - self.last_step)
        adjustment = min(adjustment, self.last_step - 1 - self.first_step)
        self.last_step += adjustment
         # TODO: self.current_step might be out of range; leave that
        # as is; advance_step() will move it into the right range
        # eventually. We might want to revisit this.