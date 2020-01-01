import datetime
from difflib import SequenceMatcher

import re
import requests

API_URL = 'https://bank.gov.ua/NBUStatService/v1/statdirectory/'


def get_current_info(currency):
    """Returns dictionary with info of given currency.
    Function is comparing currency value entered by user to API data,
    and returns full dictionary, where coincidence is found.
    Entered values can be alphabetical, numerical or full ukrainian name.
    For better search in full name is used SequenceMatcher, even if user entered name with few mistakes,
    it will find at least 75% coincidence.
    """
    info = requests.get(API_URL + 'exchange?json').json()
    if len(currency) == 3 and currency.isdigit() is False:
        for el in info:
            if currency.upper() == el['cc']:
                return el
    elif currency.isdigit() is True:
        for el in info:
            if int(currency) == int(el['r030']):
                return el
    elif len(currency) > 3:
        for el in info:
            if SequenceMatcher(a=currency.lower(), b=el['txt'].lower()).ratio() >= 0.75:
                return el
    return None


def get_info_by_date(currency, date):
    """Returns dictionary with info of given currency by given date"""
    if currency.isdigit() is False and len(currency) is 3:
        info = requests.get(API_URL + f'exchange?valcode={currency}&date={date_for_url(date)}&json').json()
        if info:
            return info[0]
        else:
            return None
    else:
        info = requests.get(API_URL + f'exchange?date={date_for_url(date)}&json').json()
        if currency.isdigit() is True:
            for el in info:
                if int(currency) == int(el['r030']):
                    return el
        elif len(currency) > 3:
            for el in info:
                if SequenceMatcher(a=currency.lower(), b=el['txt'].lower()).ratio() >= 0.75:
                    return el
        return None


def print_currency_info(currency_dict):
    """Prints data from obtained dictionaries"""
    print(f"Currency: {currency_dict['cc']}; \nRate: {currency_dict['rate']};" \
          f" \nDate: {currency_dict['exchangedate']}; \nUkrainian name: {currency_dict['txt']}.")


def get_clear_date(date_str):
    """Converts any style of entered date into correct datetime object"""
    clear_date = re.findall(r"[\d']+", date_str)
    try:
        return datetime.date(int(clear_date[2]), int(clear_date[1]), int(clear_date[0]))
    except ValueError:
        return None


def date_for_url(date_datetime):
    """Converts datetime object into string for easy inserting into url"""
    result_str = ''
    if len(str(date_datetime.year)) == 1:
        result_str += '000' + str(date_datetime.year)
    elif len(str(date_datetime.year)) == 2:
        result_str += '00' + str(date_datetime.year)
    elif len(str(date_datetime.year)) == 3:
        result_str += '0' + str(date_datetime.year)
    else:
        result_str += str(date_datetime.year)
    if len(str(date_datetime.month)) < 2:
        result_str += '0' + str(date_datetime.month)
    else:
        result_str += str(date_datetime.month)
    if len(str(date_datetime.day)) < 2:
        result_str += '0' + str(date_datetime.day)
    else:
        result_str += str(date_datetime.day)
    return result_str  # result should be like yearmonthday (20191231)


def get_sequence(currency, date_begin, date_end):
    """Returns sequence of changes of currency from entered start and end day by day"""
    result_list = []
    result_str = '0'
    if date_begin > date_end:
        return 'Wrong time direction'
    while date_begin <= date_end:
        element = get_info_by_date(currency, date_begin)
        if isinstance(element, dict):
            result_list.append(round(element['rate'], 2))
            date_begin += datetime.timedelta(days=1)
        else:
            return element  # returns 'no currency found'
    for el in range(len(result_list) - 1):
        result_str += ' ' + compare_currency(result_list[el], result_list[el + 1])
    return result_str  # result begins with 0 and step by step add increasing or decreasing comparing to previous


def compare_currency(first, second):
    """Returns difference between entered rates of currency"""
    if first > second:
        return '-' + f'{round(first - second, 2)}'
    elif first < second:
        return '+' + f'{round(second - first, 2)}'
    else:
        return '0'


if __name__ == "__main__":
    print('Enter currency. Alphabetical (like: EUR), numeral (like: 978) or full ukrainian name:')
    currency = input('>>> ')
    print('Select operation: \n1.Get current info \n2.Get info by date \n3.Get sequence of changing by dates')
    operation = input('>>> ')
    if operation is '1':
        result = get_current_info(currency)
        if result is None:
            print('No currency found')
        else:
            print_currency_info(result)
    elif operation is '2':
        date = get_clear_date(input('Enter date dd.mm.yyyy: \n>>> '))
        if date is None:
            print('Wrong date entered')
        else:
            result = get_info_by_date(currency, date)
            if result is None:
                print('No currency found')
            else:
                print_currency_info(result)

    elif operation is '3':
        date_start = get_clear_date(input('Enter start date dd.mm.yyyy: \n>>> '))
        if date_start is None:
            print('Wrong date entered')
        else:
            date_end = get_clear_date(input('Enter end date dd.mm.yyyy: \n>>> '))
            if date_end is None:
                print('Wrong date entered')
            else:
                sequence = get_sequence(currency, date_start, date_end)
                if sequence is None:
                    print('No currency found')
                else:
                    print(sequence)
    else:
        print('Wrong operation')
