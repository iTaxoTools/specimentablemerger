# /usr/bin/env python
import pandas as pd
import os
from typing import Union, TextIO


class FileFormat():
    """
    Interface for file formats supported by the program
    """

    def load_table(self, filepath_or_buffer: Union[str, TextIO]) -> pd.DataFrame:
        raise NotImplementedError

    def write_table(self, path_or_buf: Union[str, TextIO], table: pd.DataFrame) -> None:
        raise NotImplementedError


class TableFormat(FileFormat):
    """
    Format for delimiter-separated table
    """

    def __init__(self, sep: str) -> None:
        self.sep = sep

    def load_table(self, filepath_or_buffer: Union[str, TextIO]) -> pd.DataFrame:
        pd.read_csv(filepath_or_buffer, sep=self.sep).rename(
            columns=str.casefold)

    def write_table(self, path_or_buf: Union[str, TextIO], table: pd.DataFrame) -> None:
        line_terminator = os.linesep if isinstance(path_or_buf, str) else "\n"
        table.to_csv(path_or_buf, sep=self.sep, index=False,
                     line_terminator=line_terminator)


class ProgramState():
    """
    The class encapsulating the state of specimentablemerger
    """

    def __init__(self) -> None:
        self.input_format = TableFormat("\t")
        self.output_format = TableFormat("\t")
