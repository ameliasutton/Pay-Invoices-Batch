from invoicePayer import invoicePayer
import tkinter as tk
import sys
from logger import logger
import json

class popupWindow:
    def __init__(self, text):
        self.popup = tk.Tk()
        self.popup.wm_title("Popup Notice")
        self.popup.columnconfigure(0, minsize=100)
        self.popup.rowconfigure([0, 1], minsize=2)

        self.text_label = tk.Label(master=self.popup, text=text)
        self.text_label.grid(row=0, column=0)
        self.close_button = tk.Button(master=self.popup, text="OK", command=self.close)
        self.close_button.grid(row=1, column=0)

        self.popup.mainloop()

    def close(self):
        self.popup.destroy()

class inputSelectionMenu:
    def __init__(self, config ,log):
        self.config = config
        self.logger = log

        # Input Selection Menu Setup
        self.input = tk.Tk()
        self.input.wm_title("Mark Invoices as Paid")
        self.input.columnconfigure([0], minsize=150)
        self.input.rowconfigure([0], minsize=35)

        self.inCanvas = tk.Canvas(master=self.input)
        self.inCanvas.grid()

        self.inFrame = tk.Frame(master=self.inCanvas)
        self.inFrame.grid(row=0, column=0, sticky='nsew')

        # Title Label Setup
        self.title = tk.Label(master=self.inFrame, text='Voucher Number list, source selection',
                              font='TkDefaultFont 15 bold')
        self.title.grid(row=0, column=0, columnspan=3)
        self.generalPrompt = tk.Label(master=self.inFrame,
                                      text='This program marks the invoices attached to each voucher as paid.\n'
                                           'Choose one of the following options for Voucher Number list sourcing.',
                                      font='TkDefaultFont 10 italic')
        self.generalPrompt.grid(row=1, column=0, columnspan=3)

        # One-Click Option Setup
        self.one = tk.Label(master=self.inFrame, text='One-Click: ', font='TkDefaultFont 12 bold')
        self.one.grid(row=2, column=1)
        self.oneButton = tk.Button(master=self.inFrame, text='Read from \'input.txt\'',
                                   font='TkDefaultFont 10', command=self.oneStep)
        self.oneButton.grid(row=3, column=1)

        # Specified File Option Setup
        self.file = tk.Label(master=self.inFrame, text='Select from a different file:', font='TkDefaultFont 12 bold')
        self.file.grid(row=4, column=0, columnspan=3)
        self.filePrompt = tk.Entry(master=self.inFrame, font='TkDefaultFont 10')
        self.filePrompt.grid(row=5, column=0, columnspan=2)
        self.fileButton = tk.Button(master=self.inFrame, text='Use Specified File',
                                    font='TkDefaultFont 10', command=self.fileSelect)
        self.fileButton.grid(row=5, column=1, columnspan=2)

        # Text Option Setup
        self.text = tk.Label(master=self.inFrame, text='Input a list of Voucher Numbers:', font='TkDefaultFont 12 bold')
        self.text.grid(row=6, column=0, columnspan=3)
        self.textPrompt = tk.Label(master=self.inFrame, text='Please input Voucher Numbers separated by new lines.',
                                   font='TkDefaultFont 10')
        self.textPrompt.grid(row=7, column=0, columnspan=3)
        self.textField = tk.Text(master=self.inFrame)
        self.textField.grid(row=8, column=0, columnspan=3)
        self.textField.configure(height=10, width=25)
        self.fieldScroll = tk.Scrollbar(master=self.inFrame, orient='vertical', command=self.textField.yview)
        self.fieldScroll.grid(row=8, column=2, sticky='esn')
        self.textField['yscrollcommand'] = self.fieldScroll.set
        self.textButton = tk.Button(master=self.inFrame, text='Use Listed Voucher Numbers',
                                    font='TkDefaultFont 10', command=self.textSelect)
        self.textButton.grid(row=9, column=0, columnspan=3)

        # Menu Bar Setup
        self.menu_bar = tk.Menu(master=self.input)
        self.file_menu = tk.Menu(master=self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Exit", command=sys.exit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.input.config(menu=self.menu_bar)

        self.input.mainloop()

    def oneStep(self):
        identifier_list = []
        try:
            with open('input.txt', 'r') as inputFile:
                for line in inputFile:
                    identifier_list.append(int(line))
        except Exception as e:
            print(e)
            popupWindow(e)
        try:
            payer = invoicePayer(self.config, self.logger, identifier_list)
            print('\n****************************************************************************\n')
            print('OneStep Selected.')
            payer.batchPayInvoices()
            results = payer.results_dict
            print('Results:\n')
            print(json.dumps(results, indent=4))
            print('\n****************************************************************************\n')
            popupWindow("Batch invoice payment complete, see log for details")
            return 0
        except Exception as e:
            print(e)
            popupWindow(e)
            return -1

    def fileSelect(self):
        identifier_list = []
        try:
            with open(self.filePrompt.get(), 'r') as inputFile:
                for line in inputFile:
                    identifier_list.append(int(line))
        except Exception as e:
            print(e)
            popupWindow(e)
        try:
            payer = invoicePayer(self.config, self.logger, identifier_list)
            print('\n****************************************************************************\n')
            print('Named File Selected.')
            payer.batchPayInvoices()
            results = payer.results_dict
            print('Results:\n')
            print(json.dumps(results, indent=4))
            print('\n****************************************************************************\n')
            popupWindow("Batch invoice payment complete, see log for details")
            return 0
        except Exception as e:
            print(e)
            popupWindow(e)
            return -1

    def textSelect(self):
        print('Text Input Selected')
        input_data = self.textField.get('1.0', 'end')
        identifier_list = input_data.split('\n')
        identifier_list = list(filter(''.__ne__, identifier_list))
        try:
            identifier_list = list(map(int, identifier_list))
            if len(identifier_list) == 0:
                print('Input text box must not be empty.')
                popupWindow('Input text box must not be empty.')
                raise ValueError('Input text box must not be empty.')
        except ValueError:
            print('Input text must only consist of numbers and new lines.')
            popupWindow('Input text must only consist of numbers and new lines.')
        try:
            payer = invoicePayer(self.config, self.logger, identifier_list)
            print('\n****************************************************************************\n')
            print('Text Input Selected.')
            payer.batchPayInvoices()
            results = payer.results_dict
            print('Results:\n')
            print(json.dumps(results, indent=4))
            print('\n****************************************************************************\n')
            popupWindow("Batch invoice payment complete, see log for details")
            return 0
        except Exception as e:
            print(e)
            popupWindow(e)
            return -1


if __name__ == "__main__":
    logger = logger('mark_paid_log')
    print("Launching...")
    print('\n****************************************************************************\n')
    inputSelectionMenu('config.json', logger)

