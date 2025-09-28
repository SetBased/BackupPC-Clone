from typing import Iterable, Union

from cleo.formatters.style import Style
from cleo.io.inputs.input import Input
from cleo.io.io import IO
from cleo.io.outputs.output import Output, Verbosity

from pystratum_backend.Helper.Terminal import Terminal


class CloneIO(IO):
    """
    Output style for BackupPC-Clone.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, input_object: Input, output_object: Output, error_output_object: Output):
        """
        Object constructor.

        :param input_object: The input object.
        :param output_object: The output object.
        """
        IO.__init__(self, input_object, output_object, error_output_object)

        # Create style titles.
        style = Style('yellow')
        self.output.formatter.set_style('title', style)
        self.error_output.formatter.set_style('title', style)

        # Create style for errors.
        style = Style(foreground='white', background='red')
        self.output.formatter.set_style('ERROR', style)
        self.error_output.formatter.set_style('ERROR', style)

        # Create style for warnings.
        style = Style(foreground='red')
        self.output.formatter.set_style('WARNING', style)
        self.error_output.formatter.set_style('WARNING', style)

        # Create style notes.
        style = Style('yellow', None, ['bold'])
        self.output.formatter.set_style('note', style)
        self.error_output.formatter.set_style('note', style)

        # Create style for database objects.
        style = Style('green', None, ['bold'])
        self.output.formatter.set_style('dbo', style)
        self.error_output.formatter.set_style('dbo', style)

        # Create style for file and directory names.
        style = Style('white', None, ['bold'])
        self.output.formatter.set_style('fso', style)
        self.error_output.formatter.set_style('fso', style)

        # Create style for SQL statements.
        style = Style('magenta', None, ['bold'])
        self.output.formatter.set_style('sql', style)
        self.error_output.formatter.set_style('sql', style)

    # ------------------------------------------------------------------------------------------------------------------
    def text(self, message: Union[str, Iterable[str]]) -> None:
        """
        Formats informational text.

        :param message: The message or messages.
        """
        if isinstance(message, list):
            messages = message
        else:
            messages = [message]

        for line in messages:
            self._output.write_line(' {0}'.format(line))

    # ------------------------------------------------------------------------------------------------------------------
    def listing(self, elements: Iterable[str]) -> None:
        """
        Writes a bullet list.

        :param elements: The items in the list.
        """
        elements = list(map(lambda element: ' * %s' % element, elements))

        self.output.write_line(elements)
        self.output.write_line('')

    # ------------------------------------------------------------------------------------------------------------------
    def log_verbose(self, message: Union[str, Iterable[str]]) -> None:
        """
        Logs a message only when logging level is verbose.

        :param message: The message or messages.
        """
        if self._output.verbosity.value >= Verbosity.VERBOSE.value:
            self.text(message)

    # ------------------------------------------------------------------------------------------------------------------
    def log_very_verbose(self, messages: Union[str, Iterable[str]]) -> None:
        """
        Logs a message only when logging level is very verbose.

        :param messages: The message or messages.
        """
        if self._output.verbosity.value >= Verbosity.VERY_VERBOSE.value:
            self.text(messages)

    # ------------------------------------------------------------------------------------------------------------------
    def __block(self, block_type: str, messages: Union[str, Iterable[str]]) -> None:
        """
        Writes a block message to the output.

        :param messages: The title of a section.
        """
        terminal_width = Terminal().width

        if not isinstance(messages, list):
            messages = [messages]

        lines = ['<{}></>'.format(block_type)]
        for key, message in enumerate(messages):
            if key == 0:
                text = ' [{}] {}'.format(block_type, self.output.formatter.format(message))
            else:
                text = ' {}'.format(self.output.formatter.format(message))
            line = '<{}>{}{}'.format(block_type, text, ' ' * (terminal_width - len(text)))
            lines.append(line)
        lines.append('<{}></>'.format(block_type))

        self.output.write_line(lines)

    # ------------------------------------------------------------------------------------------------------------------
    def error(self, messages: Union[str, Iterable[str]]) -> None:
        """
        Writes an error message to the output.

        :param messages: The title of a section.
        """
        self.__block('ERROR', messages)

    # ------------------------------------------------------------------------------------------------------------------
    def warning(self, messages: Union[str, Iterable[str]]) -> None:
        """
        Writes a warning message to the output.

        :param messages: The title of a section.
        """
        self.__block('WARNING', messages)

    # ------------------------------------------------------------------------------------------------------------------
    def title(self, title: str) -> None:
        """
        Writes a title to the output.

        :param title: The title of a section.
        """
        self.write_line(['<title>%s</>' % title, '<title>%s</>' % ('=' * len(title)), ''])


    # ------------------------------------------------------------------------------------------------------------------
    def sub_title(self, title: str) -> None:
        """
        Writes a title to the output.

        :param title: The title of a section.
        """
        self.write_line(['<title>%s</>' % title, '<title>%s</>' % ('-' * len(title)), ''])

# ----------------------------------------------------------------------------------------------------------------------
