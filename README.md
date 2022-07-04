# Data-Collection-Pipeline

This amazon scraper pipeline is designed to collect both structured and unstructured data https://www.amazon.co.uk/ where the webscraper regularly gives you an updated dataframe of the best sellers or most wished for categories in the Computer & Accessories product section. With further work to this project, we can add further product sections to be scraped in the future.

## Project Outline

This project involves performing webscraping with Selenium to extract all the best seller and most wished for products on the Amazon UK webpage. This will easily allow the user to gather all the useful data relating to best selling products or the most desired items in a specified product category at any time. With the obtained data, one can analyze and keep up to date with the latest market trends. We only experiment with the Computer & Accessories and the Most Wished for product category but just by changing the url in the scraper, we can get the data for any other desired category. This scraper has also been published as a PyPi package here: https://pypi.org/project/areeb-amazon-scraper/0.0.1/

## Scraper functionality 

The Amazon scraper firstly visits the amazon webpage, locates and accepts the cookies button using its XPATH, and then based on the input of the user (best seller, most wished), visits the specific URL, scrolls down to the bottom of the page until all products of that particular page are shown, finds and appends the links of every product to a main list, clicks on the next button and repeats the same steps. Shown below is a code snippet of the steps the code goes through when getting the links on a page. Additionally, we show how the methods are used in order to acquire all the links.
  
```python

# Container_elements is a list of all the XPATHS of products in a given webpage
           
for property in container_elements:
        a_tag = property.find_element(by=By.TAG_NAME, value='a') # Locate the <a> tag to retrieve the href link of the product
        link = a_tag.get_attribute('href')
        link_list.append(link)

return link_list
       
```


## Scraping products and images with resulting dataframe shown

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

        if price == 'N/A':

            try:
                price = self.driver.find_element(By.XPATH, '//span[@class="a-price aok-align-center reinventPricePriceToPayMargin     priceToPay"]').text.replace('\n', '.')
            except NoSuchElementException:

                try:
                    price = self.driver.find_element(By.XPATH, '//td[@class="a-span12"]').text  # Different products have prices shown on different locations
                except:
                    try:
                        price = self.driver.find_element(By.XPATH, '//span[@data-maple-math="cost"]').text
                    except NoSuchElementException:
                        price = 'N/A'

```

Below is a screenshot of the dataframe obtained after scraping 3 product webpages, particularly the best sellers in the Computer & Accessories section.
> ![image](https://user-images.githubusercontent.com/51030860/162643812-1ad33b30-42e6-4e81-97d5-327504758582.png)


## Docstrings & Testing

In this milestone, we added docstrings to our class methods using Google's recommended form of documentation and created a testing file which performs integration and unit testing such as checking that there are no null values for price of a product which can be seen in the code snippet below:

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

@classmethod
def setUpClass(cls): # The setup class is used to initialize our scraper once so we can perform different tests on that instance
    cls.options = input("Please input your desired product category from [most wished for, best seller]: ")
    cls.scrap_1 = AmazonUKScraper(cls.options, "computer & accessories", "https://www.amazon.co.uk/")
  
  # We will test whether there are any null values for price that our scraper retrieves
  # Convert the dict into a dataframe and check the price column has no NaNs by converting to type float (if NaN value would be string N/A and
  # hence will result in error)
  
  prod_data = self.scrap_1.read_product_file()
  prop_dict = self.scrap_1.prod_dict(prod_data, links, 10)

  dataframe = pd.DataFrame(prop_dict)
  for i, j  in enumerate(dataframe['Price']):
      dataframe['Price'][i] = re.sub("[^0-9.]", "", j) # Delete all non-numeric characters apart from '.'

  self.assertGreater(dataframe['Price'].str.replace('£', '').astype(float).sum(), 30) # The sum of price column should be at least greater than £30
  self.scrap_1.update_prod_file(prop_dict)

```
## Connecting and uploading to AWS S3 & PostgreSQL RDS

In this milestone, we add two additional methods to our scraper class where the upload_to_cloud method connects to S3 using Boto3, creates a bucket and uploads all the image files alongside the product json file. We use the os library to list out all the image files and then loop through them top upload the images to S3 one by one. Our next method, upload_dataframe_rds, asks the user to input the password and endpoint to connect to the AWS RDS database and then converts the dataframe obtained from a previous method to SQL and uploads to RDS which is connected to pgadmin.The name of the dataframe is based on the options attribute of the Amazon Scraper.

When connecting to RDS and S3, to keep the credentials private, we ask the user to input these as shown below. Below are the code snippets of how the files are uploaded to RDS and S3:


```python
# S3
key_id = input('Enter your AWS key id: ')
secret_key = input('Enter your AWS secret key: ')
bucket_name = input('Enter your bucket name: ')
region = input('Enter your regions: ')

s3 = boto3.client("s3", 
                region_name=region, 
                aws_access_key_id=key_id, 
                aws_secret_access_key=secret_key)

s3.upload_file('raw_data/data.json', bucket_name, 'raw_data/data.json')

for i in os.listdir('raw_data/images_'+self.options): # We list out all the image files and loop to upload the files to S3 one by one
    s3.upload_file('raw_data/images_'+self.options+'/'+i, bucket_name, 'raw_data/images_'+self.options+'/'+i)
    
# RDS
engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
conn = engine.connect()
empty = input("Do you want to overwrite the previous SQL data in RDS: ")
if empty.lower() == 'yes':
    if self.options == 'most wished for':
        df.to_sql("most_wished_for", conn, if_exists='replace', chunksize=60) # We have defined engine globally previously
    else:
        df.to_sql("best_seller", conn, if_exists='replace', chunksize=60)

  
```

