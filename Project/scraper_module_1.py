# Import all necessary packages

import time
import uuid
import os
from pydantic import validate_arguments
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


from dotenv import load_dotenv
load_dotenv()




class AmazonUKScraper(): 

    """This class contains all data collection methods for scraping Amazon
    scrape product data from the Amazon UK website concerning best seller and 
    most wished for products in the Computer & Accessories category. The idea
    is to build a database with best seller and most wished for products over
    time in every category starting from Computers & Accessories

    Attributes:

        options (str): Category of products  i.e., Best Seller/Most Wished For
        items (str): Which type of product e.g., "Computer & Accessories"
        headless (bool): Headless mode being on or off whilst running scraper
        url (str): The url of the desired website
        metadata_dict (dict, None): dictionary will contain metadata 
        individual products from Amazon

    """

    @validate_arguments
    def __init__(self, options: str, items: (str), url: (str), headless: bool): 
        
        """
        See help(AmazonUKScraper) for details
        """

        s = Service(ChromeDriverManager().install())
        
        self.url = url
        self.options = options.lower() # To keep input text consistent
        self.items = items.lower() # To keep input text consistent
    
                    

        if headless:
    
            chrome_options = ChromeOptions()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_prefs = {}
            chrome_options.experimental_options["prefs"] = chrome_prefs
            chrome_prefs["profile.default_content_settings"] = {"images": 2}

            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument('--allow-running-insecure-content') 
            user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
            chrome_options.add_argument(f'user-agent={user_agent}')
            # chrome_options.add_argument("--no-sandbox") 
            # chrome_options.add_argument("--headless")
            # chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("window-size=1980,1000")
            self.driver = webdriver.Chrome(service=s, chrome_options=chrome_options)
        else:
            self.driver = webdriver.Chrome(service=s)

        self.driver.get(url)
        # open and bypass cookies 
        self._accept_cookies()
        # change region if necessary 
        self._change_region()
        # creates a raw_data directory to save all the data
        self._create_raw_data_dir('raw_data')
        


    def _accept_cookies(self):

        """This method locates and accepts cookies if any"""

        try: # if cookies present
            time.sleep(1)
            cookies_xpath = '//span[@class="a-button a-button-primary"]'
            self.driver.find_element(by=By.XPATH, value=cookies_xpath).click()

        except NoSuchElementException:
            pass
        
    def _change_region(self):
    
        """This method ensures the region is set to the UK when working with  
        our scraper as certain products are not available in other regions
        """

        # This scraper only works for products delivered to regions in the UK
        # First lets check whether scraper is used in the UK and if so avoid 
        # using the steps in this method
        # Some regions maybe not have best sellers or most wished for options
        
        region = os.getenv('region_change')
        time.sleep(1)
        if str(region).lower() == "yes":
            time.sleep(1)
            region_xpath = '//div[@id="nav-global-location-slot"]'
            # Locate the region button and click
            self.driver.find_element(by=By.XPATH, value=region_xpath).click()
            
            time.sleep(2)
            # Find the input text element
            text_xpath = '//input[@class="GLUX_Full_Width a-declarative"]'
            s = self.driver.find_element(by=By.XPATH, value=text_xpath) 
            s.click()
            
            time.sleep(1)
            s.send_keys('CV47AL')  # send an example UK postcode
            time.sleep(1) 
            s.send_keys(Keys.ENTER) # Press Enter with the example code 
            time.sleep(1)
            # Submit the code 
            submit_xpath = '//input[@type="submit"]'
            self.driver.find_element(by=By.XPATH, value=submit_xpath).submit() 
        else:
            pass

    def _scroll_bottom(self):

        """This function scrolls to the bottom of the webpage; useful for 
        loading all elements.
        """
        scroll_bottom = "window.scrollTo(0, document.body.scrollHeight);"
        self.driver.execute_script(scroll_bottom)


    def _find_container_elements(self):

        """This method locates all products and saves their XPATHS into a list. 

        Returns:
            list: A list of all the XPATHS concerning relevant product data in
            a html container

        """
        time.sleep(1)
        page_button = self.driver.find_element(by=By.XPATH, value='//li[@class="a-normal"]')
        page_button.location_once_scrolled_into_view   # Scrolls and waits until the bottom page button appears in view to the scraper
        time.sleep(1)
        prop_container = self.driver.find_element(by=By.XPATH, value='//div[@class="p13n-gridRow _cDEzb_grid-row_3Cywl"]')
        prop_list = prop_container.find_elements(by=By.XPATH, value='./div[@id="gridItemRoot"]')

        return prop_list

    @validate_arguments
    def _get_links_per_page(self, container_elements: list):

        """With the XPATHS obtained from the "find elements" method, this 
        method acquires all the links of the products on a given webpage.

        Args:
            container_elements (list): The list returned from the 
            find_container_elements function

        Returns:
            list: A list of the web links of every product in a given webpage

        """

        link_list = []

        for property_prod in container_elements:
            # Locate the <a> tag to retrieve the href link of the product
            a_tag = property_prod.find_element(by=By.TAG_NAME, value='a')
            link = a_tag.get_attribute('href')
            link_list.append(link)

        return link_list


    def _get_all_links(self):

        """This function sets the correct url and scrapes links of products
        

        Returns:
            list: A list of links of products for a given product category

        """

        if self.options == "best seller":
            if self.items == "computer & accessories":

                self.driver.get('https://www.amazon.co.uk/Best-Sellers-Computers-Accessories/zgbs/computers/ref=zg_bs_nav_0')


        elif self.options == "most wished for":   
            if self.items == "computer & accessories":

                self.driver.get('https://www.amazon.co.uk/gp/most-wished-for/computers/ref=zg_mw_nav_0')

        big_list = []
        
        # Two pages of products for every category in 
        # the best sellers or most wished section
        for _ in range(2):

            prop_links = self._find_container_elements()
            l = self._get_links_per_page(prop_links)
            big_list.extend(l)
            try:
                time.sleep(2)
                button = self.driver.find_element(by=By.XPATH, value='//li[@class="a-last"]')
                                                  
                element = WebDriverWait(self.driver, 2).until\
                (EC.element_to_be_clickable(button))
                
                element.click()
                time.sleep(1)

            except NoSuchElementException:
                break


        return big_list


    @staticmethod
    def _unique_id_gen(url):

        """This function takes in the URL of a product webpage and returns the 
        unique product id. For example, the format 'pd_rd_i=XXXXXXXXX&psc=N'
        is given in every URL and thus, we extract the string XXXXXXXXX.

        Args:
            url (str): The url of a given product

        Returns:
            str: The string representation of the product ID given in the 
            url argument.
        """

        # The .find method locates the first index of the required 
        # unique ID and the actual characters are found after 8 characters 
        product_id = url[url.find('pd_rd_i')+8: -6]

        return str(product_id)



    @staticmethod
    def _v4_uuid():

        """This function generates a unique uuid for every link using the uuid 
        package

        Returns:

            str: The uuid value in string format

        """


        uuid_4 = uuid.uuid4()
        return str(uuid_4)  


    def retrieve_details_from_a_page(self):

        """This function inspects various properties of a product 
        e.g., title, price, brand, reviews, image src link and more
        using multiple try-except statements

        Returns:

            tuple: The tuple contains string format of product attributes

        """

        # There are some elements such as price or voucher which sometimes 
        # differ in location depending on the 
        # product and hence, we use multiple try and except statements 
        # to locate these if they exist. 

        # Title of the product
        try:
            title = self.driver.find_element(By.XPATH, '//span[@id="productTitle"]').text
        except NoSuchElementException:
            title = 'N/A'

        # Price of the product
        try:
            price = self.driver.find_element(By.XPATH, '//span[@class="a-price a-text-price header-price a-size-base a-text-normal"]').text
        except NoSuchElementException:
            try:
                price = self.driver.find_element(By.XPATH, '//span[@class="a-size-medium a-color-price priceBlockBuyingPriceString"]').text.replace('\n', '.')
            except:
                price = 'N/A'  # Different products have prices shown on different locations (normally it could be three places, hence we use the try except statement)


        if price == 'N/A':

            try:
                price = self.driver.find_element(By.XPATH, '//span[@class="a-price aok-align-center reinventPricePriceToPayMargin priceToPay"]').text.replace('\n', '.')
            except NoSuchElementException:

                try:
                    price = self.driver.find_element(By.XPATH, '//td[@class="a-span12"]').text
                except:
                    try:
                        price = self.driver.find_element(By.XPATH, '//span[@data-maple-math="cost"]').text
                    except NoSuchElementException:
                        price = 'N/A'

        # Similar to price, we find the same problems with Brand, Voucher, Promotion and hence we perform multiple try except statements

        # Brand
        try:
            brand = self.driver.find_element(By.XPATH, '//tr[@class="a-spacing-small po-brand"]').text.split(' ')[1]
        except:
            brand = 'N/A'
        # Voucher available
        try:
            voucher = self.driver.find_element(by=By.XPATH, value='//span[@class="promoPriceBlockMessage"]').text.split('\n')[1]
        except:
            try:
                voucher = self.driver.find_element(By.XPATH, '//div[@data-csa-c-slot-id="promo-cxcw-0-0"]').text
            except NoSuchElementException:
                voucher = 'N/A'

        # Percentage reduction in price
        # These reductions are found at different places depending on the link and hence we used several try and excepts here
        try:
            price_override = self.driver.find_element(By.XPATH, '//span[@class="a-size-large a-color-price savingPriceOverride aok-align-center reinventPriceSavingsPercentageMargin savingsPercentage"]').text

        except NoSuchElementException:
            price_override = 'N/A'

        if price_override == 'N/A':
            try:
                price_override = self.driver.find_element(By.XPATH, '//td[@class="a-span12 a-color-price a-size-basepriceBlockSavingsString"]').text
            except NoSuchElementException:
                price_override = 'N/A'


        if price_override == 'N/A':
            try:
                price_override = self.driver.find_element(By.XPATH, '//td[@class="a-span12 a-color-price a-size-base"]').text
            except NoSuchElementException:
                price_override = 'N/A'

        # Below, we know for certain that these elements exist, hence we will not use try-except here

        
        try:
            # Review ratings
            review_ratings = self.driver.find_element(By.XPATH, '//span[@class="a-size-medium a-color-base"]').text
        except:
            review_ratings = 'No rating'
        
        try:  # Number of ratings
            global_ratings = self.driver.find_element(By.XPATH, '//div[@data-hook="total-review-count"]').text
        except:
            global_ratings = 'No global rating'

        try:
            # Review topics
            topics_review = self.driver.find_element(by=By.XPATH, value='//div[@class="cr-lighthouse-terms"]').text
        except:
            topics_review = 'No review topics'

        try:
            # Most helpful review
            first_review = self.driver.find_element(by=By.XPATH, value='//div[@id="cm-cr-dp-review-list"]').find_elements(by=By.XPATH, value='./div[@data-hook="review"]')[0]
            review_helpful = first_review.find_element(by=By.XPATH, value='//span[@data-hook="review-body"]').text

        except:
            review_helpful = 'No most helpful review'


        # Main Image Link
        src = self.driver.find_element(By.XPATH, '//div[@class="imgTagWrapper"]').find_element(By.TAG_NAME, 'img').get_attribute('src')


        return title, price, brand, voucher, price_override, review_ratings, \
               global_ratings, topics_review, review_helpful, src


    @staticmethod
    @validate_arguments
    def _create_raw_data_dir(name: str):
    
        """This method creates a directory and changes into that directory
        
        Args:
            name (str): The name of the directory (raw_data)
    
        """
        current_dir = os.getcwd()
        desired_dir = os.path.join(current_dir, name)
        if os.path.exists(desired_dir):
            os.chdir(desired_dir)
            
        else:
            os.mkdir(name)
            os.chdir(desired_dir)
            
            

