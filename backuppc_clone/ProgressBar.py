import time

from cleo.io.io import IO
from cleo.io.outputs.output import Output
from cleo.ui.progress_bar import ProgressBar as CleoProgressBar


class ProgressBar(CleoProgressBar):
    """
    Customized version of Cleo's ProgressBar.
    """
    refresh_interval: int = 10
    """
    The refresh interval in seconds.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, io: IO | Output, maximum: int = 0):
        """
        Constructor.

        @param Output output: The output object.
        @param int maximum: Maximum steps (0 if unknown).
        """
        CleoProgressBar.__init__(self, io, maximum)

        self.__last_display: int = -1
        """
        The last epoch the progress bar was printed.
        """

        # Show now "0/max [>------] ) 0%" (instead of after step 1: "1/max [>------] 0% very long time".
        self.set_format(' %current%/%max% [%bar%] %percent:3s%%')
        self.set_progress(0)

        # Display the remaining time.
        self.set_format(' %current%/%max% [%bar%] %percent:3s%% %remaining%')

    # ------------------------------------------------------------------------------------------------------------------
    def finish(self) -> None:
        """
        Finish the progress output.
        """
        # Force set_progress to call the parent method.
        self.__last_display = -1

        # No more remaining time, display the total elapsed time.
        self.set_format(' %current%/%max% [%bar%] %percent:3s%% %elapsed%')

        CleoProgressBar.finish(self)
        self._io.write_line('')

    # ------------------------------------------------------------------------------------------------------------------
    def set_progress(self, step: int) -> None:
        """
        Sets the current progress.

        @param int step: The current progress.
        """
        if self._should_overwrite:
            now = time.time()
            if self.__last_display == -1 or (now - self.__last_display) > ProgressBar.refresh_interval:
                CleoProgressBar.set_progress(self, step)
                self.__last_display = now
            else:
                if self._max and step > self._max:
                    self._max = step
                elif step < 0:
                    step = 0
                self._step = step

        else:
            CleoProgressBar.set_progress(self, step)

# ----------------------------------------------------------------------------------------------------------------------
