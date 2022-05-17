from invoicePayer import invoicePayer
import tkinter as tk
import sys
from logger import logger
import json
import folio_api_aneslin as api
import requests

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
        try:
            input_file = open('input.txt', 'r')
            identifier_list = self.readInputFile(input_file)
        except Exception as e:
            print(e)
            popupWindow(e)
            return -1
        try:
            payer = invoicePayer(self.config, self.logger, identifier_list)
        except Exception as e:
            if e.args[0] == 'Token rejected, new login credentials required':
                loginMenu(self.config, self.logger, identifier_list, e.args[0])
            else:
                popupWindow(e)
        try:
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
        try:
            input_file = open(self.filePrompt.get(), 'r')
            identifier_list = self.readInputFile(input_file)
        except Exception as e:
            print(e)
            popupWindow(e)
            return -1
        try:
            payer = invoicePayer(self.config, self.logger, identifier_list)
        except Exception as e:
            if e.args[0] == 'Token rejected, new login credentials required':
                loginMenu(self.config, self.logger, identifier_list, e.args[0])
            else:
                popupWindow(e)
        try:
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
        except Exception as e:
            if e.args[0] == 'Token rejected, new login credentials required':
                loginMenu(self.config, self.logger, identifier_list, e.args[0])
            else:
                popupWindow(e)
        try:
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

    def readInputFile(self, input_file):
        identifier_list = []
        try:
            for line in input_file:
                try:
                    identifier_list.append(int(line))
                except Exception:
                    raise Exception('Input text file must consist only of numbers and new lines')
            if len(identifier_list) == 0:
                raise Exception('Input text file must not be empty.')
        except Exception as e:
            print(e)
            popupWindow(e)
            raise(e)
        return identifier_list


class loginMenu:
    def __init__(self, config, logger=None, idlist=None, prompt=None):
        if not prompt:
            prompt = 'Please Input API Login Credentials:'
        self.logger = logger
        self.idlist = idlist
        # Read Config File
        self.configFileName = config
        try:
            with open(config, "r") as c:
                config = json.load(c)
                url = config["url"]
                tenant = config["tenant"]
                token = config["token"]
        except ValueError:
            print(f"Config file \"{config}\" not found")
            popupWindow(f"Config file \"{config}\" not found")

        # Create Requester
        try:
            self.requester = api.requestObject(url, tenant)
            self.requester.setToken(token)

            # Create Session
            headers = {'Content-Type': 'application/json',
                       'x-okapi-tenant': config["tenant"],
                       'x-okapi-token': self.requester.token,
                       'Accept': 'application/json'}
            self.session = requests.Session()
            self.session.headers = headers
        except Exception as e:
            print(e)
            popupWindow(e)

        self.root = tk.Tk()
        self.root.rowconfigure([0, 1, 2, 3], minsize=10)
        self.root.columnconfigure([0, 1], minsize=10)

        self.prompt = tk.Label(master=self.root, text=prompt, font='TkDefaultFont 12 bold')
        self.prompt.grid(row=0, column=0, columnspan=2)

        self.userPrompt = tk.Label(master=self.root, text='Username: ', font='TkDefaultFont 10 bold')
        self.userPrompt.grid(row=1, column=0)

        self.userInput = tk.Entry(master=self.root)
        self.userInput.grid(row=1, column=1)

        self.passPrompt = tk.Label(master=self.root, text='Password: ', font='TkDefaultFont 10 bold')
        self.passPrompt.grid(row=2, column=0)

        self.passInput = tk.Entry(master=self.root, show='*')
        self.passInput.grid(row=2, column=1)

        self.submit = tk.Button(master=self.root, text='Submit', command=self.Submit)
        self.submit.grid(row=3, column=0, columnspan=2)

        self.root.mainloop()

    def Submit(self):
        username = self.userInput.get()
        password = self.passInput.get()
        try:
            self.requester.retrieveToken(username, password)
        except Exception as e:
            print(e)
            popupWindow(e)

        with open(self.configFileName, 'r') as old_config:
            config = json.load(old_config)
        config['token'] = self.requester.token
        with open(self.configFileName, 'w') as new_config:
            new_config.write(json.dumps(config, indent=4))

        print('Login Successful. Token Updated in config')
        self.root.destroy()
        popupWindow('Login Successful.\nToken Updated in config')



if __name__ == "__main__":
    logger = logger('mark_paid_log')
    print("Launching...")
    print('\n****************************************************************************\n')
    inputSelectionMenu('config.json', logger)

