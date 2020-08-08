from selenium import webdriver
from bs4 import BeautifulSoup
import time
import json
import urllib.request
import os
import copy
import re

#option to start chrome full screen
options = webdriver.ChromeOptions()
options.page_load_strategy = 'normal'
options.add_argument("--start-maximized")

#--------------------------------------------------------------------------------------------------------------
# Product URLs
#--------------------------------------------------------------------------------------------------------------

JSON = {}
subsubcategoryURL = ""
productsList = {}
productID = 1
page = 1
fileNumber = 1

#load subsubcategories JSON into memory
with open('/home/musaddiq/Desktop/Parts/3. Subsubcategories/Subsubcategories.json', 'r') as f:
	JSON = json.load(f)

print("Loaded Subsubcategories List JSON! Dictionary size: %s"%len(JSON))

for keys in JSON:

	try:
		#check if page counter has been reset
		if page == 0:
			page = 1

		#load particular product list data
		category = JSON[keys]["Parent Category"]
		subCategory = JSON[keys]["Parent Subcategory"]
		subsubCategory = JSON[keys]["Name"]
		subsubcategoryURL = JSON[keys]["URL"]
		subsubcategoryID = JSON[keys]['ID']

		print("\nSuccess reading data from JSON. Currently: \n Category = %s \n Subcategory = %s \n Subsubcategory = %s \n SubsubcategoryURL = %s \n SubsubcategoryID = %s of 5162" %(category,subCategory,subsubCategory,subsubcategoryURL,subsubcategoryID))

		#open Subsubcategory Page and load data

		#iterate through pages, while page counter has not been reset
		while page > 0:

			#create new driver with options
			print("\nOpening page %s of Subsubcategory [%s] %s, please wait..." %(page, subsubcategoryID, subsubCategory))
			driver = webdriver.Chrome("/snap/bin/chromium.chromedriver",options=options)

			#get webpage
			URL = subsubcategoryURL + "?&itemperpage=45&currentpage=" + str(page)
			driver.get(URL)
			print("\nSuccessfully opened webpage for subsubcategory %s [%s of 5162]!"%(subsubCategory,subsubcategoryID))

			#checking if last page reached
			try:
				driver.find_element_by_id("sectionCard-0")
				print("\nItems found!")

				#parse HTML
				print("\nProducts loaded! Parsing HTML...")
				content = driver.page_source
				contentCopy = copy.deepcopy(content) #copy for later use
				soup = BeautifulSoup(content,features="html.parser")
				print("\nSuccessfully parsed HTML!")

	#-------------------------------------------ARTICLE SECTION--------------------------------------------------------------------------------------------------------------------------------------

				#get article if exists, append to SubsubcategorieswWithArticles.json which, an element of which is already loaded into memeory. First page only
				if page == 1:
					try:
						driver.find_element_by_id("PartArticle")
						print("\nFound article on page!")

						#get articleHeading
						articleHeading = soup.find('div', attrs={'id':'ArticleHeading'}).text

						#get articleSubheading
						articleHTML = soup.find('div', attrs={'id':'ArticleSection'})

						#remove attributes from HTML
						attributes_to_del = ["style", "class", "id"]
						for attr_del in attributes_to_del:
							for p in soup.find_all():
								if attr_del in p.attrs:
									del p.attrs[attr_del]
d
				    		#prettify and cast to string
						pretty_article = articleHTML.prettify()
						article = str(pretty_article)

						#add article heading
						article = "<h2>" + articleHeading + "</h2>\n" + article
						print("\nGot article!")

						#update JSON file
						JSON[keys].update({
								'Article': {
									'Article Heading': articleHeading,
									'Article Text': article
								}
							}
						)

						print("\nAdded article %s for subsubcategory %s to JSON!"%(articleHeading,JSON[keys]['Name']))

						#write Subsubcategories With Articles JSON
						with open('/home/musaddiq/Desktop/Parts/3. Subsubcategories/Subsubcategories With Articles (639 onwards).json', 'w') as file:
							json.dump(JSON, file, indent = 2)

						print("\nWrote Article to Subsubcategories With Articles JSON file")

					except Exception as e:
						print("\nNo article to take :( OR already taken ;)\n")
						print(e)

	#-------------------------------------------PRODUCTS SECTION--------------------------------------------------------------------------------------------------------------------------------------

				#Using content HTML deep copy with tags because we deleted tags in original content
				soupNew = BeautifulSoup(contentCopy,features="html.parser")
				print("\nUsing HTML deep copy with tags. Making new Soup! :D\n")

				for data in soupNew.findAll(id=re.compile("sectionCard")):

					#get Product name
					productName = data.find(id=re.compile("productTitle")).text

					#get Product URL
					sourceURL = "https://www.carparts.com"
					productURL = data.find('a').get('href')
					productURL = sourceURL + productURL

					#add to subcategories dictionary
					productsList.update({
						"Product%s" %productID: {
							'ID':productID,
							'Name':productName,
							'URL':productURL,
							'Parent Subsubcategory':subsubCategory,
							'Parent Subcategory':subCategory,
							'Parent Category':category,
						}
					}
					)

					print("Getting Product [%s] %s :" %(productID,productName))

					#write Products List JSON
					productsFileName = "Products List " + str(fileNumber)
					with open(productsFileName, 'w') as file:
						json.dump(productsList, file, indent = 2)

					productID += 1

			except Exception as e:
				print(e)
				page = 0
				continue

			#next page
			driver.close()
			page += 1

		fileNumber += 1
		productsList.clear()
	except Exception as e:
		print(e)
		continue
