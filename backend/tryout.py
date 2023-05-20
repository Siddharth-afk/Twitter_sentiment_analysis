import requests      
from bs4 import BeautifulSoup
import re

# Parse the HTML content of the page using Beautiful Soup
#soup = BeautifulSoup(response.content, 'html.parser')
file = open("myfile.txt", "w")

search = "maruti"

url = ('https://newsapi.org/v2/everything?'
       f'q={search}&'
       'apiKey=6323d4d8a8584c5d99ddd4c85a134c07')

print(url)

response = requests.get(url)

tot = response.json()
val = (d['description'] for d in tot['articles'])
for i in val:
    a = re.sub("<[^<]+?>", "", i)
    file.write(a + '\n')


# Extract the text content of the page by selecting all the "p" elements within the content_div

""" a = re.sub("<[^<]+?>", "", soup.get_text())
file.write(a) """

