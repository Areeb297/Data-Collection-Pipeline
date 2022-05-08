# Data-Collection-Pipeline

> This project involves performing webscraping with Selenium to extract all the best seller and most wished for products on the Amazon UK webpage. This will easily allow the user to gather all the useful data relating to best selling products or the most desired items in a specified product category at any time. With the obtained data, one can analyze and keep up with the latest market trends. We only experiment with the Computer & Accessories category but just by changing the url in the scraper, we can get the data for any other desired category.

## Milestone 1

The Amazon scraper firstly visits the amazon webpage, locates and accepts the cookies button using its XPATH, and then based on the input of the user (best seller, most wished), visits the specific URL, scrolls down to the bottom of the page until all products of that particular page are shown, finds and appends the links of every product to a main list, clicks on the next button and repeats the same steps. Shown below is a code snippet of the steps the code goes through when getting the links on a page. Additionally, we show how the methods are used in order to acquire all the links.
  
```python

# Container_elements is a list of all the XPATHS of products in a given webpage
           
for property in container_elements:
        a_tag = property.find_element(by=By.TAG_NAME, value='a') # Locate the <a> tag to retrieve the href link of the product
        link = a_tag.get_attribute('href')
        link_list.append(link)

return link_list
        
# How to run the scraper class:
        
scraper = Amazon_UK_Scraper("Best Seller", "Computer & Accessories", "https://www.amazon.co.uk/") # The input could be "Most Wished For" or "Best Seller"
scraper.accept_cookies()
scraper.change_region() # Use this if you are not in the UK as the scraper only works delivery regions in the UK
links = scraper.get_all_links() # The get all links method uses the get get_links_per_page function and the get_all links function mainly justs appends the links to a 
# main list and clicks on the next button to obtain the same data on the next page.
prop_dict = scraper.prod_dict(links, 3) # Obtain a dictionary with all the product details 
# The rest of the code and explanation can be found in the main scraper file
```


## Milestone 2

Within this milestone, we retrieve all the product data and save it in dictionary format. The dictionary includes a unique product id obtained from the url of the webpage for example, B08F2NDB39 from "pd_rd_i=B08F2NDB39&th=1" section of the url, a version 4 universally unique id, title, price, product brand, promotion, ratings, most helpful review, and image and webpage link of the product. All the information is obtained through searching the XPATH of the appropriate element and obtaining it through Selenium. Additionally, we create two folders (raw_data, images) using the OS Python library where the dictionary and the images are saved. We use the os.mkdir command to create a new directory. Regarding downloading and saving images, we used the urllib library where we can download the image after obtaining the src link from the webpage using Selenium. The code for downloading the images using urllib is shown below:

```bash
    for i, img_link in enumerate(prop_dict['Image link']):
        # download the image
        urllib.request.urlretrieve(img_link, str(i)+'.jpg') # With each image link, we downloading its corresponding image and name it with the index of the image link e.g., the 2nd image link will be 2.jpg
```

A code snippet of the function that retrieves details from a product webpage along with the functions to output the uuid and unique ID are shown below. Moreover, we show how the dictionary is first converted to a dataframe and then dumped as a json file in the raw_data directory

```python

      product_id = value[value.find('pd_rd_i')+8: -6] # The .find method locates the first index of the required unique ID and the actual characters are found 8  characters after
    
    
    def v4_uuid(self):
        
        
        uuid_4 = uuid.uuid4()
            
        return str(uuid_4)  

        
    def retrieve_details_from_a_page(self):
       
        
        # There are some elements such as price or voucher which sometimes differ in location depending on the 
        # product and hence, we use multiple try and except statements to locate these if they exist. 

        # Title of the product
        try:
            title = self.driver.find_element(By.XPATH, '//span[@id="productTitle"]').text
        except NoSuchElementException:
            title = 'N/A'
        
        # Price of the product
        try:
            price = self.driver.find_element(by=By.XPATH, value='//span[@class="a-price aok-align-center"]').text.replace('\n', '.')
        except:
            price = 'N/A'  # Different products have prices shown on different locations (normally it could be three places, hence we use the try except statement)
            
        if price == 'N/A':
            
            try:
                price = self.driver.find_element(by=By.XPATH, value='//span[@class="a-price-whole"]').text
            except:
                price = 'N/A'
            
        if price == 'N/A':
            price = self.driver.find_element(By.XPATH, '//td[@class="a-span12"]').text
```

Below is a screenshot of the dataframe obtained after scraping 3 product webpages, particularly the best sellers in the Computer & Accessories section.
> ![image](https://user-images.githubusercontent.com/51030860/162643812-1ad33b30-42e6-4e81-97d5-327504758582.png)


## Milestone 3

- In this milestone, we added docstrings to our class methods using Google's recommended form of documentation and created a testing file which performs integration and unit testing such as checking we are using a specific chromedriver version or that there are no null values for price of a product which can be seen in the code snippet below:

```python

  # Doctring of our prod_dict class method:
  
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
  
  
  
  # Code snippets from our testing file

  self.scrap_1 = Amazon_UK_Scraper("most wished for", "computer & accessories", "https://www.amazon.co.uk/")
  
  expected_value = '101.0.4951.41' # Driver we worked with
  actual_value = self.scrap_1.__dict__['driver'].__dict__['caps']['browserVersion']
  # Assert statement to check expected and actual are the same values
  self.assertEqual(expected_value, actual_value)
  
  # Convert the dict into a dataframe and check the price column has no NaNs by converting to type float (if NaN value would be string N/A and
  #  hence will result in error)
  prop_dict = self.scrap_1.prod_dict(links, 5)
  df = pd.DataFrame(prop_dict)
  self.assertGreater(df['Price'].astype(float).sum(), 5) # Test 2

```


## Conclusions

- Maybe write a conclusion to the project, what you understood about it and also how you would improve it or take it further.

- Read through your documentation, do you understand everything you've written? Is everything clear and cohesive?
