from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time 
import json
import argparse
import os


def get_products(page_url, save_directory, headless):    
    options = Options()
    options.add_argument('--log-level=3')
    if headless:
        options.add_argument('--headless')
        options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(page_url)
    driver.maximize_window()
    page_title = driver.title.split('-')[0]

    # Get the total scrollable height of the page
    total_height = driver.execute_script("return document.body.scrollHeight")

    # Define the number of steps to scroll
    num_steps = 15

    # Calculate the scroll height for each step
    step_height = total_height // num_steps

    # Scroll to each step
    for step in range(1, num_steps + 1):
        # Calculate the target scroll position
        scroll_position = step * step_height
        # Scroll to the target position 
        driver.execute_script(f"window.scrollTo(0, {scroll_position});")
    
    products = []
        
    btns = driver.execute_script('return document.getElementsByClassName("multi--item--3Tn_ffI multi--quickView--1LMw5TZ");')  
    for btn in btns:
        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", btn)
        time.sleep(1.5)
        btn.click()
        time.sleep(1.5)
        product = {
            'title': None,
            'info': None,
            'shipping': None,
            'current_price': None,
            'original_price': None,
            'colors': None,
            'sizes': None,
            'gallery': None
        }
        #extract data
        try:
            title = driver.execute_script("return document.getElementsByClassName('title--wrap--Ms9Zv4A')[0].innerText;")
            product['title'] = title
        except Exception as e:
            print(str(e))
        try:
            info = driver.execute_script("return document.getElementsByClassName('reviewer--wrap--sPGWrNq')[0].innerText;")
            product['info'] = info
        except Exception as e:
            print(str(e))
        try:
            shipping = driver.execute_script("return document.getElementsByClassName('shipping--wrap--Dhb61O7 pdp-disable-pointer')[0].innerText;")
            product['shipping'] = shipping
        except Exception as e:
            print(str(e))
        try:
            current_price = driver.execute_script("return document.getElementsByClassName('price--current--H7sGzqb')[0].innerText;")
            product['current_price'] = current_price
        except Exception as e:
            print(str(e))
        try:
            original_price = driver.execute_script("return document.getElementsByClassName('price--original--qDQaH8V')[0].innerText;")
            product['original_price'] = original_price
        except Exception as e:
            print(str(e))
        #get colors and sizes
        try:
            colors_section = driver.execute_script("return document.getElementsByClassName('sku-item--box--6Mh3HRv')[0].getElementsByTagName('img');")
            colors = {}
            for color in colors_section:
                colors[color.get_attribute('alt')] = color.get_attribute('src')
            product['colors'] = colors
        except Exception as e:
            print(str(e))
        try:
            sizes_section = driver.execute_script("return document.getElementsByClassName('sku-item--text--s0fbnzX');")
            sizes = []
            for size in sizes_section:
                sizes.append(size.get_attribute('title'))
            product['sizes'] = sizes
        except Exception as e:
            print(str(e))
        try:
            gallery_section = driver.execute_script("return document.getElementsByClassName('slider--wrap--PM2ajTZ')[0].getElementsByTagName('img');")
            gallery = []
            for img in gallery_section:
                gallery.append(img.get_attribute('src'))
            product['gallery'] = gallery
        except Exception as e:
            print(str(e))
        
        products.append(product)
        driver.execute_script('document.getElementsByClassName("comet-v2-modal-close")[0].click();')       
       
    save_path = os.path.join(save_directory, f'{datetime.now().strftime("%Y-%m-%d").replace("-", "_")}-{page_title}.json')
    with open(save_path, 'w') as f:
        json.dump(products, f, indent=4)
    return products, page_title
   
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape products from a given url.')
    parser.add_argument('url', type=str, help='url to the webpage containing the products')
    parser.add_argument('save_directory', type=str, help='directory to save the scraped data')
    parser.add_argument('--visible', action='store_true', help='Show the browser window')
    args = parser.parse_args()
    get_products(args.url, args.save_directory, not args.visible)
    
