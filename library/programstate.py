# /usr/bin/env python
import pandas as pd
import os
from typing import Union, TextIO, List, Any


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


def the_unique(column: pd.Series) -> Any:
    result = column.dropna().unique()
    if len(result) == 0:
        return None
    elif len(result) == 1:
        return result.squeeze()
    else:
        raise ValueError


def merge_rows(rows: pd.DataFrame, column_name: str) -> pd.DataFrame:
    try:
        result = rows.agg(the_unique)
    except ValueError:
        result = rows.copy()
        result['remarks'] = f"Rows for this {column_name} not merged due to multiple occurrences with non-identical content in one table"
    else:
        result.to_frame().T
    return result


class ProgramState():
    """
    The class encapsulating the state of specimentablemerger
    """

    def __init__(self) -> None:
        self.input_format: FileFormat = TableFormat("\t")
        self.output_format: FileFormat = TableFormat("\t")
        self.unifying_field = "specimenid"

    def merger(self, input_files: List[str], output_file: str) -> None:
        table = pd.concat(self.input_format.load_table(filename)
                          for filename in input_files)
        output_table = table.groupby(self.unifying_field).apply(
            merge_rows, self.unifying_field)
        self.output_format.write_table(output_file, output_table)
