from todo.models import Scheme, AMC
import datetime
from colorama import Fore, Back, Style, init

init(autoreset=True)


def analyze_pdf():

    # pdf2txt.py -o ../test.txt ../mycase2.pdf
    # qpdf --password=YOURPASSWORD-HERE --decrypt input.pdf output.pdf

    # pdf2txt.py -F 0 -W 10 -M 10 -L 10 -o ../test.txt ../mycase2-unsecure.pdf

    # Open a PDF file.
    doc = '/mnt/c/work/newdref/test.txt'

    text_file = open(doc, "r")

    amcs = AMC.objects.all()

    amc_names = []
    amc_name_map = {}

    for amc in amcs:
        amc_names.append(getattr(amc, "name"))
        amc_name_map[getattr(amc, "name")] = amc

        if "Kotak" in getattr(amc, "name"):
            amc_names.append("Kotak Mutual Fund")
            amc_name_map["Kotak Mutual Fund"] = amc

    lines = text_file.readlines()

    amc = False
    folio = False
    fund = False
    best_fund_match = False
    # since we don't always have all funds, we will keep text itself in case fund doesn't match
    trxs = []

    is_mf_block = False
    is_folio_block = False
    is_scheme_block = False

    is_transaction_start = False
    is_transaction_finish = False

    current_state = None
    allowed_states = ["MF", "FOLIO", "FUND", "TRX_START", "TRX_END"]

    trx_opening_balance = 0
    folio_trx_opening_balance = 0

    folio_line_no = 0

    # basically these are different states or "lines" we will encouter when we are processing the text file
    # in the above sequence
    i = 0
    while i < len(lines):

        line = lines[i].strip()
        if is_mf_line(line):

            if current_state == "FUND" or current_state == "TRX_START" or current_state == "TRX_END":
                print(
                    Fore.RED + "some issue we were not excpect mutual at this state: ", line)

            is_transaction_finish = True
            is_mf_block = False
            is_folio_block = False
            is_scheme_block = False
            is_transaction_start = False
            pass

        # first do a check i guess

        if is_mf_block == False:
            # till now we haven't even found an mf so first just search for mf
            if is_mf_line(line):
                # print(line)

                amc = False

                if line in amc_names:
                    print("#######   ", line, " ########")
                    amc = amc_name_map[line]
                    is_mf_block = True
                    current_state = "MF"
                else:
                    print(Fore.RED + "amc not found!!", line)
        else:
            # this mean's we have found an mutual fund.
            # now next lines in the text file will be related to folio and fund related

            if is_folio_block == False:

                if is_folio_line(line):

                    folio = False
                    fund = False
                    trxs = []
                    line = line.replace("Folio No:", "")
                    line = line.strip()
                    print("         folio no is ", line)
                    folio = line
                    is_folio_block = True
                    current_state = "FOLIO"

                    folio_line_no = i

            else:

                # folio is found next find scheme

                if is_scheme_block == False:
                    # we are assuming scheme should be found in max next 5 lines
                    # if not we will take up the best possible line match

                    if is_scheme_line(line) and i < folio_line_no + 5:
                        scheme_found = False
                        is_scheme_block = True
                        schemes = Scheme.objects.get_funds(amc=amc)
                        best_fund_match = line
                        for scheme in schemes:
                            name = getattr(scheme, "fund_name")

                            if name.lower() in line.lower():
                                print("                 ",
                                      name, " scheme found")
                                scheme_found = scheme
                                fund = scheme
                                break

                        current_state = "FUND"
                        if scheme_found == False:
                            print(
                                Fore.RED + "                 scheme not found! ", line)

                else:

                    if is_transaction_start == False:
                        if is_transaction_start_line(line):

                            trx_opening_balance = line.replace(
                                "Opening Unit Balance:", "")

                            val, t = extract_date_or_number(
                                trx_opening_balance)

                            trx_opening_balance = val
                            folio_trx_opening_balance = val

                            # transactions started
                            print("                         ",
                                  line, "transactions started")
                            is_transaction_start = True
                            is_transaction_finish = False
                            current_state = "TRX_START"

                    else:

                        trx_type = False  # manual

                        # trx type is AUTOMATIC means that its done by amc like phone update, email updated etc
                        # AUTOMATIC is usually maximum 2-3 lines and it has *** in it
                        # MANUAL means its done via investor like sip purchase and this is usually 6 lines

                        if len(line) > 1:
                            if line.startswith("Page"):
                                pass

                            if "***" in line or line == "Zero balance SIP":
                                if line == "Zero balance SIP":
                                    line = "***" + line

                                i = process_automatic_trx(line, lines, trxs, i)

                            else:
                                if is_trx_line(line):
                                    print("manual trx:", line)

                                    # we usually have 5 lines after this
                                    # 1. date
                                    # 2. amount (how much purchased)
                                    # 3. unit (how many units assigned by mf)
                                    # 4. price (price of per unit of mf i.e nav)
                                    # 5. unit balance (total balance of units)
                                    # problem is we don't in which order pdf gets parsed great! :)

                                    # picking up next 5 line
                                    try:
                                        trx_date = False
                                        trx_amount = 0
                                        trx_unit = 0
                                        trx_price = 0
                                        trx_balance = 0
                                        trx_amounts = []
                                        trx_type = ""

                                        # 95% of the cases it always just the next 5 line.
                                        # but one odd case sometimes its not e.g
                                        """
                                        Redemption - ELECTRONIC PAYMENT - via myCAMS Online -  UTR
                                        (14,178.91)
                                        27-Aug-2018
                                        18909270216 , less STT
                                        *** STT Paid ***
                                        27-Aug-2018
                                        0.14

                                        (570.907)

                                        24.836
                                        """
                                        no_data_found = 0
                                        max_data_points = 5

                                        for j in range(10):
                                            line = lines[i+1].strip()
                                            print("::::", line, "::::::")

                                            if "***" in line:
                                                i = process_automatic_trx(
                                                    line, lines, trxs, i + 1)
                                            else:
                                                val, t = extract_date_or_number(
                                                    line, False)
                                                if val != -1:
                                                    no_data_found += 1
                                                    if t == "date":
                                                        trx_date = val
                                                    else:
                                                        trx_amounts.append(val)
                                                else:
                                                    print(
                                                        "unable to identify will try nxt line", line)

                                                i += 1

                                            if no_data_found == max_data_points:
                                                break

                                        # no to identify
                                        # amount = unit * price

                                        # ok so to solve this i am using unit balance
                                        # basically if its a first transaction unit balance will be equal to unit so for first transaction two fields will be equal
                                        # and after that previous unit + current unit = new balance
                                        # or previous unit - current unit = balance
                                        # we need to consider opening balance as well. since its not always 0

                                        if trx_opening_balance == 0:
                                            # first transaction
                                            from collections import Counter
                                            dups = [k for k, v in Counter(
                                                trx_amounts).items() if v > 1]

                                            trx_balance = dups[0]
                                            trx_unit = dups[0]
                                            trx_type = "CREDIT"

                                        else:
                                            # opening balance + unit = final
                                            found = False
                                            for idx, org_amt in enumerate(trx_amounts):
                                                amt_credit = org_amt + trx_opening_balance
                                                amt_debit = trx_opening_balance - org_amt

                                                # find if this amount exists in list in approximation of 1

                                                for idx2, x in enumerate(trx_amounts):
                                                    if idx2 == idx:
                                                        continue
                                                    if abs(amt_credit - x) < 1 or abs(amt_debit - x) < .02:
                                                        # cool found uuuuuu!!!!

                                                        trx_balance = x
                                                        trx_unit = org_amt

                                                        if abs(amt_credit - x) < 1:
                                                            trx_type = "CREDIT"
                                                        else:
                                                            trx_type = "DEBIT"

                                                        found = True
                                                        break

                                                if found:
                                                    break

                                            if not found:
                                                print(trx_opening_balance)
                                                print(trx_amounts)
                                                print(Fore.RED +
                                                      "something went wrong when finding final unit balance")

                                                raise Exception(
                                                    "unable to find final unit balance")

                                        print("trx balance", trx_balance)
                                        print("trx unit", trx_unit)
                                        trx_amounts.remove(trx_balance)
                                        trx_amounts.remove(trx_unit)

                                        # print(trx_amounts[0] / trx_amounts[1])
                                        # print(trx_amounts[1] / trx_amounts[0])
                                        if abs(trx_unit - (trx_amounts[0] / trx_amounts[1])) < 1:
                                            trx_amount = trx_amounts[0]
                                            trx_price = trx_amounts[1]
                                        else:
                                            if abs(trx_unit - (trx_amounts[1] / trx_amounts[0])) < 1:
                                                trx_amount = trx_amounts[1]
                                                trx_price = trx_amounts[0]
                                            else:
                                                print(
                                                    Fore.RED + "not found amount and units !!!!!!!")
                                                raise Exception(
                                                    "unable to find amount and units")

                                        trx_opening_balance = trx_balance

                                        print("trx date", trx_date)
                                        print("trx amount", trx_amount)
                                        print("trx_price", trx_price)
                                        print("trx_unit", trx_unit)
                                        print("trx_balance", trx_balance)
                                        print("trx_type", trx_type)

                                        trxs.append({
                                            "type": "MANUAL",
                                            "name": line,
                                            "date": trx_date,
                                            "amount": trx_amount,
                                            "price_per_unit": trx_price,
                                            "unit": trx_unit,
                                            "unit_balance": trx_balance,
                                            "trx_type": trx_type
                                        })

                                    except Exception as e:
                                        raise Exception("ddd")
                                        print(Fore.RED + str(e))
                                        pass

                            print(
                                "                                              ", line)

                        # transaction started
                        if is_transaction_finish == False:
                            if is_transaction_finish_line(line):
                                current_state = "TRX_FINISH"
                                # transaction are finished

                                balance = line.replace(
                                    "Closing Unit Balance:", "")

                                val, t = extract_date_or_number(balance)

                                closing_balance = val

                                print("                         ",
                                      line, "transactions stoppped")
                                # we sould read and validations maybe to verify
                                is_transaction_finish = True
                                # is_mf_block = False  we cannot set this false because one mf has multiple folio

                                # lets recompile out data at this stage
                                balance = folio_trx_opening_balance

                                print("opening balanced: ", balance)
                                for trx in trxs:
                                    if trx["type"] == "MANUAL":
                                        print(trx)
                                        if trx["trx_type"] == "CREDIT":
                                            balance += trx["unit"]
                                        else:
                                            balance -= trx["unit"]

                                        print("balance: ",balance)

                                is_folio_block = False
                                is_scheme_block = False
                                is_transaction_start = False
                                trx_opening_balance = 0
                                if abs(balance - closing_balance) < 1:
                                    print("all good")
                                else:

                                    print(Fore.RED +
                                          "something wrong with trx balances not matching")
                                    raise Exception("xxxxxx")

                                    # if "PAN:" in line:
                                    #     line = line.replace("PAN:", "")
                                    #     line = line.strip()
                                    #     print("pan no is ", line)
        i += 1

    text_file.close()


