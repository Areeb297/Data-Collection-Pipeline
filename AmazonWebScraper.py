# Import all packages

import time
import uuid
import json
import urllib
from tqdm import tqdm
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from pydantic import validate_arguments

import boto3
from sqlalchemy import create_engine





class AmazonUKScraper(): 

    """

    This class is used to scrape types of product from the Amazon UK store for 
    the best seller and most wished for product categories

    Attributes:

        options (str): The product category ("Best Seller" or "Most Wished For")
        items (str): The type of products e.g., "Computer & Accessories"

    """

    # Methods --> Accept Cookies, Scrolling down, Clicking on next page until run out of pages
    # Finding information about best sellers and most wished for products in a given section in the UK Amazon ecommerce site e.g., price etc

    @validate_arguments
    def __init__(self, options: str, items, url: str): 
        
        """
        See help(Amazon_UK_Scraper) for details
        """
      
        self.options = options.lower() # To keep text consistent
        self.items = items.lower() # To keep text consistent
        self.driver = webdriver.Chrome(ChromeDriverManager().install()) # Get the latest version of Chrome Driver Manager
        self.driver.get(url)


    def accept_cookies(self):

        """
        This method locates and accepts cookies if any.

        """

        try: # if cookies present
            self.driver.find_element(by=By.XPATH, value='//span[@class="a-button a-button-primary"]').click()
            time.sleep(1)

        except NoSuchElementException:
            pass
        
    def change_region(self):
    
        """
        This method ensures the region is set to the UK when accessing this scraper in a different country as this scraper only works within the UK region
        """

        # We need to check whether region is set to the UK as that is important 
        # This scraper only works for products delivered to regions in the UK
        # First lets check whether scraper is used in the UK and if so avoid using the steps in this method
        region = input("Are you in the UK: ")
        time.sleep(1)
        if str(region).lower() == "no":
            time.sleep(1)
            self.driver.find_element(by=By.XPATH, value='//div[@id="nav-global-location-slot"]').click() # Locate the region button and click

            time.sleep(2)
            s = self.driver.find_element(by=By.XPATH, value='//input[@class="GLUX_Full_Width a-declarative"]') # Find the input text element
            s.click()
            time.sleep(1)
            s.send_keys('CV47AL')  # send an example UK postcode
            time.sleep(1) 
            s.send_keys(Keys.ENTER) # Press Enter with the example code 
            time.sleep(1)
            self.driver.find_element(by=By.XPATH, value='//input[@type="submit"]').submit() # Submit the code 
        else:
            pass

    def scroll_bottom(self):

        """
        This function  scrolls to the bottom of the webpage; useful for loading out all elements on a given webpage.
        """

        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


    def find_container_elements(self):

        """
        This method locates all products and saves their XPATHS into a list. This function scrolls to the bottom of every webpage until all elements are loaded 
        and then locates XPATHS for every product inside a given container.

        Returns:
            list: A list of all the XPATHS concerning product data in the given container

        """


        try:
            time.sleep(1)
            next_button = self.driver.find_element(by=By.XPATH, value='//li[@class="a-last"]')
            next_button.location_once_scrolled_into_view   # Scrolls and waits until the next button appears in view to the scraper
            time.sleep(1)
            prop_container = self.driver.find_element(by=By.XPATH, value='//div[@class="p13n-gridRow _cDEzb_grid-row_3Cywl"]')
            prop_list = prop_container.find_elements(by=By.XPATH, value='./div[@id="gridItemRoot"]')

        except NoSuchElementException:
            time.sleep(1)
            previous_button = self.driver.find_element(by=By.XPATH, value='//li[@class="a-normal"]')
            time.sleep(1)
            # As the Next button is not visible/clickable anymore due it being the last page, we search for the previous button
            # Until that button is displayed, we keep scrolling to display all products on that given page
            previous_button.location_once_scrolled_into_view # Ensure all products are displayed
            time.sleep(1)
            prop_container = self.driver.find_element(by=By.XPATH, value='//div[@class="p13n-gridRow _cDEzb_grid-row_3Cywl"]')
            prop_list = prop_container.find_elements(by=By.XPATH, value='./div[@id="gridItemRoot"]')


        return prop_list

    @validate_arguments
    def get_links_per_page(self, container_elements: list):

        """
        With the XPATHS obtained from the "find elements" method, this method acquires all the links of the products on a given webpage.

        Args:
            container_elements (list): The list returned from the find_container_elements function

        Returns:
            list: A list of all the web links of every product on a given webpage

        """

        link_list = []

        for property_prod in container_elements:
            a_tag = property_prod.find_element(by=By.TAG_NAME, value='a') # Locate the <a> tag to retrieve the href link of the product
            link = a_tag.get_attribute('href')
            link_list.append(link)

        return link_list


    def get_all_links(self):

        """

        This function of the class uses the inputs from the class constructor and the set driver method to navigate to the correct URL. 
        Afterward, it uses the find_container_elements and get_links_per_page functions on a single webpage, clicks on the next button and 
        uses the previou methods again to append all the links of products listed.

        Returns:
            list: A list of all the links of products available for the given product category

        """

        if self.options == "best seller":
            if self.items == "computer & accessories":

                self.driver.get('https://www.amazon.co.uk/Best-Sellers-Computers-Accessories/zgbs/computers/ref=zg_bs_nav_0')


        elif self.options == "most wished for":   
            if self.items == "computer & accessories":

                self.driver.get('https://www.amazon.co.uk/gp/most-wished-for/computers/ref=zg_mw_nav_0')

        big_list = []

        for _ in range(2): # 2 pages of products for every category in the best sellers or most wished section

            prop_links = self.find_container_elements()
            l = self.get_links_per_page(prop_links)
            big_list.extend(l)
            try:
                time.sleep(2)
                button = self.driver.find_element(by=By.XPATH, value='//li[@class="a-last"]')
                element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable(button))
                element.click()
                time.sleep(1)

            except NoSuchElementException:
                break


        return big_list


    @staticmethod
    def unique_id_gen(url):

        """
        This function takes in the URL of a product webpage and returns the unique product id. For example, the format 'pd_rd_i=XXXXXXXXX&psc=N'
        is given in every URL and thus, we extract the string XXXXXXXXX.

        Args:
            url (str): The url of a given product

        Returns:
            str: The string representation of the product ID given in the url argument.
        """

        product_id = url[url.find('pd_rd_i')+8: -6]     # The .find method locates the first index of the required 
                                                        # unique ID and the actual characters are found 8 characters after

        return str(product_id)



    @staticmethod
    def v4_uuid():

        """
        This function generates a unique uuid for every link using the uuid package

        Returns:

            str: The uuid value in string format

        """


        uuid_4 = uuid.uuid4()
        return str(uuid_4)  


    def retrieve_details_from_a_page(self):

        """
        This function inspects various properties of a product e.g., title, price, brand, reviews, description, image src link etc., using multiple try-except statements

        Returns:

            tuple: The tuple contains string format of product attributes

        """

        # There are some elements such as price or voucher which sometimes differ in location depending on the 
        # product and hence, we use multiple try and except statements to locate these if they exist. 

        # Title of the product
        try:
            title = self.driver.find_element(By.XPATH, '//span[@id="productTitle"]').text
        except NoSuchElementException:
            title = 'N/A'

        # Price of the product
        try:
            price = self.driver.find_element(By.XPATH, '//span[@class="a-size-base a-color-price"]').text
        except NoSuchElementException:
            price = 'N/A'  # Different products have prices shown on different locations (normally it could be three places, hence we use the try except statement)

        if price == 'N/A':
            try:
                price = self.driver.find_element(By.XPATH, '//span[@class="a-price aok-align-center reinventPricePriceToPayMargin priceToPay"]').text.replace('\n', '.')
            except NoSuchElementException:
                price = 'N/A'

        if price == 'N/A':
            try:
                price = self.driver.find_element(By.XPATH, '//td[@class="a-span12"]').text
            except NoSuchElementException:
                price = 'N/A'

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
        # These reductions are found at different places depending on the link and hence we used several try and excepts here
        try:
            price_override = self.driver.find_element(By.XPATH, '//span[@class="a-size-large a-color-price savingPriceOverride aok-align-center reinventPriceSavingsPercentageMargin savingsPercentage"]').text

        except NoSuchElementException:
            price_override = 'N/A'

        if price_override == 'N/A':
            try:
                price_override = self.driver.find_element(By.XPATH, '//td[@class="a-span12 a-color-price a-size-base\
                                                  priceBlockSavingsString"]').text
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


        return title, price, brand, voucher, price_override, review_ratings, global_ratings, topics_review, review_helpful, src



    def prod_dict(self, links, n):

        """
        This function initializes a dictionary and by using the previously defined methods, retrieves different product information from every webpage,
        and appends the information to relevant list corresponding to the appropriate dictionary key.

        Args:
            links (list): List of links relating to all products 
            n (int): How many products to scrape and gather information of

        Returns:
            dict: All product information in the form of a dictionary 

        """

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

        # We use tqdm to have a progress bar to ensure the scraper is working
        for link in tqdm(links[0:n]):

            self.driver.get(link)
            time.sleep(1)
            self.scroll_bottom()
            time.sleep(2)
            prop_dict['Page Link'].append(link)
            prop_dict['UUID'].append(self.v4_uuid())
            prop_dict['Unique Product ID'].append(self.unique_id_gen(link))


            title, price, brand, voucher, price_override, review_ratings, global_ratings, \
            topics_review, review_helpful, src = self.retrieve_details_from_a_page()

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

        return prop_dict

    @validate_arguments 
    def dump_json_image_upload(self, prod_diction: dict):

        """
        This function creates a new json file, stores the product dictionary obtained from the prod_dict function in json format. 
        Furthermore, it creates another directory  within the raw_data directory or folder to store all the image data. 
        Lastly, using the urlib package, it retrieves the product image link from the product dictionary and stores each image as jpg. 

        Args:
            prod_diction (dict): Information about every product

        Returns:
            df_prod: All product information in a pandas dataframe to upload on the AWS RDS
        """
        # dump the generated dictionary into a json file

        with open('data.json', 'w') as f:
            df_prod = pd.DataFrame(prod_diction)  # First convert our dictionary of product information to a dataframe 
                                                  # and then to json
            json.dump(df_prod.to_json(), f)


        try:
            os.mkdir("images")
        except:
            print("Directory already exists")

        os.chdir('images')
        for i, img_link in enumerate(prod_diction['Image link']):
            # download the image
            try:
                urllib.request.urlretrieve(img_link, f"{i}.jpg")
            except:
                print("Image already exists")

        return df_prod

    @staticmethod
    def create_raw_data_dir():

        """
        This method creates a directory called "raw_data" and changes the current directory

        """
        # Try except statement as directory will be created once the code is run and cannot be created twice
        try:
            os.mkdir("raw_data")
        except:
            print("Directory already exists")

        os.chdir('raw_data')

    @staticmethod
    def upload_to_cloud():

        """
        This class method uses boto3 to create a S3 bucket on AWS and upload the raw_data folder which includes all the image files 
        and the product information json file. 

        """


        s3 = boto3.client('s3')
        s3.create_bucket(Bucket='aicorebucketareeb')

        s3.upload_file('raw_data/data.json', 'aicorebucketareeb', 'raw_data/data.json')


        for i in os.listdir('raw_data/images'): # We list out all the image files and loop to upload the files to S3 one by one
            s3.upload_file('raw_data/images/'+i, 'aicorebucketareeb', 'raw_data/images/'+i)

    def upload_dataframe_rds(self, df):

        """
        This function requests the user to input credentials required to set up connection between AWS RDS database and PostgresSQL/PgAdmin
        where it then takes the dataframe which was entered as an argument, converts it to SQL format and the saves it in the RDS.

        Args:
            df (DataFrame): Pandas Dataframe containing all product information which was scraped

        """

        PASSWORD = input("Please input password: ")
        ENDPOINT = input("Please enter your AWS endpoint for RDS: ")  # Your AWS endpoint

        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        USER = 'postgres'
        PORT = 5432
        DATABASE = 'postgres'
        engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
        engine.connect()
        if self.options == 'most wished for':
            try:
                df.to_sql('most_wished_for', engine, if_exists='replace')
            except:
                print('Dataframe already exists')
        else:
            try:
                df.to_sql('best_seller', engine, if_exists='replace')
            except:
                print('Dataframe already exists')




if __name__ == '__main__':


    scraper = AmazonUKScraper("most wished for", "computer & accessories", "https://www.amazon.co.uk/")
    scraper.accept_cookies()
    scraper.change_region()

    prod_links = scraper.get_all_links()

    product_dictionary = scraper.prod_dict(prod_links, 6) # Get information about 5 products
    scraper.create_raw_data_dir()
    dataframe = scraper.dump_json_image_upload(product_dictionary)

    # Go back two directories prior to be able to use other methods in the future

    for _ in range(2):
        parent_directory = os.path.dirname(os.getcwd())
        os.chdir(parent_directory)

    scraper.upload_to_cloud()
    scraper.upload_dataframe_rds(dataframe)

    scraper.driver.quit()











