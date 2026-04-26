import atexit
import logging


class ErrorMonitor(logging.Handler):
    """
    V28: Sovereign Error Monitor
    Captures all ERROR level logs and displays a summary at the end of execution.
    """

    def __init__(self):
        super().__init__()
        self.errors = []
        self.printed = False
        self.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            self.errors.append(self.format(record))

    def print_summary(self):
        if self.printed:
            return

        if self.errors:
            # Clear some space
            print("\n" + "!" * 80)
            print("!!! SOVEREIGN ERROR SUMMARY DETECTED !!!".center(80))
            print(f"!!! FOUND {len(self.errors)} CRITICAL ERRORS DURING THIS RUN !!!".center(80))
            print("!" * 80)
            for i, err in enumerate(self.errors, 1):
                print(f"{i}. {err}")
            print("!" * 80 + "\n")

        # V28: Hardened Explicit Error Badge (always visible)
        print(f"Total [ERRORS] = {len(self.errors)}")
        self.printed = True


_MONITOR_INITIALIZED = False
_MONITOR_INSTANCE = None


def init_error_monitor():
    """
    V28 Hierarchy Leader: Error Monitoring initialization.
    Idempotent: Only registers the handler and atexit hook once.
    """
    global _MONITOR_INITIALIZED, _MONITOR_INSTANCE
    if _MONITOR_INITIALIZED:
        return _MONITOR_INSTANCE

    _MONITOR_INSTANCE = ErrorMonitor()
    # Add to root logger to capture errors from all modules
    logging.getLogger().addHandler(_MONITOR_INSTANCE)
    # Ensure it prints at the very end
    atexit.register(_MONITOR_INSTANCE.print_summary)

    _MONITOR_INITIALIZED = True
    return _MONITOR_INSTANCE


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    init_error_monitor()
    logging.info("Starting test...")
    logging.error("Test error 1: Database connection failed.")
    logging.error("Test error 2: API Rate limit hit.")
    print("Script finished normally, summary should follow.")
