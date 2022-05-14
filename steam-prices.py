from csv import DictWriter
from subprocess import run
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from re import sub
from datetime import datetime
from bs4 import BeautifulSoup as bs4
from decorators.decorators import timeit
from selenium.webdriver.firefox.options import Options
from multiprocessing import Process, Queue


class Game:
    def __init__(self, name='', discounted_price='', link='', original_price='', date='', discount=''):
        self.name = name
        self.discounted_price = discounted_price
        self.link = link
        self.original_price = original_price
        self.date = date
        self.discount = discount


def define_money(value):
    for money in money_types_global.values():
        if money in value:
            return money
    return None


def get_price(class_name, soup, price_type=None) -> str:
    global money_type_global
    value = soup.find(class_=class_name).getText().replace(
        '\n', '').strip() or 'None'
    money_type = define_money(value)
    if money_type:
        value = value.split(money_type)
        del value[0]
        for index in range(len(value)):
            value[index] = f'{money_type}{value[index]}'
        if len(value) == 2:
            if price_type == columns_global['discounted_price']:
                return value[1]
        return value[0]
    elif '%' or 'None' in value:
        return value
    else:
        raise Exception('Your money type is not supported currently')


def get_item_soup(soup, initial_index, final_index):
    games_local = []
    for i in range(initial_index, initial_index + final_index):
        try:
            row = soup.find_all(class_='search_result_row')[i]

            g.name = row.find(class_='title').getText()
            g.original_price = get_price('search_price', row, 'original_price')
            g.discounted_price = get_price(
                'search_price', row, columns_global['discounted_price'])
            g.discount = get_price('search_discount', row)
            g.date = row.find(class_='search_released').getText()

            games_local.append(
                {
                    columns_global['name']: g.name,
                    columns_global['original_price']: g.original_price,
                    columns_global['discounted_price']: g.discounted_price,
                    columns_global['discount']: g.discount,
                    columns_global['release_date']: g.date or 'Not Declared'
                }
            )
            print(f'-> {g.name}')
        except IndexError:
            break
    q.put(games_local)


@timeit
def get_games():
    browser = webdriver.Firefox(options=Options)
    browser.get(f'https://store.steampowered.com/search/?filter={page}')

    for i in range(pages_to_search - 1):
        browser.execute_script(
            'window.scrollTo(0, document.body.scrollHeight);')
        sleep(0.8)

    offers = browser.find_elements(By.CLASS_NAME, 'search_results')[
        0].get_attribute('innerHTML')
    browser.close()
    soup = bs4(offers, 'html.parser')

    print()
    print(f'Parsing data from {pages_to_search * 50} games...')
    print()
    divisor = int((pages_to_search * 50) / threads_global)
    initial_index = []
    for i in range(threads_global):
        initial_index.append(int(i * divisor))
    threads = [Process(target=get_item_soup, args=(soup, initial_index[i], divisor)) for i in range(threads_global)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    for i in range(threads_global):
        for j in q.get():
            games_global.append(j)
    print()
    print(f'{len(games_global)} games found!')


def current_date():
    return str(datetime.now()).split('.')[0].replace(' ', '_').replace(':', '-')


def sorted_games(arr):
    if sort_column == columns_global['discounted_price']:
        return price_sorted(arr)
    return sorted(arr, key=lambda k: k[sort_column])


def price_sorted(arr):
    local_arr = [{'price': el[columns_global['discounted_price']], 'index': index}
                 for index, el in enumerate(arr)]
    for el in local_arr:
        el['price'] = int(sub('[a-zA-Z]+', '', el['price']
                              .replace('$', '')
                              .replace(',', '')
                              .replace('.', '')
                              .replace(' ', '')
                              .strip()) or 0
                          )
    local_arr = sorted(local_arr, key=lambda k: k['price'])
    final_arr = []
    for el in local_arr:
        final_arr.append(arr[el['index']])
    return final_arr


def remove_non_discounts(arr):
    for el in arr:
        if el[columns_global['original_price']] == el[columns_global['discounted_price']]:
            el[columns_global['discounted_price']] = '---'
    return arr


def export_csv():
    header_info = [
        columns_global['name'],
        columns_global['discount'],
        columns_global['original_price'],
        columns_global['discounted_price'],
        columns_global['release_date']
    ]
    header_info_print = {
        header_info[0]: 'Name',
        header_info[1]: 'Discount',
        header_info[2]: 'Original Price',
        header_info[3]: 'Discounted Price',
        header_info[4]: 'Release Date'
    }
    games_sorted = sorted_games(games_global)
    games_sorted = remove_non_discounts(games_sorted)
    games_sorted.insert(0, header_info_print)
    with open(file_name, 'w') as csvfile:
        writer = DictWriter(csvfile, fieldnames=header_info, delimiter=',')
        writer.writerows(games_sorted)


def separator():
    print()
    print('####################################################')
    print()


def page_chooser():
    print()
    print('Choose a page to search:')
    print('1 - Top Sellers (Default)')
    print('2 - New Releases')
    print('3 - Upcoming')
    print()
    choose_page = int(input('Selected number: ') or 1)
    page_local = page_types_global['top_sellers']
    if choose_page == 2:
        page_local = page_types_global['new_releases']
    elif choose_page == 3:
        page_local = page_types_global['upcoming']

    separator()

    print('It will be sorted by:')
    print('1 - Price (Default)')
    print('2 - Discount')
    print('3 - Name')
    print()
    choose_sort = int(input('Selected number: ') or 1)
    sort_column_local = columns_global['discounted_price']
    if choose_sort == 2:
        sort_column_local = columns_global['discount']
    elif choose_sort == 3:
        sort_column_local = columns_global['name']

    separator()

    num_pages = int(
        input('Enter the numbers of pages to search (Default 5): ') or 5)

    separator()

    print('Gathering data from Steam...')
    return page_local, num_pages, sort_column_local


def ask_open():
    separator()
    open_file = input('Do you want to open the file? (Y/n)').lower() or 'y'
    if open_file == 'y' or open_file == 'yes':
        run(['xdg-open', f'{file_name}'])
    else:
        separator()
        print(f'File saved as: {file_name}')


if __name__ == '__main__':
    # Global variables.
    games_global = []
    page_types_global = {
        'top_sellers': 'topsellers',
        'new_releases': 'newreleases',
        'upcoming': 'upcoming'
    }
    columns_global = {
        'name': 'name',
        'discount': 'discount',
        'original_price': 'original_price',
        'discounted_price': 'discounted_price',
        'release_date': 'release_date'
    }
    money_types_global = {
        'real': 'R$',
        'dollar': '$'
    }
    # Not much performance improvement having a value above 5.
    # The value has to be a multiple of 5.
    threads_global = 5

    g = Game()
    q = Queue()

    # Set browser to run in background.
    Options = Options()
    Options.headless = True

    # Main functions.
    page, pages_to_search, sort_column = page_chooser()
    file_name = f'{page}-{current_date()}.csv'
    get_games()
    export_csv()
    ask_open()
