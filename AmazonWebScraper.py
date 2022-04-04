# Finding information about best sellers and most wished for in a given section say computers and accessories in the UK Amazon Store
# Based on selection, obtaining best seller data for the requested product such as laptops etc
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import uuid
from selenium.common.exceptions import NoSuchElementException
import os
import pandas as pd
import json
import urllib






class Amazon_UK_Scraper(): # Amazon
    
    # Methods --> Accept Cookies, Scrolling down, Clicking on next page until run out of pages
    
    def __init__(self, options, items): # options would be best sellers or most wished for
        # currently we will restrict items to be in either the Computer/Accessories section or Business/Science/Industry Section
        self.options = options.lower()
        self.items = items.lower()
        self.driver = ChromeDriverManager().install()
        
    def set_driver_url(self):
        url = "https://www.amazon.co.uk/"
        self.driver = webdriver.Chrome() 
        self.driver.get(url)
            
            
    def accept_cookies(self):

        time.sleep(1)
        try: # if cookies present
            self.driver.find_element(by=By.XPATH, value='//span[@class="a-button a-button-primary"]').click()
            time.sleep(1)

        except:
            pass
        
    def scroll_to_the_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        
    def get_links_on_a_page(self):
        
        link_list = []
        try:
            next_button = self.driver.find_element(by=By.XPATH, value='//li[@class="a-last"]')
            next_button.location_once_scrolled_into_view
            time.sleep(1)
            prop_container = self.driver.find_element(by=By.XPATH, value='//div[@class="p13n-gridRow _p13n-zg-list-grid-desktop_style_grid-row__3Cywl"]')
            prop_list = prop_container.find_elements(by=By.XPATH, value='./div[@id="gridItemRoot"]')
            
        except:
            print("Last page of products")
            previous_button = self.driver.find_element(by=By.XPATH, value='//li[@class="a-normal"]')
            time.sleep(1)
            # As the Next button is not visible anymore due it being the last page, we search for the previous button
            # Until that button is displayed, we keep scrolling to display all products on that given page
            previous_button.location_once_scrolled_into_view
            time.sleep(1)
            prop_container = self.driver.find_element(by=By.XPATH, value='//div[@class="p13n-gridRow _p13n-zg-list-grid-desktop_style_grid-row__3Cywl"]')
            prop_list = prop_container.find_elements(by=By.XPATH, value='./div[@id="gridItemRoot"]')
           
        for property in prop_list:
                a_tag = property.find_element(by=By.TAG_NAME, value='a')
                link = a_tag.get_attribute('href')
                link_list.append(link)
                
        return link_list
    
    
    def get_all_links(self):
        
        if self.options == "best seller":
            if self.items == "computer & accessories":
                
                self.driver.get('https://www.amazon.co.uk/Best-Sellers-Computers-Accessories/zgbs/computers/ref=zg_bs_nav_0')
                time.sleep(1)
                
        elif self.options == "most wished for":   
            if self.items == "computer & accessories":
                
                self.driver.get('https://www.amazon.co.uk/gp/most-wished-for/computers/ref=zg_mw_nav_0')
                time.sleep(1)   
            
        big_list = []
        
        for i in range(2):
            
            l = self.get_links_on_a_page()
            big_list.extend(l)
            try:
                time.sleep(2)
                button = self.driver.find_element(by=By.XPATH, value='//li[@class="a-last"]')
                element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable(button))
                element.click()
                time.sleep(1)
                
            except:
                break
                
                
        return big_list
    
    
    def unique_id_gen(self, value):
        

        product_id = value[value.find('pd_rd_i')+8: -6]
            
        return str(product_id)
    
    
    def v4_uuid(self):
        
        
        uuid_4 = uuid.uuid4()
            
        return str(uuid_4)  

        
    def retrieve_details_from_a_page(self):
        
        # Title of the product
        
        try:
            title = self.driver.find_element(By.XPATH, '//span[@id="productTitle"]').text
        except NoSuchElementException:
            title = 'N/A'
        
        # Price of the product
        try:
            price = self.driver.find_element(By.XPATH, '//span[@id="priceblock_ourprice"]').text
        
        except:
            price = 'N/A'  # Different products have prices shown on different locations (normally it could be three places, hence we use the try except statement)
            
        if price == 'N/A':
            try:
                price = self.driver.find_element(By.XPATH, '//span[@class="a-price aok-align-center reinventPricePriceToPayPadding priceToPay"]').text.replace('\n', '.')
            except:
                price = self.driver.find_element(By.XPATH, '//td[@class="a-span12"]').text

        # Similar to price, we find the same problems with Brand, Voucher, Promotion and hence we perform multiple try except statements
            
        # Brand
        try:
            brand = self.driver.find_element(By.XPATH, '//tr[@class="a-spacing-small po-brand"]').text.split(' ')[1]
        except NoSuchElementException:
            brand = 'N/A'
        # Voucher available
        
        try:
            voucher = self.driver.find_element(By.XPATH, '//div[@data-csa-c-slot-id="promo-cxcw-0-0"]').text
        except NoSuchElementException:
            voucher = 'N/A'
            
        # Percentage reduction in price
        
        try:
            price_override = self.driver.find_element(By.XPATH, '//span[@class="a-size-large a-color-price savingPriceOverride aok-align-center reinventPriceSavingsPercentagePadding savingsPercentage"]').text
            
        except:
            price_override = 'N/A'
            
        if price_override == 'N/A':
            try:
                price_override = self.driver.find_element(By.XPATH, '//td[@class="a-span12 a-color-price a-size-base priceBlockSavingsString"]').text
            except:
                price_override = 'N/A'
                
        if price_override == 'N/A':
            try:
                price_override = self.driver.find_element(By.XPATH, '//td[@class="a-span12 a-color-price a-size-base"]').text
            except NoSuchElementException:
                price_override = 'N/A'
            
        # Review ratings
        
        review_ratings = self.driver.find_element(By.XPATH, '//span[@class="a-size-medium a-color-base"]').text
        
        # Number of ratings
        
        global_ratings = self.driver.find_element(By.XPATH, '//div[@data-hook="total-review-count"]').text
        
        # Review topics
        
        topics_review = self.driver.find_element(By.XPATH, '//div[@data-hook="lighthut-terms-list"]').text
        
        # Most helpful review
        
        review_helpful = self.driver.find_element(By.XPATH, '//div[@class="a-section review aok-relative"]').text
        
        # Main Image Link
        
        src = self.driver.find_element(By.XPATH, '//div[@class="imgTagWrapper"]').find_element(By.TAG_NAME, 'img').get_attribute('src')
    
    
        return title, price, brand, voucher, price_override, review_ratings, global_ratings, topics_review, review_helpful, src
  
