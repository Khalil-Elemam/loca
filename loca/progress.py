
import sys
import time
import threading
from typing import Iterator, Any
from colorama import Fore, Style, init

init(autoreset=True)


class ProgressBar:
    """Simple progress bar for command line operations."""

    def __init__(self, total: int, description: str = "Processing", width: int = 50):
        self.total = total
        self.current = 0
        self.description = description
        self.width = width
        self.start_time = time.time()

    def update(self, amount: int = 1, item_name: str = ""):
        """Update progress by the given amount."""
        self.current += amount
        self._display(item_name)

    def _display(self, item_name: str = ""):
        """Display the current progress."""
        if self.total == 0:
            percent = 100
        else:
            percent = (self.current / self.total) * 100

        filled = (
            int(self.width * self.current // self.total)
            if self.total > 0
            else self.width
        )
        bar = "█" * filled + "░" * (self.width - filled)

        elapsed = time.time() - self.start_time
        if self.current > 0 and self.total > 0:
            eta = (elapsed / self.current) * (self.total - self.current)
            eta_str = f" ETA: {eta:.1f}s"
        else:
            eta_str = ""

        item_display = f" | {item_name[:30]}" if item_name else ""

        # Clear line and print progress

        sys.stdout.write(
            f"\r{Fore.CYAN}{self.description}{Style.RESET_ALL}: [{Fore.GREEN}{bar}{Style.RESET_ALL}] {Fore.YELLOW}{percent:.1f}%{Style.RESET_ALL} ({self.current}/{self.total}){Fore.MAGENTA}{eta_str}{Style.RESET_ALL}{item_display}"
        )
        sys.stdout.flush()

        if self.current >= self.total:
            print()  # New line when complete

    def finish(self):
        """Mark progress as complete."""
        self.current = self.total
        self._display()


class Spinner:
    """Threaded spinner for indeterminate progress."""

    def __init__(self, description: str = "Loading"):
        self.description = description
        self.chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.index = 0
        self.active = False
        self.thread = None
        self.start_time = None

    def _spin(self):
        """Background thread that animates the spinner."""
        while self.active:
            char = self.chars[self.index % len(self.chars)]
            sys.stdout.write(f"\r{Fore.YELLOW}{char} {Fore.CYAN}{self.description}{Style.RESET_ALL}")
            sys.stdout.flush()
            self.index += 1
            time.sleep(0.1)

    def __enter__(self):
        self.active = True
        self.start_time = time.time()
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.active = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=0.5)  # Don't wait too long
        
        # Clear spinner line
        sys.stdout.write("\r" + " " * (len(self.description) + 20) + "\r")
        sys.stdout.flush()
        
        # Print completion message
        elapsed = time.time() - self.start_time
        print(f"{Fore.GREEN}✓ {self.description} (completed in {elapsed:.2f}s){Style.RESET_ALL}")


def progress_iterator(
    iterable: Iterator[Any], description: str = "Processing"
) -> Iterator[tuple[Any, ProgressBar]]:
    """Wrap an iterable with a progress bar."""
    items = list(iterable)
    progress = ProgressBar(len(items), description)

    for item in items:
        yield item, progress
        progress.update()
