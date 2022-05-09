import unittest
from AmazonWebScraper import Amazon_UK_Scraper
import pandas as pd
from PIL import Image
import os
from selenium.webdriver.common.by import By

class Scraper_Test(unittest.TestCase):
    def setUp(self):
        self.scrap_1 = Amazon_UK_Scraper("most wished for", "computer & accessories", "https://www.amazon.co.uk/")

    def test_version_inputs(self):

        """
        This test method checks which driver version we expect our Scraper to run with, verifies that cookies were accepted
        and additionally checks that the category of products are correctly passed
        i.e., Most Wished For products on the Amazon UK store

        """

        expected_value = '101.0.4951.41' # Driver we worked with where one can change this if needed 
        actual_value = self.scrap_1.__dict__['driver'].__dict__['caps']['browserVersion']
        # Assert statement to check expected and actual are the same values
        self.assertEqual(expected_value, actual_value)
        # Use the accept cookies method
        self.scrap_1.accept_cookies()
        # Tries to find the XPATH of the cookies button element and if not found, return False - we expect to obtain False if our accpet cookies method ran 
        # successfully
        try:
            self.scrap_1.find_element(by=By.XPATH, value='//span[@class="a-button a-button-primary"]') 
        except:
            val = False
        self.assertFalse(val)
        # Our last test for this method checks whether the options category is actually "Most Wished For" or not based on our setUp method
        # We can change this any other category of our choosing depending on how we initialize our Amazon_UK_Scraper class
        self.assertEqual('most wished for', self.scrap_1.__dict__['options'])

    def test_links_dict_images_format(self):
        """"
        This method tests 6 things - namely: 
         1) Whether the number of links we obtain are above a certain number (we use 20 as an example) to ensure our public method of get_all_links is working correctly. 
         2) Checks if the Price column of the product dataframe does not contain any null values as every product has a price listed
         3) Checks no duplicate rows are present in the dataframe as we have unique Product ID and UUIDs present so we essentially test these methods.
         4) Assert that the number of unique UUID values in our dataframe is equal to the number of rows in our dataframe - just to further check the UUID method
         5) Assert or check that a value in the UUID column has 36 characters as we used uuid4
         6) Test whether our Unique Product ID column has values only of 9 characters
         7) Ensures that the number of unique Unique Product ID values are the same as the number of rows of our dataframe - similar to UUID
         8) Lastly, we test whether the images we obtain are of JPEG format as we saved the images as '.jpg'
        If all these tests are satisfied, then we can be sure all of our methods of our scraper class are working correctly

        """

        self.scrap_1.accept_cookies()
        self.scrap_1.change_region()

        links = self.scrap_1.get_all_links()
        self.assertGreater(len(links), 20) # Test 1
        prop_dict = self.scrap_1.prod_dict(links, 5)
        # Convert the dict into a dataframe and check the price column has no NaNs by converting to type float (if NaN value would be string N/A and
        #  hence will result in error)
        df = pd.DataFrame(prop_dict)
        self.assertGreater(df['Price'].astype(float).sum(), 5) # Test 2
        # Check there are no duplicate rows in our dataframe obtained from converting the dictionary from the prod_dict method to a dataframe
        self.assertEqual(df.duplicated().sum(), 0) # Test 3

        self.assertEqual(df['UUID'].nunique(), df.shape[0]) # Test 4
        # Check whether the value of UUID has 36 characters
        self.assertEqual(len(df['UUID'][2]), 36) # Test 5

        self.assertEqual(len(df['Unique Product ID'][3]), 9) # Test 6

        self.assertEqual(df['Unique Product ID'].nunique(), df.shape[0]) # Test 7
        # Check the type of images generated
        # Try changing to the raw_data directory to see if it exits already - if not create a directory called raw_data and switch to it
        # Our dump_json_image_upload method creates an images directory to save all the images
        try:
            os.chdir('raw_data')
        except:
            print("Directory does not exist")
            os.mkdir("raw_data")
            os.chdir('raw_data')

        self.scrap_1.dump_json_image_upload(prop_dict)
        # Check whether the images in the directory are JPEG
        with Image.open('1.jpg') as image:
            self.assertEqual(type(image).format, 'JPEG') # Test 8

        # To change back to our original directory
        for _ in range(2):
            path_parent = os.path.dirname(os.getcwd())
            os.chdir(path_parent)



    def tearDown(self):
        # This method tears down or exists the scraper/driver
        self.scrap_1.driver.quit()


if __name__ == '__main__':
    unittest.main()