if __name__ == '__main__':
    
    scraper = Amazon_UK_Scraper("Best Seller", "Computer & Accessories")
    scraper.set_driver_url()
    scraper.accept_cookies()
    links = scraper.get_all_links()
    # prod_ids = scraper.unique_id_gen(links)
    
    prop_dict = {
        
        'UUID': [],
        'Unique Product ID': [],
        
        'Title': [],
        'Price': [],
        'Brand': [],
        'Savings/Promotion': [],
        'Voucher': [],
        
        'Review Ratings': [],
        'Global Ratings': [],
        'Topics in Reviews': [],
        
        'Most Helpful Review': [],
        'Image link': [],
        'Page Link': []

        
        }
    
    for link in links[0:5]:
        
        scraper.driver.get(link)
        time.sleep(1)
        scraper.scroll_to_the_bottom()
        time.sleep(2)
        prop_dict['Page Link'].append(link)
        prop_dict['UUID'].append(scraper.v4_uuid())
        prop_dict['Unique Product ID'].append(scraper.unique_id_gen(link))
        
        
        title, price, brand, voucher, price_override, review_ratings, global_ratings, topics_review, review_helpful, src = scraper.retrieve_details_from_a_page()
        
        prop_dict['Title'].append(title)
        prop_dict['Price'].append(price)
        prop_dict['Brand'].append(brand)
        prop_dict['Voucher'].append(voucher)
        prop_dict['Savings/Promotion'].append(price_override)
        prop_dict['Review Ratings'].append(review_ratings)
        prop_dict['Global Ratings'].append(global_ratings)
        prop_dict['Topics in Reviews'].append(topics_review)
        prop_dict['Most Helpful Review'].append(review_helpful)
        prop_dict['Image link'].append(src)
        
        
    
    try:
        os.mkdir("raw_data")
    except:
        print("Directory already exists")
        
    
    
    os.chdir('raw_data')
    directory = os.getcwd()
    filename = "data.json"
    
    file_path = os.path.join(directory, filename)

    with open('data.json', 'w') as f:
        df = pd.DataFrame(prop_dict)
        json.dump(df.to_json(), f)
        
    
    try:
        os.mkdir("images")
    except:
        print("Directory already exists")
        
    os.chdir('images')
        
    for i, img_link in enumerate(prop_dict['Image link']):
        # download the image
        urllib.request.urlretrieve(img_link, str(i)+'.jpg')
        
    
    
        
    
        
        
