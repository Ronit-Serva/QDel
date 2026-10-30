from .processor import Processor


class DarkStore:
    def __init__(self, env, num_processors, platform=None):
        self.env, self.platform = env, platform
        self.processors = self.create_processors(num_processors)

    def create_processors(self, n):
        if not isinstance(n, int) or n < 1:
            raise ValueError("At least one processor is required")
        return [Processor(self.env, self, f"P{i + 1:02d}") for i in range(n)]
