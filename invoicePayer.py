import json
import folio_api_aneslin as api
import requests
from logger import logger


class invoicePayer:

    def __init__(self, config: str, log: logger, identifiers: list[int] = None):
        self.log = log
        print('Initializing Invoice Payer...')
        if identifiers:
            self.identifiers = identifiers
        self.results_dict = {'Voucher Number': 'Result'}
        self.invoices = []

        # Read Config File
        self.configFileName = config
        try:
            with open(config, "r") as c:
                config = json.load(c)
                url = config["url"]
                tenant = config["tenant"]
                token = config["token"]
        except Exception as e:
            print(f"Config file \"{config}\" not found")
            raise e

        # Create Requester
        try:
            self.requester = api.requestObject(config["url"], config["tenant"])
            self.requester.setToken(config["token"])
            self.log.pauseLogging()
            self.requester.testToken()
            self.log.resumeLogging()
            self.__updateToken()

            # Create Session
            headers = {'Content-Type': 'application/json',
                       'x-okapi-tenant': config["tenant"],
                       'x-okapi-token': self.requester.token,
                       'Accept': 'application/json'}
            self.session = requests.Session()
            self.session.headers = headers
        except Exception as e:
            print(e)
            raise e

    def __updateToken(self) -> int:
        with open(self.configFileName, "r") as readConf:
            config = json.load(readConf)
        config["token"] = self.requester.token
        with open(self.configFileName, "w") as writeConf:
            writeConf.write(json.dumps(config, indent=4))
        print("Token in config is up to date.")
        return 0

    def __getInvoice(self, identifier: int) -> dict:
        response = self.requester.singleGet(f"invoice/invoices?query=voucherNumber="
                                            f"\"{str(identifier)}\"", self.session)
        if response["totalRecords"] == 1:
            return response["invoices"][0]
        else:
            return {}

    def __payInvoice(self, invoiceJson: dict) -> int:
        print(f"...FOLIO Invoice Number: {invoiceJson['folioInvoiceNo']}")
        if invoiceJson['status'] == "Paid":
            return -3
        elif invoiceJson["status"] != "Approved":
            return -2
        invoiceJson["status"] = "Paid"
        uuid = invoiceJson["id"]
        response = self.requester.put(f"invoice/invoices/{str(uuid)}", self.session, invoiceJson)
        if response == {}:
            return 0
        else:
            return -1

    def batchPayInvoices(self) -> int:
        if not self.identifiers:
            return -1
        print("Setting Invoices to Paid Status...")
        for item in self.identifiers:
            retrieved_invoice = self.__getInvoice(item)
            if retrieved_invoice == {}:
                self.results_dict[item] = "No Invoice Found Matching This Voucher Number"
            else:
                self.invoices.append(retrieved_invoice)
        for invoice in self.invoices:
            paid = self.__payInvoice(invoice)
            if paid == 0:
                self.results_dict[invoice["voucherNumber"]] = "Marked Paid"
            elif paid == -1:
                self.results_dict[invoice["voucherNumber"]] = "Request Failed, see above for details."
            elif paid == -2:
                self.results_dict[invoice["voucherNumber"]] = "Invoice has not been approved."
            elif paid == -3:
                self.results_dict[invoice["voucherNumber"]] = "Invoice has already been paid."
        return 0


if __name__ == "__main__":
    try:
        logger = logger('mark_paid_log')
        payer = invoicePayer('config.json', logger, [1096])
        payer.batchPayInvoices()
        results = payer.results_dict
        print('\n****************************************************************************\n')
        print('Results:\n')
        print(json.dumps(results, indent=4))
    except Exception as e:
        print(e)
        raise e
