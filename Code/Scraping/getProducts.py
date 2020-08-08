from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import time
import json
import urllib.request
import os
import re
import math
import socket
from datetime import datetime

#--------------------------------------------------------------------------------------------------------------
# Get Product URLs
#--------------------------------------------------------------------------------------------------------------

JSON = {}
paths = []
socket.setdefaulttimeout(120)

#get file paths
for file in os.listdir('/home/spare/Desktop/Parts/4. Product List'):
	if file.startswith("Products List"):
		filePath = os.path.join("/home/spare/Desktop/Parts/4. Product List", file)
		paths.append(filePath)
paths.sort()

#--------------------------------------------------------------------------------------------------------------
# Get One Product Information
#--------------------------------------------------------------------------------------------------------------

def get_product_info(keys):
	fitmentPage = 1
	products = {}
	productID = keys[1]["ID"]
	productURL = keys[1]["URL"]

	#skipping done products
	with open("/home/spare/Desktop/Parts/5. Products/doneURLs.txt", 'r') as file:
		if productURL in file.read():
			#print("\nProduct Already Done! Skipping...")
			return
		file.close()

	subsubCategory = keys[1]["Parent Subsubcategory"]
	subCategory = keys[1]["Parent Subcategory"]
	category = keys[1]["Parent Category"]

	print(f"\nProcessing product [{productID}]. Opening webpage {productURL} \n \nPlease wait...")
	
	now = datetime.now()
	
	current_time = now.strftime("%H:%M:%S")
	print("Current Time =", current_time)
	
	options = webdriver.ChromeOptions()
	options.page_load_strategy = 'normal'
	options.add_argument("--start-maximized")

	#open product webpage
	driver = webdriver.Chrome("/snap/bin/chromium.chromedriver", options=options)
	driver.get(productURL)
	delay = 30 # seconds
	ready = False
	retries = 0
	while not ready:
		if retries < 10:
			try:
				myElem = WebDriverWait(driver, delay).until(lambda x: x.find_elements_by_id("my-gallery") or x.find_elements_by_css_selector("[data-test~=carousel-item-0]"))[0]
				time.sleep(15)
				print("\nPage is ready!")
				ready = True
			except TimeoutException:
				print("\nLoading took too much time!\n")
				driver.close()
				driver = webdriver.Chrome("/snap/bin/chromium.chromedriver", options=options)
				driver.get(productURL)
				ready = False
				retries += 1
				continue
		else:
			print("URL Broken! Skipping page.")
			with open("/home/spare/Desktop/Parts/5. Products/brokenURLs.txt", 'a') as brokenurlfile:
				brokenurlfile.write(productURL+"\n")
				brokenurlfile.close()
			with open("/home/spare/Desktop/Parts/5. Products/doneURLs.txt", 'a') as urlfile:
				urlfile.write(productURL+"\n")
				urlfile.close()
			return
	content = driver.page_source
	soup = BeautifulSoup(content,features="html.parser")

	productName = soup.find('div', attrs={'id':'skuTitle'}).get_text()

	highlightsRaw = [text for text in soup.find('div', attrs={'id':'highlights'}).stripped_strings]
	del highlightsRaw[0]

	i = 0
	while i < len(highlightsRaw):
		st = highlightsRaw[i]
		st = st[:-1]
		highlightsRaw[i] = st
		i += 2

	highlights = dict(zip(highlightsRaw[::2], highlightsRaw[1::2]))

	def x_in_y(query, base):
		try:
			l = len(query)
		except TypeError:
			l = 1
			query = type(base)((query,))

		for i in range(len(base)):
			if base[i:i+l] == query:
				return True
		return False

	def soupCleaner(soupToClean):
		soupToClean = soupToClean[5:]
		try:
			indexOfPrevious = soupToClean.index('Previous')
		except Exception as e:
			try:
				indexOfPrevious = soupToClean.index('1')
			except Exception as e:
				indexOfPrevious = len(soupToClean) + 1
		soupToClean = soupToClean[:indexOfPrevious]
		return(soupToClean)

	try:
		vehicleFitment = []
		donefitment = []
		try:
			tempList = [text for text in soup.find('div', attrs={'id':'vehicleFitment'}).stripped_strings]
			tempList = tempList[len(tempList)-1]
			tempList = tempList[:tempList.index("|")]
			pages = [int(s) for s in tempList.split() if s.isdigit()]

			start = pages[0]
			end = pages[1]
		except:
			start = 0
			end = 1
			pass

		for i in range(start,end):
			print(f"\nGathering Fitment Data, Page {i+1} of {end}")
			newContent = driver.page_source
			newSoup = BeautifulSoup(newContent,features="html.parser")
			vehicleFitmentRaw = [text for text in newSoup.find('div', attrs={'id':'vehicleFitment'}).stripped_strings]
			print(f"Step 1. Got Vehicle Fitment Raw \n {vehicleFitmentRaw} \n")

			if "Loading interface..." not in vehicleFitmentRaw:
				if not x_in_y(soupCleaner(vehicleFitmentRaw), vehicleFitment):
					vehicleFitment.extend(soupCleaner(vehicleFitmentRaw))
					print(f"Step 2. Extended Vehicle Fitement \n {soupCleaner(vehicleFitmentRaw)} \n ")
			
			try:
				tempContents = driver.page_source
				tempSoups = BeautifulSoup(tempContents,features="html.parser")
				tempWaitLists = [text for text in tempSoups.find('div', attrs={'id':'vehicleFitment'}).stripped_strings]
				print(f"Step 3. Temp Wait Lists To Match Page \n {soupCleaner(vehicleFitmentRaw)} \n ")
				try:
					pageList = [text for text in tempSoups.find('div', attrs={'id':'vehicleFitment'}).stripped_strings]
					pageList = pageList[len(pageList)-1]
					pageList = pageList[:pageList.index("|")]
					newpages = [int(s) for s in pageList.split() if s.isdigit()]

					newstart = newpages[0]
					newend = newpages[1]
				except:
					newstart = 0
					newend = 1
					pass
				
				print(f"Step 4. Done Fitment Pages = {donefitment} \nCurrent Page = {newstart} \nCurrent Iteration = {i}") 
				
				if newstart not in donefitment:
					print("New Page! Congratulations! ^_^")
					driver.find_element_by_id("pagination-next").click()
					donefitment.append(newstart)
					print(f"Step 5. Clicked BUTTON {i} TIME!")
				
				while True:
					tempContent = driver.page_source
					tempSoup = BeautifulSoup(tempContent,features="html.parser")
					tempWaitList = [text for text in tempSoup.find('div', attrs={'id':'vehicleFitment'}).stripped_strings]
					print(f"Step 8. Temp Wait List = {tempWaitList}")
						
					try:
						pageListfinal = [text for text in tempSoup.find('div', attrs={'id':'vehicleFitment'}).stripped_strings]
						pageListfinal = pageListfinal[len(pageListfinal)-1]
						pageListfinal = pageListfinal[:pageListfinal.index("|")]
						newpagesfinal = [int(s) for s in pageListfinal.split() if s.isdigit()]

						newstartfinal = newpagesfinal[0]
						newendfinal = newpagesfinal[1]
					except:
						newstartfinal = 0
						newendfinal = 1
						pass
					
					if "Loading interface..." not in tempWaitList:
						if not x_in_y(soupCleaner(tempWaitList), vehicleFitment):
							vehicleFitment.extend(soupCleaner(tempWaitList))
							print(f"Step 9. Added! = {soupCleaner(tempWaitList)}")
							break
					elif newstartfinal in donefitment:
						time.sleep(2)
						driver.find_element_by_id("pagination-next").click()
						print("Not match,  SOME PROBLEMMMMMMMMMMMMMMMMMMMMMM!!!!!!!!!!!!!!!!!!")
						time.sleep(5)
						continue
					else:
						print("CONTINUING LIKE a REEEEEEEEEEEEEEEEEEEEEEEEEEEEETARD")
						continue
					print("nice continue:")
			except Exception as e:
				print(e)
				continue



		vehicleFitmentDict = {}
		fitmentID = 1
		for value in range(0,len(vehicleFitment),4):
			try:
				vehicleFitmentDict.update({
					fitmentID : {
					'VehicleName':vehicleFitment[value],
					'Submodel':vehicleFitment[value+1],
					'Engine':vehicleFitment[value+2],
					'Fitment Information':vehicleFitment[value+3]
					}
				})
				fitmentID += 1
			except Exception as e:
				print(e)
				pass
	except AttributeError:
		vehicleFitmentDict = "Universal Fitment"
		pass

	#get product images
	try:
		imagesoup = soup.findAll('div', attrs={'data-test':'carousel-viewer-wrap'})
		image_urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(imagesoup[0]))
		fullImages = []
		squareImages = image_urls
		for _ in image_urls:
			fullImages.append(_[:66] + _[137:])

		fullImageID = 1
		fullImagePaths = []
		for _ in fullImages:
			if not os.path.exists("/home/spare/Desktop/Parts/5. Products/Images/Product %s/Full"%(productID)):
				os.makedirs("/home/spare/Desktop/Parts/5. Products/Images/Product %s/Full"%(productID))

			print("Downloading Image for Product %s from %s" %(productName,_))
			imagePath = "/home/spare/Desktop/Parts/5. Products/Images/Product %s/Full/Product %s Full Image %s"%(productID,productID,fullImageID)
			imagePaths = "./Images/Product %s/Full/Product %s Full Image %s"%(productID,productID,fullImageID)
			fullImagePaths.append(imagePaths)
			try:
				urllib.request.urlretrieve(_, imagePath)
				fullImageID += 1
			except Exception as e:
				print(e)
				continue

		squareImageID = 1
		squareImagePaths = []
		for _ in squareImages:
			if not os.path.exists("/home/spare/Desktop/Parts/5. Products/Images/Product %s/Square"%(productID)):
				os.makedirs("/home/spare/Desktop/Parts/5. Products/Images/Product %s/Square"%(productID))

			print("Downloading Image for Product %s from %s" %(productName,_))
			imagePath = "/home/spare/Desktop/Parts/5. Products/Images/Product %s/Square/Product %s Square Image %s"%(productID,productID,squareImageID)
			imagePaths = "./Images/Product %s/Square/Product %s Square Image %s"%(productID,productID,squareImageID)
			squareImagePaths.append(imagePaths)
			try:
				urllib.request.urlretrieve(_, imagePath)
				squareImageID += 1
			except Exception as e:
				print(e)
				continue
	except IndexError:
		try:
			try:
				imagesoup = soup.findAll('div', attrs={'id':'my-gallery'})
				image_urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(imagesoup[0]))
				image_url_single = image_urls[0]
			except Exception as e:
				print(e)
				test = driver.find_elements_by_id("my-gallery")
				print("No Images Found!")
				image_url_single = "https://upload.wikimedia.org/wikipedia/en/f/f9/No-image-available.jpg"
			
			
			test = driver.find_elements_by_id("my-gallery")
			print("One Image Found!")
			if not os.path.exists("/home/spare/Desktop/Parts/5. Products/Images/Product %s/Full"%(productID)):
					os.makedirs("/home/spare/Desktop/Parts/5. Products/Images/Product %s/Full"%(productID))
			imagePath = "/home/spare/Desktop/Parts/5. Products/Images/Product %s/Full/Product %s Full Image 1"%(productID,productID)
			try:
					urllib.request.urlretrieve(image_url_single, imagePath)
					print("Downloaded 1 Full Image")
			except Exception as e:
				print(e)
				pass
			imagePaths = "./Images/Product %s/Full/Product %s Full Image 1"%(productID,productID)
			fullImagePaths = []
			fullImagePaths.append(imagePaths)

			if not os.path.exists("/home/spare/Desktop/Parts/5. Products/Images/Product %s/Square"%(productID)):
				os.makedirs("/home/spare/Desktop/Parts/5. Products/Images/Product %s/Square"%(productID))
			imagePath = "/home/spare/Desktop/Parts/5. Products/Images/Product %s/Square/Product %s Square Image 1"%(productID,productID)
			try:
					urllib.request.urlretrieve(image_url_single, imagePath)
					print("Downloaded 1 Square Image")
			except Exception as e:
				print(e)
				pass

			imagePaths = "./Images/Product %s/Square/Product %s Square Image 1"%(productID,productID)
			squareImagePaths = []
			squareImagePaths.append(imagePaths)
		except Exception as e:
			print(e)
			pass
		pass


	#get product pricing
	try:
		pricingLocator = soup.find('div', attrs={'id':'skuTitle'}).next_sibling
		pricingLocator = pricingLocator.children
		pricingList = []
		for _ in pricingLocator:
			dummy = _
		for childs in dummy:
			pricingList.append(childs.get_text())
	except Exception as e:
		print(e)
		pass

	if "You Save" in pricingList[2]:
		pricingUSD = pricingList[0]
		#pricingUSD = re.sub("[^\d\.]", "", pricingUSD)
		if "," in pricingUSD:
			pricingUSD = pricingUSD.replace(",","")
		try:
			pricingUSD = float(pricingUSD[1:])
		except ValueError:
			try:
				pricingUSD = float(pricingUSD[1:pricingUSD.index("+")])
			except ValueError:
				return
		
		
		pricingSAR = float(pricingUSD)*3.75

		listPriceUSD = pricingList[2]
		groups = listPriceUSD.split(':')
		listPriceUSD = groups[len(groups)-1]
		#listPriceUSD = re.sub("[^\d\.]", "", listPriceUSD)
		if "," in listPriceUSD:
			listPriceUSD = listPriceUSD.replace(",","")
		listPriceUSD = float(listPriceUSD[2:])

		listPriceSAR = float(listPriceUSD)*3.75

		try:
			manfNum = pricingList[4]
			manfNum = manfNum[manfNum.index("#")+1:]
		except ValueError:
			manfNum = "Not Available"
	else:
		pricingUSD = pricingList[0]
		if "," in pricingUSD:
			pricingUSD = pricingUSD.replace(",","")
		try:
			pricingUSD = float(pricingUSD[1:])
		except ValueError:
			try:
				pricingUSD = float(pricingUSD[1:pricingUSD.index("+")])
			except ValueError:
				return

		pricingSAR = float(pricingUSD)*3.75

		listPriceUSD = pricingUSD
		listPriceSAR = pricingSAR

		try:
			manfNum = pricingList[2]
			manfNum = manfNum[manfNum.index("#")+1:]
		except ValueError:
			manfNum = "Not Available"

	information = soup.find('div', attrs={'id':'productInfo'})
	attributes_to_del = ["style", "class", "id", "target"]
	for attr_del in attributes_to_del:
			for p in information.find_all():
				if attr_del in p.attrs:
					del p.attrs[attr_del]
	productInfo = ""
	for child in information.children:
		productInfo = (str(child))

	#jsonify
	newProduct = {
		"Product%s" %productID: {
			'ID':productID,
			'Name':productName,
			'URL':productURL,
			'Parent Subsubcategory':subsubCategory,
			'Parent Subcategory':subCategory,
			'Parent Category':category,
			'Price': {
					'Price (USD)': pricingUSD,
					'Price (SAR)': pricingSAR,
					'List Price (USD)': listPriceUSD,
					'List Price (SAR)': listPriceSAR,
					'Discount (USD)': listPriceUSD - pricingUSD,
					'Discount (SAR)': listPriceSAR - pricingSAR
					},
			'Manufacturer Number': manfNum,
			'Information': productInfo,
			'Highlights': highlights,
			'Vehicle Fitment': vehicleFitmentDict,
			'Images': {
				'Full':fullImagePaths,
				'Square':squareImagePaths
				}
			}
		}

	print(json.dumps(newProduct, indent = 2))

	writing = json.dumps(newProduct, indent = 2)

	productsFileName = "/home/spare/Desktop/Parts/5. Products/Products/Product " + str(productID) + ".json"

	with open(productsFileName, 'w') as file:
		file.write(writing)
		file.close()

	with open("/home/spare/Desktop/Parts/5. Products/doneURLs.txt", 'a') as urlfile:
		urlfile.write(productURL+"\n")
		urlfile.close()

	if 'driver' in locals():
		driver.quit()

#--------------------------------------------------------------------------------------------------------------
# Get ALL Products Information
#--------------------------------------------------------------------------------------------------------------

threads = []

for path in paths:
	#load productsList JSON into memory
	with open(path, 'r') as f:
		JSON = json.load(f)

	print(f"\nOpening file {path}")

	print("\nLoaded Products List JSON! Dictionary size: %s"%len(JSON))
	for items in JSON.items():
		get_product_info(items)
