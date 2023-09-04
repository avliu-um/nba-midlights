from scraper_util_avliu.util import get_soup, write_to_bucket, get_selenium_driver


def get_driver_write(url):
    driver = get_selenium_driver(undetected=True)
    driver.get(url)
    html = driver.page_source

    with open("./output.html", "w", encoding='utf-8') as file:
        # prettify the soup object and convert it into a string
        file.write(html)

    write_to_bucket('ev-cloud-testing', './output.html', 'test_write_output.html')


if __name__ == '__main__':
    get_driver_write('https://google.com')
