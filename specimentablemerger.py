#!/usr/bin/env python3

import os
import sys
from library.gui_utils import *
from library.programstate import *
import tkinter.font as tkfont


format_dict = {
    "tab": TableFormat('\t'),
    "CSV (comma delimited)": TableFormat(','),
    "CSV (semicolon delimited)": TableFormat(';')
}


def gui_main() -> None:
    root = tk.Tk()
    root.title("Specimentablemerger")
    if os.name == "nt":
        root.wm_iconbitmap(os.path.join(sys.path[0], 'data', 'specimentablemerger_icon.ico'))

    style = ttk.Style()
    style.configure("MergeButton.TButton", background="blue")

    banner_frame = ttk.Frame(root)
    logo_image = tk.PhotoImage(file=os.path.join(sys.path[0], 'data', 'iTaxoTools Digital linneaeus MICROLOGO.png'))
    ttk.Label(banner_frame, image=logo_image).grid(row=0, column=0,sticky='nsw')
    ttk.Label(banner_frame, text="Tool to merge the content of tables based on specimen identifiers or species names", font=tkfont.Font(size=14)).grid(row=0, column=1, sticky='ws')

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

    fuzzy_merge_var = tk.BooleanVar()
    fuzzy_merge_chk = ttk.Checkbutton(root, text="Allow for common misspellings of merge value", variable=fuzzy_merge_var)
    fuzzy_merge_var.trace_add("write", lambda *_: programstate.set_fuzzy_merge(fuzzy_merge_var.get()))

    def merge() -> None:
        with display_errors_and_warnings():
            programstate.merger(input_chooser.file_list(),
                                output_chooser.file_var.get())
            tkmessagebox.showinfo("Done", "The merging has been completed")

    merge_btn = ttk.Button(root, text="Merge", command=merge, style="MergeButton.TButton")

    banner_frame.grid(row=0, column=0, columnspan=3, sticky='nsew')
    ttk.Separator(root, orient='horizontal').grid(row=1, column=0, columnspan=3, sticky='nsew')
    input_chooser.grid(row=2, column=0, sticky="nsew")
    output_chooser.grid(row=2, column=2, sticky="new")
    fuzzy_merge_chk.grid(row=3, column=0, sticky="nw")

    #padding
    ttk.Label(root).grid(row=4, column=0, pady=5)

    input_format_cmb.grid(row=4, column=0)
    output_format_cmb.grid(row=4, column=2)

    unifying_field_cmb.grid(row=4, column=1)

    merge_btn.grid(row=5, column=1)

    root.rowconfigure(2, weight=1)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(2, weight=1)

    root.mainloop()


def main() -> None:
    gui_main()


if __name__ == "__main__":
    main()
