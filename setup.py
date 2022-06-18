from setuptools import setup
from setuptools import find_packages

setup(
    name='areeb_amazon_scraper',
    version='0.0.1',    
    description='Package that scrapes the computer & accessories products in the best seller and most wished for categories. The data is uploaded to AWS S3 and AWS PostgresSQL RDS',
    url='https://github.com/Areeb297/Data-Collection-Pipeline.git',
    author='Areeb Shafqat',
    license='MIT',
    packages=find_packages(),
    install_requires=['sqlalchemy', 'psycopg2-binary', 'selenium', 'pandas', 'webdriver-manager', 'requests', 'tqdm', 'pydantic', 'boto3', 'uuid', 'typing'],
) 
