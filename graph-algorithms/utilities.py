import time

class TicTac:
    """Simple class for timing execution."""

    def __init__(self):
        """Constructor."""
        self.timers = {}
        self.timers_ids_stack = []

    def tic(self):
        """Start timer."""
        if len(self.timers_ids_stack) != 0:
            new_id = 1 + self.timers_ids_stack[len(self.timers_ids_stack) - 1]
            self.timers_ids_stack.append(new_id)
            self.timers[new_id] = [time.perf_counter()]
        else:
            self.timers_ids_stack.append(0)
            self.timers[0] = [time.perf_counter()]

    def tac(self):
        """Stop the closest previously started timer."""
        if len(self.timers_ids_stack) != 0:
            current_id = self.timers_ids_stack.pop()
            self.timers[current_id].append(time.perf_counter())
            return (self.timers[current_id][1] - self.timers[current_id][0])