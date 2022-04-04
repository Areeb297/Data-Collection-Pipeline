# Data-Collection-Pipeline

> This project involves performing webscraping with Selenium to extract all the best seller and most wished for products on the Amazon UK webpage. This will easily allow the user to gather all the useful data relating to best selling products or the most desired items in a specified product category at any time. With the obtained data, one can analyze and keep up with the latest market trends. We only experiment with the Computer & Accessories category but just by changing the url in the scraper, we can get the data for any other desired category.

## Milestone 1

The Amazon scraper firstly visits the amazon webpage, locates and accepts the cookies button using its XPATH, and then based on the input of the user (best seller, most wished), visits the specific URL, scrolls down to the bottom of the page until all products of that particular page are shown, finds and appends the links of every product to a main list, clicks on the next button and repeats the same steps. Shown below is a code snippet of the steps the code goes through when getting the links on a page. Additionally, we show how the methods are used in order to acquire all the links.
  
```python

    def get_links_on_a_page(self):
        
        link_list = []
        try:
            next_button = self.driver.find_element(by=By.XPATH, value='//li[@class="a-last"]')
            next_button.location_once_scrolled_into_view
            time.sleep(1)
            prop_container = self.driver.find_element(by=By.XPATH, value='//div[@class="p13n-gridRow _p13n-zg-list-grid-desktop_style_grid-row__3Cywl"]')
            prop_list = prop_container.find_elements(by=By.XPATH, value='./div')
            
        except:
            print("Last page of products")
            previous_button = self.driver.find_element(by=By.XPATH, value='//li[@class="a-normal"]')
            time.sleep(1)
            
            # As the Next button is not visible anymore due it being the last page, we search for the previous button
            # Until that button is displayed, we keep scrolling to display all products on that given page
            
            previous_button.location_once_scrolled_into_view
            time.sleep(1)
            prop_container = self.driver.find_element(by=By.XPATH, value='//div[@class="p13n-gridRow _p13n-zg-list-grid-desktop_style_grid-row__3Cywl"]')
            prop_list = prop_container.find_elements(by=By.XPATH, value='./div')
           
        for property in prop_list:
                a_tag = property.find_element(by=By.TAG_NAME, value='a')
                link = a_tag.get_attribute('href')
                link_list.append(link)
                
        return link_list
        
# How to run the scraper class:
        
scraper = Amazon_UK_Scraper("Most Wished For", "Computer & Accessories") # The input could be "Most Wished For" or "Best Seller"
scraper.set_driver_url()
scraper.accept_cookies()
links = scraper.get_all_links() # The get all links method uses the get links_on_a_page function and the get all links function mainly justs appends the links to a 
# main list and clicks on the next button to obtain the same data on the next page.
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
"""    def unique_id_gen(self, value):
        

        product_id = value[value.find('pd_rd_i')+8: -6] # The .find method locates the first index of the required unique ID and the actual characters are found 8 characters after
            
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
            price = 'N/A'
            
        if price == 'N/A': # Different products have prices shown on different locations (normally it could be three places, hence we use the try except statement)
            try:
                price = self.driver.find_element(By.XPATH, '//span[@class="a-price aok-align-center reinventPricePriceToPayPadding priceToPay"]').text.replace('\n', '.')
            except:
                price = self.driver.find_element(By.XPATH, '//td[@class="a-span12"]').text"""
```

Below is a screenshot of the dataframe obtained after scraping 3 product webpages, particularly the best sellers in the Computer & Accessories section.
> ![image](https://user-images.githubusercontent.com/51030860/161623165-5fdff401-3a8a-43f9-a348-4c160df630de.png)

## Milestone n

- Continue this process for every milestone, making sure to display clear understanding of each task and the concepts behind them as well as understanding of the technologies used.

- Also don't forget to include code snippets and screenshots of the system you are building, it gives proof as well as it being an easy way to evidence your experience!

## Conclusions

- Maybe write a conclusion to the project, what you understood about it and also how you would improve it or take it further.

- Read through your documentation, do you understand everything you've written? Is everything clear and cohesive?
