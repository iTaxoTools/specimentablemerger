# /usr/bin/env python
import pandas as pd
import os
import re
from typing import Union, TextIO, List, Any, cast

fuzzy_merge_regex = re.compile(r'[- _./\\]+')


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

    def load_table(self, filepath: str) -> pd.DataFrame:
        with open(filepath, errors='replace') as infile:
            return pd.read_csv(infile, sep=self.sep).rename(
                    columns=str.casefold)

    def write_table(self, path_or_buf: Union[str, TextIO], table: pd.DataFrame) -> None:
        line_terminator = os.linesep if isinstance(path_or_buf, str) else "\n"
        table.to_csv(path_or_buf, sep=self.sep, index=False,
                     line_terminator=line_terminator)

def the_unique(column: pd.Series) -> Any:
    values = column.dropna()
    try:
        result: str = cast(str, values.iat[0])
    except IndexError:
        return None
    if values.eq(result).all():
        return result
    else:
        raise ValueError

def the_unique_fuzzy(column: pd.Series) -> Any:
    values = column.dropna()
    try:
        result: str = cast(str, values.iat[0])
    except IndexError:
        return None
    values = values.str.casefold().replace(fuzzy_merge_regex, "")
    first_value = fuzzy_merge_regex.sub("", result.casefold())
    if values.eq(first_value).all():
        return result
    else:
        raise ValueError


def merge_rows(rows: pd.DataFrame, column_name: str, fuzzy_merge: bool) -> pd.DataFrame:
    try:
        if fuzzy_merge:
            result = rows.agg(the_unique_fuzzy)
        else:
            result = rows.agg(the_unique)
    except ValueError:
        result = rows.copy()
        result['remarks'] = f"Rows for this {column_name} not merged due to multiple occurrences with non-identical content in one table"
    else:
        result = result.to_frame()
        if result.shape[1] == 1:
            result = result.T
        result['remarks'] = ""
    return result


class ProgramState():
    """
    The class encapsulating the state of specimentablemerger
    """

    def __init__(self) -> None:
        self.input_format: FileFormat = TableFormat("\t")
        self.output_format: FileFormat = TableFormat("\t")
        self.unifying_field = "specimenid"
        self.fuzzy_merge = False

    def set_input_format(self, format: FileFormat) -> None:
        self.input_format = format

    def set_output_format(self, format: FileFormat) -> None:
        self.output_format = format

    def set_unifying_field(self, field: str) -> None:
        self.unifying_field = field

    def groupby_value(self, table: pd.DataFrame) -> Union[str, pd.Series]:
        if not self.fuzzy_merge:
            return self.unifying_field
        return table[self.unifying_field].str.casefold().replace(fuzzy_merge_regex, "")

    def merger(self, input_files: List[str], output_file: str) -> None:
        table = pd.concat([self.input_format.load_table(filename)
                           for filename in input_files])
        output_table = table.groupby(self.groupby_value(table)).apply(
            merge_rows, self.unifying_field, self.fuzzy_merge)
        self.output_format.write_table(output_file, output_table)
