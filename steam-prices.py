from csv import DictWriter
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from datetime import datetime
from bs4 import BeautifulSoup as bs4
from decorators.decorators import timeit


class Game ():
    def __init__(self, name='', price='', link='', review='', date='', discount=''):
        self.name = name
        self.price = price
        self.link = link
        self.review = review
        self.date = date
        self.discount = discount


# Global variables
games = []
pages_to_search = 2
money_type = 'R$'
page = 'topsellers'


def get_price(class_name, soup) -> str:
    value = soup.find(class_=class_name).getText().replace('\n', '').strip() or 'None'
    if money_type in value:
        value = value.split(money_type)
        del value[0]
        for index, _ in enumerate(range(len(value))):
            value[index] = f'{money_type}{value[index]}'
        if len(value) == 2:
            return f'{value[0]} --> {value[1]}'
        return value[0]
    else:
        return value


@timeit
def get_games():
    g = Game()
    browser = webdriver.Firefox()
    browser.get(f'https://store.steampowered.com/search/?filter={page}')

    # browser.find_element(
    #     By.XPATH, '/html/body/div[1]/div[7]/div[5]/div[1]/div[1]/div/div[1]/div[8]/a[1]').click()
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
            g.price = get_price('search_price', row)
            g.discount = get_price('search_discount', row)
            g.date = row.find(class_='search_released').getText()

            games.append(
                {
                    "name": g.name,
                    "price": g.price,
                    "discount": g.discount,
                    "release_date": g.date or 'Not Declared'
                }
            )
            print({
                "name": g.name,
                "price": g.price,
                "discount": g.discount,
                "release_date": g.date or 'Not Declared'
            })
        except IndexError:
            break
    print()
    print(f'{len(games)} games found!')


def current_date():
    return str(datetime.now()).split('.')[0].replace(' ', '_').replace(':', '-')


def export_csv():
    header_info = ['name', 'discount', 'price', 'release_date']
    with open(f'{page}-{current_date()}.csv', 'w') as csvfile:
        writer = DictWriter(csvfile, fieldnames=header_info)
        writer.writeheader()
        writer.writerows(games)


def page_chooser():
    print()
    print('Choose a page to search:')
    print('1 - Top Sellers (Default)')
    print('2 - New Releases')
    print('3 - Upcoming')
    print()

    choose = int(input('Selected number: ') or 1)
    if choose == 1:
        page = 'topsellers'
    elif choose == 2:
        page = 'newreleases'
    elif choose == 3:
        page = 'upcoming'
    else:
        page = 'topsellers'

    print()
    num_pages = int(
        input('Enter the numbers of pages to search (Default -> 2): ') or 2)
    return page, num_pages


if __name__ == '__main__':
    page, pages_to_search = page_chooser()
    get_games()
    export_csv()