def process_automatic_trx(line, lines, trxs, i):
    print("automatic trx:", line)

    if line.startswith("***"):
        indexL = 3
        indexR = len(line) - 3
        actual_trx = line[indexL:indexR]

        # picking up next line
        try:
            for j in range(2):
                line = lines[i+j+1].strip()
                val, trx_type = extract_date_or_number(
                    line)

                if trx_type == "date":
                    trx_date = val
                else:
                    trx_amount = val

            i += 2

            print("trx date", trx_date)
            print("trx value", trx_amount)

            trxs.append({
                "type": "AUTOMATIC",
                "name": actual_trx,
                "date": trx_date,
                "amount": trx_amount
            })

        except Exception as e:
            print(e)
            pass

    else:

        indexL = line.find("***")
        indexR = line.rfind("***")

        date = line[:indexL]
        print(date)
        if date == "Request":
            # edge case something this is just Request
            pass
        else:
            try:
                trx_date = datetime.datetime.strptime(
                    date, "%d-%b-%Y").date()
                actual_trx = line[indexL+3:indexR]
                print(
                    "actual trx", actual_trx.strip(), "on date ", trx_date)

                trxs.append({
                    "type": "AUTOMATIC",
                    "name": actual_trx,
                    "date": trx_date,
                    "amount": False
                })
            except ValueError as e:
                print(Fore.RED + str(e))
                trxs.append({
                    "type": "AUTOMATIC",
                    "name": actual_trx,
                    "date": False,
                    "amount": False
                })
                pass
    return i


def extract_date_or_number(line, throw_exception=True):
    if "-" in line:
        # its a date
        try:
            trx_date = datetime.datetime.strptime(line,
                                                  "%d-%b-%Y").date()
            return trx_date, "date"
        except:
            pass

    if "." in line:
        # its a number
        line = line.replace(",", "")
        line = line.replace("(", "")
        line = line.replace(")", "")
        trx_amount = float(line)

        return trx_amount, "number"
    if throw_exception:
        raise Exception("unable to identify")
    else:
        return -1, False


def is_mf_line(line):
    return "Mutual Fund" in line and "Advisor" not in line


def is_folio_line(line):
    return line.startswith("Folio No:")


def is_scheme_line(line):
    return "-" in line and ("Advisor" in line or "Regular" in line or "Direct" in line)


def is_transaction_start_line(line):
    return line.startswith("Opening Unit Balance")


def is_transaction_finish_line(line):
    return line.startswith("Closing Unit Balance")


def is_trx_line(line):
    return "Purchase" in line or "Redemption" in line or "Systematic" in line or "Switch" in line or "Dividend" in line or "SIP" in line or "Investment" in line or "Lateral" in line or "Exchange" in line
