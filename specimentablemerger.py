#!/usr/bin/env python3

from library.gui_utils import *
from library.programstate import *


format_dict = {
    "tab": TableFormat('\t'),
    "CSV (comma delimited)": TableFormat(','),
    "CSV (semicolon delimited)": TableFormat(';')
}


def gui_main() -> None:
    root = tk.Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(2, weight=1)

    programstate = ProgramState()

    input_chooser = FileListChooser(root, label="Input files")
    output_chooser = FileChooser(root, label="Output file", mode="save")

    input_format_cmb = LabeledCombobox(
        root, label="Input files format", values=list(format_dict), readonly=True)
    output_format_cmb = LabeledCombobox(
        root, label="Ouput file format", values=list(format_dict), readonly=True)
    input_format_cmb.var.trace_add(
        "write", lambda *_: programstate.set_input_format(format_dict[input_format_cmb.var.get()]))
    output_format_cmb.var.trace_add(
        "write", lambda *_: programstate.set_output_format(format_dict[output_format_cmb.var.get()]))

    unifying_field_cmb = LabeledCombobox(root, label="Unifying field", values=[
        "specimenid", "species", "specimen_voucher", "locality"], readonly=False)
    unifying_field_cmb.combobox.current(0)
    unifying_field_cmb.var.trace_add(
        "write", lambda *_: programstate.set_unifying_field(unifying_field_cmb.var.get()))

    def merge() -> None:
        with display_errors_and_warnings():
            programstate.merger(input_chooser.file_list(),
                                output_chooser.file_var.get())
            tkmessagebox.showinfo("Done", "The merging has been completed")

    merge_btn = ttk.Button(root, text="Merge", command=merge)

    input_chooser.grid(row=0, column=0, sticky="nsew")
    output_chooser.grid(row=0, column=2, sticky="nsew")

    input_format_cmb.grid(row=1, column=0)
    output_format_cmb.grid(row=1, column=2)

    unifying_field_cmb.grid(row=1, column=1)

    merge_btn.grid(row=2, column=1)

    root.mainloop()


def main() -> None:
    gui_main()


if __name__ == "__main__":
    main()
