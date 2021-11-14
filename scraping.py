# Import Splinter and BeautifulSoup, and pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    # initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now()
    }
    # stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    # optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # get the most recent news article and summary
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # try except to handle errors
    try:
        slide_elem = news_soup.select_one('div.list_text')
        slide_elem.find('div', class_='content_title')
        # extract the text from the other junk
        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()
        #get the teaser
        news_summary = slide_elem.find('div', class_='article_teaser_body').get_text()
    
    except AttributeError:
        return None, None
    
    return news_title, news_summary


def featured_image(browser):
    # visit url
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # grab the image data
    try:
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'
    return img_url


def mars_facts():

    try:
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]
    except BaseException:
        return None
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    return df.to_html(classes="table table-striped")


if __name__ == "__main__":
    # if running as script, print scraped data
    print(scrape_all())




