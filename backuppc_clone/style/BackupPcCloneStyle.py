"""
BackupPC Clone
"""
from cleo import Output
from cleo.styles import CleoStyle


class BackupPcCloneStyle(CleoStyle):
    """
    Output style for py-stratum.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, input_object, output_object):
        """
        Object constructor.

        :param cleo.inputs.input.Input input_object: The input object.
        :param cleo.outputs.output.Output output_object: The output_object object.
        """
        CleoStyle.__init__(self, input_object, output_object)

        # Create style notes.
        output_object.get_formatter().add_style('note', 'yellow', None, ['bold'])

        # Create style for data_layer objects.
        output_object.get_formatter().add_style('dbo', 'green', None, ['bold'])

        # Create style for file and directory names.
        output_object.get_formatter().add_style('fso', 'white', None, ['bold'])

        # Create style for SQL statements.
        output_object.get_formatter().add_style('sql', 'magenta', None, ['bold'])

    # ------------------------------------------------------------------------------------------------------------------
    def warning(self, message):
        """
        Writes a waring message.

        :param str|list[str] message: The message or list of messages.

        :return:
        """
        self.block(message, 'WARNING', 'fg=white;bg=red', padding=True)

    # ------------------------------------------------------------------------------------------------------------------
    def text(self, message):
        """
        Formats informational text.

        :param str|list[str] message: The message or list of messages.
        """
        if isinstance(message, list):
            messages = message
        else:
            messages = [message]

        for line in messages:
            self.writeln(' {0}'.format(line))

    # ------------------------------------------------------------------------------------------------------------------
    def log_verbose(self, message):
        """
        Logs a message only when logging level is verbose.

        :param str|list[str] message: The message.
        """
        if self.get_verbosity() >= Output.VERBOSITY_VERBOSE:
            self.writeln(message)

    # ------------------------------------------------------------------------------------------------------------------
    def log_very_verbose(self, message):
        """
        Logs a message only when logging level is very verbose.

        :param str|list[str] message: The message.
        """
        if self.get_verbosity() >= Output.VERBOSITY_VERY_VERBOSE:
            self.writeln(message)

# ----------------------------------------------------------------------------------------------------------------------
