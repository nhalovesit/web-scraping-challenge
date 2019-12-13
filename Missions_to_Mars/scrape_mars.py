from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt


def scrape():
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)

    news_title, news_par = mars_news(browser)

    # Run all scraping functions and store in dictionary.
    data = {
        "news_title": news_title,
        "news_paragraph": news_par,
        "featured_image": featured_image(browser),
        "hemispheres": hemispheres(browser),
        "weather": weather(browser),
        "facts": facts(),
        "date_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):
    browser.visit('https://mars.nasa.gov/news/')

    news = BeautifulSoup(browser.html, 'html.parser')

    # select the html that contains the title and paragraph
    first_element = news.select_one('ul.item_list li.slide div.list_text')
    # get the news title
    news_title = first_element.find("div", class_='content_title').get_text()
    # get the paragraph text
    news_par = first_element.find('div', class_="article_teaser_body").get_text()

    return news_title, news_par


def featured_image(browser):
    browser.visit('https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars')

    # find full image and click on it
    full_image = browser.find_by_id("full_image")
    full_image.click()

    # find 'more info' and click on it
    browser.is_element_present_by_text("more info", wait_time=1)
    more_info= browser.find_link_by_partial_text("more info")
    more_info.click()

    # parse the html
    img_bs= BeautifulSoup(browser.html, "html.parser")

    image_url = img_bs.select_one('figure.lede a img').get("src")

    # concatenate to get the full url 
    featured_image_url = 'https://www.jpl.nasa.gov' + image_url
    return featured_image_url
   


def hemispheres(browser):
    browser.visit("https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars")

    # Click the link, find the sample anchor, return the href
    hemisphere_image_urls = []
    for i in range(4):

        # Find the elements on each loop to avoid a stale element exception
        browser.find_by_css("a.product-item h3")[i].click()

        hemi_data = scrape_hemisphere(browser.html)

        # Append hemisphere object to list
        hemisphere_image_urls.append(hemi_data)

        # Finally, we navigate backwards
        browser.back()

    return hemisphere_image_urls


def weather(browser):
    browser.visit('https://twitter.com/marswxreport?lang=en')

    html = browser.html
    weather_data = BeautifulSoup(browser.html, 'html.parser')

    # get the first latest tweet data
    whole_tweet = weather_data.find('div', attrs={"class": "tweet", "data-item-id": "1198749371459870722"})

    # find the actual tweet
    mars_weather = whole_tweet.find('p', 'tweet-text').get_text()

    return mars_weather


def scrape_hemisphere(html_text):

    # Soupify the html text
    hemi_soup = BeautifulSoup(html_text, "html.parser")

    # Try to get href and text except if error.
    try:
        title_elem = hemi_soup.find("h2", class_="title").get_text()
        sample_elem = hemi_soup.find("a", text="Sample").get("href")

    except AttributeError:

        # Image error returns None for better front-end handling
        title_elem = None
        sample_elem = None

    hemisphere = {
        "title": title_elem,
        "img_url": sample_elem
    }

    return hemisphere


def facts():
    try:
        mars_data_df = pd.read_html('https://space-facts.com/mars/')[0]
    except BaseException:
        return None

    mars_data_df.columns = ['Description', 'Value']
    mars_data_df.set_index('Description', inplace=True)

    # Add some bootstrap styling to <table>
    return mars_data_df.to_html()


if __name__ == "__main__":
    print(scrape())