## Containerzing using Docker and running on AWS EC2 instance

With this milestone, we add additional code to prevent our scraper from rescraping the data e.g., check if the product id already exists in the scraped dictionary. Moreover, we containerize our application where we use create a docker image for our webscraper so to avoid "it works on my machine" problem where all the required packages are installed using a requirements.txt file and dockerfile is used to build the docker image on top of a Python 3.8 image where it installs chromedriver and copies all the local files in the webscraper directory to the docker image. We can then run the docker image in a container and push it to dockerhub. This image is publicly accessible on DockerHub and can be pulled as follows: docker pull areeb297/amazon:latest

Afterward, we pull the image into our EC2 Ubuntu instance and we can run our scraper there using headless mode. To run the python file inside a docker container and EC2 instance, we need to add several arguments such as headless mode, no sandbox, set the window size to be able to capture all web elements etc. Shown below is a code snippet of how we add those options to be able to run the code using docker. Additionally, we show the code which prevents rescraping of products:


```python

chrome_options = ChromeOptions()
chrome_options.add_argument('--no-sandbox') 
chrome_options.add_argument('--disable-dev-shm-usage') 
chrome_options.add_argument("--window-size=1920, 1080")
chrome_options.add_argument("--remote-debugging-port=9222") 
s = Service(ChromeDriverManager().install())

self.options = options.lower() # To keep text consistent
self.items = items.lower() # To keep text consistent

if headless:
    chrome_options.add_argument('--headless')
    self.driver = webdriver.Chrome(service=s, options=options)
else:
    self.driver = webdriver.Chrome(service=s)

self.driver.get(url)

# To prevent rescraping:

# We check whether record exists in the SQL database connected with AWS RDS

prod_id_most_wished_for = pd.DataFrame(conn.execute('''SELECT "Unique Product ID" FROM most_wished_for'''))
prod_id_best_seller = pd.DataFrame(conn.execute('''SELECT "Unique Product ID" FROM best_seller'''))

if self.unique_id_gen(link) in prop_dict['Unique Product ID']: # This prevents rescraping if the product id is already scraped and added to the dict
    if self.options == 'most wished for':
        s = prod_id_most_wished_for['Unique Product ID'].str.contains(self.unique_id_gen(link)).sum() # There should only be one unique link
        if s == 1:
            print('Already scraped this product')
            continue
        elif s == 0:
            print('This record does not exist in the SQL data in AWS RDS & PgAdmin')
            pass
    else:
        s = prod_id_best_seller['Unique Product ID'].str.contains(self.unique_id_gen(link)).sum()
        if s == 1: # There should only be one unique link
            print('Already scraped this product')
            continue

        elif s == 0:
            print('This record does not exist in the SQL data in AWS RDS & PgAdmin')
            pass

```

## Monitoring using Prometheus & Grafana

Our next step is monitoring the docker containers using Prometheus and Grafana where we first create a container running Prometheus on the EC2 instance after pulling the Prometheus image from Dockerhub. We change the security inbound rules to be able to access port 9090 and see the Prometheus webpage. In our EC2 instance, we add a prometheus.yml file and a daemon.json file for monitoring docker containers using Prometheus. Afterward, prometheus was configured to scrape node exporter metrics for tracking OS metrics. Exporters like node are useful for exporting existing metrics from third party systems and making them available to Prometheus. Lastly, we install Grafana and we are able to then view OS and Docker metrics on localhost:3000 in a dashboard format as shown below which include visualizing metrics like container states, number of bytes in use etc:


Grafana

![image](https://user-images.githubusercontent.com/51030860/174436211-2179df05-24cf-40f5-95bb-49cd9c21d628.png)


## CI-CD Pipeline

The last milestone involves setting up a CI-CD pipeline using Github Actions where we setup the GitHub secret credentials for us to be able to push the new changes to our files to our docker image on Dockerhub. The CI-CD pipeline entails us pushing changes from our local machine to the Github repository using git which results in Github automatically building a new docker image and pushing it to our dockerhub account, thus replacing our older image. Shown in the image below are the steps taken by the Github workflow everytime we add a new commit to our repository:

![image](https://user-images.githubusercontent.com/51030860/174460078-cf96e7bb-741d-4783-9aa7-8f3e83953019.png)

Finally, a daily cronjob was set up to operate every 12-am-midnight to scrape and update the most-wished-for product database in AWS S3 and RDS. As we used an env file, we can easily change the product category by adding -e options='best seller' in the sudo docker statement. The images of the cronjob file and the result run on our ubuntu EC2 instance is shown below. The cronjob does the following:

* Restart the scraper every midnight on the EC2 instance by using 0 0 * * * in the cron file.
* Stops and kills the docker container after a successful run from the previous cronjob.
* Pulls the latest amazon scraper image from DockerHub & runs the scraper again the next midnight

![image](https://user-images.githubusercontent.com/51030860/177171542-01fa31a2-c165-46bd-b67a-874451a15aae.png)

![image](https://user-images.githubusercontent.com/51030860/177171563-754dfbd0-dd1c-4492-bf95-52eda8433268.png)

