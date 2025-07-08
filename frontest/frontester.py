from typing import Any, Optional

class Frontester:
    def __init__(self, strategy, data_source, execution_simulator, reporter):
        self.strategy = strategy
        self.data_source = data_source
        self.execution_simulator = execution_simulator
        self.reporter = reporter

    def run(self, config: Optional[dict] = None) -> Any:
        """Run the frontest (paper trading) and return results."""
        # 1. Connect to live data
        # 2. Apply strategy to generate signals
        # 3. Simulate execution (no real trades)
        # 4. Collect results
        # 5. Generate report
        pass 