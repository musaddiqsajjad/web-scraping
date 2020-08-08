from selenium import webdriver
from bs4 import BeautifulSoup
import time
import json
import urllib.request
import os

#option to start chrome full screen
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

#--------------------------------------------------------------------------------------------------------------
# Subcategories
#--------------------------------------------------------------------------------------------------------------

#initialize dictionary
subcategories = {}
subcategoryID = 1

subsubcategories = {}
subsubcategoryID = 1
subsubcategoriesURLs = {}


#full range(8)---------------------------------------------------------------------
for i in range(8):

	print("Finding Subcategories for Category", category[i])

	#create new driver with options
	driver = webdriver.Chrome("/snap/bin/chromium.chromedriver",options=options)
	
	#get webpage
	driver.get(url[i])

	#click on see more categories if available
	try:
		driver.find_element_by_id("seeMoreCategories").click()
	except:
		pass
	finally:
		#initialize BeautifulSoup
		content = driver.page_source
		soup = BeautifulSoup(content,features="html.parser")
		
		#get subcategories
		for data in soup.findAll('div', attrs={'class':'StyledBox-sc-13pk1d4-0 cmTaTX'}):
			
			#get subcategory name
			subcategoryName = data.text
			
			#get subcategory URL
			URL = data.find('a',attrs={'class':'jxlue7-0 druKYc'}).get('href')
			subcategoryURL = source + URL[1:]
			
			#get subcategory Image
			if not os.path.exists("./Images/%s"%category[i]):
				os.makedirs("./Images/%s"%category[i])
			
			imageURL = data.find("img").get('data-src')
			imageURL = imageURL[:38]+imageURL[103:]
			print("Downloading Image for Subcategory %s" %subcategoryName)
			imagePath = "./Images/%s/%s.jpg"%(category[i],subcategoryName)
			urllib.request.urlretrieve(imageURL, imagePath)
			
			#get subcategory parent category
			subcategoryParentCategory = category[i]
			
			#get subsubcategories, all data and stuff--------------------------------------------------------
			
			#create new driver with options
			driverNew = webdriver.Chrome("/snap/bin/chromium.chromedriver",options=options)
			
			#get subcategory webpage to see subsubcategory list
			driverNew.get(subcategoryURL)
			
			#click on see more categories if available
			try:
				driverNew.find_element_by_id("seeMoreCategories").click()
			except:
				pass
			finally:
				
				print("Opening Subsubcategories for %s" %subcategoryName)
				
				#initialize BeautifulSoup
				contentNew = driverNew.page_source
				soupNew = BeautifulSoup(contentNew,features="html.parser")
				
				#get subsubcategories
				for dataNew in soupNew.findAll('div', attrs={'class':'StyledBox-sc-13pk1d4-0 cmTaTX'}):
					
					#get subsubcategory name
					subsubcategoryName = dataNew.text
					if "/" in subsubcategoryName:
						print("Oops, / found in name. Sanitizing...")
						subsubcategoryName = subsubcategoryName.replace("/","")
						print("Sanitized: %s"%subsubcategoryName)
					elif "\\" in subsubcategoryName:
						print("Oops, BACKSLASH found in name. Sanitizing...")
						subsubcategoryName = subsubcategoryName.replace("\\","")
						print("Sanitized: %s"%subsubcategoryName)	
					
					#getsubsubcategory URL
					URLNew = dataNew.find('a',attrs={'class':'jxlue7-0 druKYc'}).get('href')
					subsubcategoryURL = source + URLNew[1:]
					subsubcategoriesURLs.update({subsubcategoryName:subsubcategoryURL})
					
					#get subsubcategory Image
					if not os.path.exists("/home/musaddiq/Desktop/Parts/Subsubcategories/Images/%s/%s"%(category[i],subcategoryName)):
						os.makedirs("/home/musaddiq/Desktop/Parts/Subsubcategories/Images/%s/%s"%(category[i],subcategoryName))
					imageURLNew = dataNew.find("img").get('data-src')
					print(imageURLNew)
					imageURLNew = imageURLNew[:38]+imageURLNew[103:]
					print("Downloading Image for Subsubcategory %s from %s" %(subsubcategoryName,imageURLNew))
					imagePathNew = "/home/musaddiq/Desktop/Parts/Subsubcategories/Images/%s/%s/%s.jpg"%(category[i],subcategoryName, subsubcategoryName)
					try:
						if not os.path.exists(imagePathNew):
							try:
								urllib.request.urlretrieve(imageURLNew, imagePathNew)						
							except:
								try:
									smallImageURL = dataNew.find("img").get('data-src')
									print("Full Image Not Found! Getting smaller image from %s", smallImageURL)
									urllib.request.urlretrieve(smallImageURL, imagePathNew)
								except:							
									print("No Image Found! Getting default No Image Found picture...")
									urllib.request.urlretrieve("https://upload.wikimedia.org/wikipedia/en/f/f9/No-image-available.jpg", imagePathNew)
					except:
						pass
					finally:
						#get subsubcategory parent subcategory
						subsubcategoryParentCategory = subcategoryName
						
						#add to subcategories dictionary
						subsubcategories.update({
						"Subsubcategory%s" %subsubcategoryID: {
							'ID':subsubcategoryID,
							'Name':subsubcategoryName,
							'URL':subsubcategoryURL,
							'Image':"."+imagePathNew[42:],
							'Parent Subcategory':subsubcategoryParentCategory,
							'Parent Category':subcategoryParentCategory,
							}
						})
					print("writing to JSON..")
					print(json.dumps(subsubcategories, indent=2))
					print(subsubcategoriesURLs)
					subsubcategoryID += 1
						
					#close window
					driverNew.quit()
			
			#------------------------------------------------------------------------------------------------
			
			#add to subcategories dictionary
			subcategories.update({
			"Subcategory%s" %subcategoryID: {
				'ID':subcategoryID,
				'Name':subcategoryName,
				'URL':subcategoryURL,
				'Image':imagePath,
				'Parent Category':subcategoryParentCategory,
				}
			})
			
			subcategoryID += 1
		
		#write subsubcategories JSON file
		with open('/home/musaddiq/Desktop/Parts/Subsubcategories/Subsubcategories.json', 'w') as file:
			json.dump(subsubcategories, file, indent = 2)
		
		#write subsubcategoriesURLS JSON file
		with open('/home/musaddiq/Desktop/Parts/Subsubcategories/SubsubcategoriesURLS.json', 'w') as file:
			json.dump(subsubcategoriesURLs, file, indent = 2)
		
		#close window
		driver.quit()
		
	print(json.dumps(subcategories))
		
with open('Subcategories.json', 'w') as file:
	json.dump(subcategories, file, indent = 2)




