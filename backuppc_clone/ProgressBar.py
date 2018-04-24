"""
BackupPC Clone
"""
import time

from cleo import ProgressBar as CleoProgressBar, Helper
from cleo.exceptions import CleoException


class ProgressBar(CleoProgressBar):
    """
    Customized version of Cleo's ProgressBar.
    """
    refresh_interval = 10
    """
    The refresh interval in seconds.

    :type: int
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, output, maximum=0):
        """
        Constructor.

        :param cleo.outputs.output.Output output: The output object.
        :param int maximum: Maximum steps (0 if unknown).
        """
        CleoProgressBar.__init__(self, output, maximum)

        self.__last_display = -1
        """
        The last epoch the progress bar was printed.

        :type: int
        """

        # Show now "0/max [>------] ) 0%" (instead of after step 1: "1/max [>------] 0% very long time".
        self.set_format(' %current%/%max% [%bar%] %percent:3s%%')
        self.set_progress(0)

        # Display the remaining time.
        self.set_format(' %current%/%max% [%bar%] %percent:3s%% %remaining%')

    # ------------------------------------------------------------------------------------------------------------------
    def finish(self):
        """
        Finish the progress output.
        """
        # Force set_progress to call the parent method.
        self.__last_display = -1

        # No more remaining time, display the total elapsed time.
        self.set_format(' %current%/%max% [%bar%] %percent:3s%% %elapsed%')

        CleoProgressBar.finish(self)
        self._output.writeln('')

    # ------------------------------------------------------------------------------------------------------------------
    def _formatter_remaining(self):
        """
        Bug fix, see https://github.com/sdispater/cleo/pull/53.

        :rtype: str
        """
        if not self._max:
            raise CleoException('Unable to display the remaining time if the maximum number of steps is not set.')

        if not self._step:
            remaining = 0
        else:
            remaining = (round((time.time() - self._start_time) / self._step * (self._max - self._step)))

        return Helper.format_time(remaining)

    # ------------------------------------------------------------------------------------------------------------------
    def set_progress(self, step):
        """
        Sets the current progress.

        :param int step: The current progress.
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
