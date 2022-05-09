from csv import DictWriter
from subprocess import run
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from datetime import datetime
from bs4 import BeautifulSoup as bs4
from decorators.decorators import timeit
from selenium.webdriver.firefox.options import Options


class Game ():
    def __init__(self, name='', discounted_price='', link='', original_price='', date='', discount=''):
        self.name = name
        self.discounted_price = discounted_price
        self.link = link
        self.original_price = original_price
        self.date = date
        self.discount = discount


# Global variables
games = []
money_types = {
    "real": "R$",
    "dollar": "$"
}


Options = Options()
Options.headless = True


def define_money(value):
    money_type = None
    if money_types['real'] in value:
        money_type = money_types['real']
    elif money_types['dollar'] in value:
        money_type = money_types['dollar']
    return money_type


def get_price(class_name, soup, price_type=None) -> str:
    value = soup.find(class_=class_name).getText().replace(
        '\n', '').strip() or 'None'
    money_type = define_money(value)
    if money_type:
        value = value.split(money_type)
        del value[0]
        for index in range(len(value)):
            value[index] = f'{money_type}{value[index]}'
        if len(value) == 2:
            if price_type == 'discounted_price':
                return value[1]
            elif price_type == 'original_price':
                return value[0]
        elif price_type == 'original_price':
            return value[0]
        return '---'
    elif '%' or 'None' in value:
        return value
    else:
        raise Exception('Your money type is not supported currently')


@timeit
def get_games():
    g = Game()
    browser = webdriver.Firefox(options=Options)
    browser.get(f'https://store.steampowered.com/search/?filter={page}')

    for i in range(pages_to_search - 1):
        browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        sleep(0.8)

    offers = browser.find_elements(By.CLASS_NAME, 'search_results')[
        0].get_attribute('innerHTML')
    browser.close()
    soup = bs4(offers, 'html.parser')

    print()
    print(f'Parsing data from {pages_to_search * 50} games...')
    print()
    for i in range(pages_to_search * 50):
        try:
            row = soup.find_all(class_='search_result_row')[i]

            g.name = row.find(class_='title').getText()
            g.original_price = get_price('search_price', row, 'original_price')
            g.discounted_price = get_price(
                'search_price', row, 'discounted_price')
            g.discount = get_price('search_discount', row)
            g.date = row.find(class_='search_released').getText()

            games.append(
                {
                    "name": g.name,
                    "original_price": g.original_price,
                    "discounted_price": g.discounted_price,
                    "discount": g.discount,
                    "release_date": g.date or 'Not Declared'
                }
            )
            print(f'-> {g.name}')
        except IndexError:
            break
    print()
    print(f'{len(games)} games found!')


def current_date():
    return str(datetime.now()).split('.')[0].replace(' ', '_').replace(':', '-')


def sorted_games(arr):
    return sorted(arr, key=lambda k: k[sort_column])


def export_csv():
    header_info = ['name', 'discount', 'original_price',
                   'discounted_price', 'release_date']
    with open(file_name, 'w') as csvfile:
        writer = DictWriter(csvfile, fieldnames=header_info)
        writer.writeheader()
        writer.writerows(sorted_games(games))


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
    if choose_page == 1:
        page = 'topsellers'
    elif choose_page == 2:
        page = 'newreleases'
    elif choose_page == 3:
        page = 'upcoming'
    else:
        page = 'topsellers'

    separator()

    print('It will be sorted by:')
    print('1 - Discount (Default)')
    print('2 - Name')
    print()
    choose_sort = int(input('Selected number: ') or 1)
    if choose_sort == 1:
        sort_column = 'discount'
    elif choose_sort == 2:
        sort_column = 'name'
    else:
        sort_column = 'discount'

    separator()

    num_pages = int(
        input('Enter the numbers of pages to search (Default 5): ') or 5)

    separator()

    print('Gathering data from Steam...')
    return page, num_pages, sort_column


def ask_open():
    separator()
    open = input('Do you want to open the file? (Y/n)').lower() or 'y'
    if open == 'y' or open == 'yes':
        run(['xdg-open',  f'{file_name}'])
    else:
        separator()
        print(f'File saved as: {file_name}.csv')


if __name__ == '__main__':
    page, pages_to_search, sort_column = page_chooser()
    file_name = f'{page}-{current_date()}.csv'
    get_games()
    export_csv()
    ask_open()
