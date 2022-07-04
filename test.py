import unittest
import pandas as pd
import time
from PIL import Image
from selenium.webdriver.common.by import By
from Project.main import Run_Scraper

class ScraperTest(unittest.TestCase):
    """
    This test class ensures all public methods of the AmazonUKScraper Class work as expected
    """
    @classmethod
    def setUpClass(cls):

        """Set up method initialises an instance of Run_Scraper class 
        and navigates to desired product category page after accepting cookies
        and changing to the correct region for delivert if necessary (not in the UK)
        """
        cls.options = input("Please input your desired product category from [most wished for, best seller]: ")
        cls.headless = input("True or False for Headless: ")
        cls.scrap_1 = Run_Scraper(cls.options, "computer & accessories", cls.headless)
        time.sleep(2)

    def test_scraped_products(self):    
        """
        This test would run successfully if correct number of produts in the correct UK region 
        are scraped with no duplicates and null values
        and finally, the images are in correct format.
        """
        
        # initialize required arguments 
        num_links = 4
        # check region is Coventry after applying the change region method
        self.scrap_1.driver.find_element(by=By.XPATH, value='//span[@class="nav-line-2 nav-progressive-content"]').text[:8] == 'Coventry'
        prod_diction = self.scrap_1.collectdata(num_links)
        # check for duplicates
        dataframe = pd.DataFrame(prod_diction)
        self.assertEqual(dataframe.duplicated().sum(), 0)
        # check correct number of products scraped
        self.assertEqual(len(prod_diction['Price']), num_links)
        # check no null values
        self.assertEqual(dataframe.isna().sum().sum(), 0)
        # check image exists and verify format
        self.scrap_1.dump_json_image_upload(prod_diction)
        with Image.open('0.jpg') as image:
            self.assertEqual(type(image).format, 'JPEG') 

    @classmethod
    def tearDownClass(cls) -> (None):
        return cls.scrap_1.driver.quit()



if __name__ == '__main__':
    unittest.main()

    
