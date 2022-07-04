import time
import json
import urllib
import os
from tqdm import tqdm

import pandas as pd
from pydantic import validate_arguments
from typing import Union

import boto3
from sqlalchemy import create_engine 

from scraper_module_1 import AmazonUKScraper

from dotenv import load_dotenv
load_dotenv()



class Run_Scraper():
    
    """This class initializes the amazon webscraper, saves the product data 
    locally and updates the data stored in AWS S3 and RDS.
    
    Attributes:

        options (str): Category of products  i.e., Best Seller/Most Wished For
        items (str): Which type of product e.g., "Computer & Accessories"
        headless (bool): Headless mode being on or off whilst running scraper

    """
    
    @validate_arguments
    def __init__(self, options: str, items: str, headless: bool): 
        
        """
        See help(AmazonUKScraper) for details
        """
        self.options = options
        self.items = items
        self.headless = headless

        self.scraper = AmazonUKScraper(options, items, "https://www.amazon.co.uk/", headless)
        self.driver = self.scraper.driver
        time.sleep(1)

    

    
    @validate_arguments
    def collectdata(self, n: Union[int, str]):
    
        """This function retrieves different product information from every
        webpage, and appends the information to relevant list corresponding 
        to the appropriate dictionary key.
    
        Args:
            links (list): List of links relating to all products 
            n (int): How many products to scrape and gather information 
    
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
        
        links = self.scraper._get_all_links()
        if n == 'all':
            n = len(links)
        # We use tqdm to have a progress bar to ensure the scraper is working
        engine = self._engine_func()
        global conn
        conn = engine.connect()
        if self.options == 'most wished for':
            try:
                query_wish = '''SELECT "Unique Product ID" FROM most_wished_for'''
                prod_id_most_wished_for = pd.DataFrame(conn.execute(query_wish))
            except:
                print("No data present in pgadmin")
                prod_id_most_wished_for = pd.DataFrame(prop_dict)

        else:
            try:
                query_best = '''SELECT "Unique Product ID" FROM best_seller'''
                prod_id_best_seller = pd.DataFrame(conn.execute(query_best))
            except:
                print("No data present in pgadmin")
                prod_id_best_seller = pd.DataFrame(prop_dict)
        try:  
            empty_existing_data = os.getenv('start_empty')
        except:
            empty_existing_data = input('Do you want to start from an empty dictionary: ').lower()
            
        for link in tqdm(links[0:n]):  
            # We check whether record exists in the SQL database connected
            # with AWS RDS
            # This prevents rescraping if the product id is already 
            # scraped and added to the dict
            if self.options == 'most wished for' and empty_existing_data == 'no':
                try:
                    s = prod_id_most_wished_for['Unique Product ID'].str.contains(self.scraper._unique_id_gen(link)).sum() 
                except:
                    s = 0
                # There should only be one unique link
                if s == 1:
                    print('Already scraped this product')
                    continue
                elif s == 0:
                    print('This record does not exist in the SQL data in AWS RDS & PgAdmin')
                    pass
            elif self.options == 'best seller' and empty_existing_data == 'no':
                try:
                    s = prod_id_best_seller['Unique Product ID'].str.contains(self.scraper._unique_id_gen(link)).sum()
                except:
                    s = 0
                if s == 1: # There should only be one unique link
                    print('Already scraped this product')
                    continue

                elif s == 0:
                    print('This record does not exist in the SQL data in AWS RDS & PgAdmin')
                    pass
            else:
                pass
    
            
    
            self.driver.get(link)
            time.sleep(1)
            self.scraper._scroll_bottom()
            time.sleep(2)
            
    
            prop_dict['Unique Product ID'].append(self.scraper._unique_id_gen(link))
            
            prop_dict['Page Link'].append(link)
            prop_dict['UUID'].append(self.scraper._v4_uuid())
    
    
            title, price, brand, voucher, price_override, review_ratings, \
            global_ratings, topics_review, review_helpful, \
            src = self.scraper.retrieve_details_from_a_page()
    
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

    
    def _engine_func(self):
        
        """This class method allows us to set up connection between us and 
        the AWS RDS database and PostgresSQL/PgAdmin using psycopg2
        """
        # Pgadmin password
        PASSWORD = os.getenv('password')
        # Your AWS endpoint
        ENDPOINT = os.getenv('endpoint')
    
        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        USER = os.getenv('user')
        PORT = 5432
        DATABASE = 'postgres'
        engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
        return engine
    
    
    @validate_arguments 
    def dump_json_image_upload(self, prod_diction:dict):
    
        """This function creates a new json file, stores the product dictionary
        obtained from the prod_dict function in json format. Furthermore, it 
        creates another directory  within the raw_data directory or folder to 
        store all the image data. Lastly, using the urlib package, it retrieves
        the product image link from the product dictionary and stores 
        each image as jpg. 
    
        Args:
            prod_diction (dict): Information about every product
    
        Returns:
            df_prod: All product information in a pandas dataframe to upload 
            on the AWS RDS
        """
        # dump the generated dictionary into a json file

        with open('data.json', 'w') as f:
            df_prod = pd.DataFrame(prod_diction) 
            # First convert our dictionary of product information
            # to a dataframe and then to json
            json.dump(df_prod.to_json(), f)
    
        # we will add images to the folder which are new or not been scraped
    
        try:
            os.mkdir("images_"+self.options)
        except:
            print("Directory already exists")
    
        os.chdir('images_'+self.options)
        list_files = os.listdir(os.getcwd()) # dir is your directory path
        number_files = len(list_files) 
        for img_link in prod_diction['Image link']:
            # download the image
            urllib.request.urlretrieve(img_link, "{}.jpg".format(number_files))
            number_files += 1

        try:
            update = os.getenv('update_cloud').lower()
        except:
            update = input('Update data in cloud? ').lower()
        
        if update == 'yes':
            self._upload_dataframe_rds(df_prod)
            self._upload_to_cloud()


    
    
    def _upload_to_cloud(self):
    
        """
        This class method uses boto3 to create a S3 bucket on AWS and upload 
        the raw_data folder which includes all the image files 
        and the product information json file. 
    
        """

        key_id = os.getenv('key_id')
        secret_key = os.getenv('secret_key')
        bucket_name = os.getenv('bucket_name')
        region = os.getenv('region')

        s3 = boto3.client("s3", 
                        region_name=region, 
                        aws_access_key_id=key_id, 
                        aws_secret_access_key=secret_key)

        self._move_to_parent_dir(1) # Go back directory to access data.json

        s3.upload_file('data.json', bucket_name, 
                        'raw_data/data.json')


        for i in os.listdir('images_'+self.options): 
            # We list out all the image files and loop to upload the files 
            # to S3 one by one
            s3.upload_file('images_'+self.options+'/'+i, 
                    bucket_name, 'raw_data/images_'+self.options+'/'+i)
    
    
    def _upload_dataframe_rds(self, df):
    
        """This function takes the dataframe which was entered as an argument, 
        converts it to SQL format and then saves it in the RDS.
    
        Args:
            df (DataFrame): Pandas dataframe containing all product information
            which was scraped
    
        """
        if self.options == 'most wished for':
            df.to_sql("most_wished_for", conn, if_exists='append', 
                        chunksize=60) 
        # We have defined engine globally previously
        else:
            df.to_sql("best_seller", conn, if_exists='append', 
                        chunksize=60)
    
    def _move_to_parent_dir(self, n):
    
        """This class method allows us to move above to the parent directory a 
        specified number of times using the os library
    
        Args:
            n (int): The number of times we want to move above to the 
            parent directory
    
        """
        for _ in range(n):
            parent_directory = os.path.dirname(os.getcwd())
            os.chdir(parent_directory)



if __name__ == '__main__':

    choices = os.getenv('options')
    scraper = Run_Scraper(choices, "computer & accessories", headless=True)
    prod_diction = scraper.collectdata(os.getenv('n'))
    scraper.dump_json_image_upload(prod_diction)
    scraper.driver.quit()
