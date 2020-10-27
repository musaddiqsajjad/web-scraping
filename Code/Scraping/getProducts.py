#version 1/10/2020 after sold out no price convert to float issue (added try catch in listpriceUSD) ... and adding a few scroll to home keys because highlights issue
#192.168.200.69

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time
import json
import urllib.request
import os
import re
import math
import socket
import copy
from datetime import datetime
from random import randint
from fake_useragent import UserAgent



#ping test
import subprocess, platform
def pingOk(sHost):
	try:
		output = subprocess.check_output("ping -{} 1 {}".format('n' if platform.system().lower()=="windows" else 'c', sHost), shell=True)
	except Exception as e:
		return False
	return True

#--------------------------------------------------------------------------------------------------------------
# Get Product URLs
#--------------------------------------------------------------------------------------------------------------

JSON = {}
paths = []
socket.setdefaulttimeout(120)

#get file paths
for file in os.listdir('/home/musaddiq/Desktop/Parts/4. Product List'):
	if file.startswith("Products List"):
		filePath = os.path.join("/home/musaddiq/Desktop/Parts/4. Product List", file)
		paths.append(filePath)
paths.sort()

#--------------------------------------------------------------------------------------------------------------
# Get One Product Information
#--------------------------------------------------------------------------------------------------------------

def get_product_info(keys):

	try:

		fitmentPage = 1
		products = {}
		productID = keys[1]["ID"]
		productURL = keys[1]["URL"]
		productsFileName = "/home/musaddiq/Desktop/Parts/5. Products/Products/Product " + str(productID) + ".json"
		
		#--------------------------------------------------------------------------------------------------------------
		#skipping done products
		with open("/home/musaddiq/Desktop/Parts/5. Products/doneURLs.txt", 'r') as file:
			if productURL in file.read():
				#print("\nProduct Already Done! Skipping...")
				return
			file.close()

		if (os.path.exists("/home/musaddiq/Desktop/Parts/5. Products/Images/Product %s/Full"%(productID)) and len(os.listdir("/home/musaddiq/Desktop/Parts/5. Products/Images/Product %s/Full"%(productID))) > 1 and os.path.exists(productsFileName)):
			print("Multiple Images gathered before and JSON exists, skipping product safely")
			with open("/home/musaddiq/Desktop/Parts/5. Products/doneURLs.txt", 'a') as urlfile:
					urlfile.write(productURL+"\n")
					urlfile.close()
			return

		#--------------------------------------------------------------------------------------------------------------

		subsubCategory = keys[1]["Parent Subsubcategory"]
		subCategory = keys[1]["Parent Subcategory"]
		category = keys[1]["Parent Category"]

		print(f"\nProcessing product [{productID}]. Opening webpage {productURL} \n \nPlease wait...")
		
		#--------------------------------------------------------------------------------------------------------------
		
		#Skipping products that only need images
		
		if os.path.exists(productsFileName):
			onlyneedimages = True
			print("\nOnly images are needed!")
		else:
			onlyneedimages = False
			print("\nProcessing complete product...")
		
		#--------------------------------------------------------------------------------------------------------------
		
		now = datetime.now()

		current_time = now.strftime("%H:%M:%S")
		print("\nCurrent Time =", current_time)

		#--------------------------------------------------------------------------------------------------------------

		#adding a fake useragent
		ua = UserAgent()
		userAgent = ua.random
		print(userAgent)
		options = webdriver.ChromeOptions()
		options.page_load_strategy = 'normal'
		options.add_argument("--start-maximized")
		options.add_argument("--disable-infobars")
		options.add_argument("--disable-extensions")
		options.add_argument("--disable-cache")
		options.add_argument("--disable-application-cache")
		options.add_argument("--disable-dev-shm-usage")
		options.add_argument("--dns-prefetch-disable")
		options.add_argument(f'user-agent={userAgent}')
		#options.add_argument("--proxy-server=54.229.215.97:8888")

		#--------------------------------------------------------------------------------------------------------------

		#open product webpage
		delay = 30 # seconds
		ready = False
		retries = 0
		
		#--------------------------------------------------------------------------------------------------------------
		
		#opening page
		while not ready:
			time.sleep(randint(10,25))
			if retries < 5:
				try:
					waiting = True
					
					#ping test
					
					print("\nPinging carparts.com...\n")
					with open("/home/musaddiq/Desktop/Parts/5. Products/wget.txt", 'w') as wget:
						wget.write("")
					
					while waiting:
						os.system('wget carparts.com -O wget.txt >/dev/null 2>&1')
						if not os.path.getsize("wget.txt") == 0:
							print("Ping success!")
							waiting=False
							break
						else:
							continue
							
					#check elements loaded
					driver = webdriver.Chrome("/snap/bin/chromium.chromedriver", options=options)
					driver.get(productURL)
					myElem = WebDriverWait(driver, delay).until(lambda x: x.find_elements_by_id("my-gallery") or x.find_elements_by_css_selector("[data-test~=carousel-item-0]") and x.find_elements_by_id("highlights"))[0]
					time.sleep(randint(10,15))
					
					print("\nPage is ready!")
					ready = True
					
				#--------------------------------------------------------------------------------------------------------------	
					
				except TimeoutException:
				
					print("\nLoading took too much time!\n")
					
					#check if listing page, skip if yes
					listingpage = driver.find_elements_by_id("MainSectionGrid")

					if listingpage:
						print("\nURL Broken! Skipping page.")
						with open("/home/musaddiq/Desktop/Parts/5. Products/brokenURLs.txt", 'a') as brokenurlfile:
							brokenurlfile.write(productURL+"\n")
							brokenurlfile.close()
						with open("/home/musaddiq/Desktop/Parts/5. Products/doneURLs.txt", 'a') as urlfile:
							urlfile.write(productURL+"\n")
							urlfile.close()
						driver.close()
						return

					driver.close()
					ready = False
					retries += 1
					continue
				except WebDriverException:
					print("\nDNS ERROR! Web page failed to load. Reloading~\n")
					driver.close()
					ready = False
					retries += 1
					continue
			else:
				print("\nURL Broken! Skipping page.")
				with open("/home/musaddiq/Desktop/Parts/5. Products/brokenURLs.txt", 'a') as brokenurlfile:
					brokenurlfile.write(productURL+"\n")
					brokenurlfile.close()
				with open("/home/musaddiq/Desktop/Parts/5. Products/doneURLs.txt", 'a') as urlfile:
					urlfile.write(productURL+"\n")
					urlfile.close()
				return
		
		#--------------------------------------------------------------------------------------------------------------
		
		print("\nNavigating to end of page")
		driver.find_element_by_xpath('/html/body').send_keys(Keys.CONTROL+Keys.END)
		time.sleep(randint(1,2))
		driver.find_element_by_xpath('/html/body').send_keys(Keys.CONTROL+Keys.END)
		time.sleep(randint(1,2))
		driver.find_element_by_xpath('/html/body').send_keys(Keys.CONTROL+Keys.END)
		time.sleep(randint(1,2))
		driver.find_element_by_xpath('/html/body').send_keys(Keys.CONTROL+Keys.END)
		time.sleep(randint(1,2))
		driver.find_element_by_xpath('/html/body').send_keys(Keys.CONTROL+Keys.END)
		time.sleep(randint(1,2))
		driver.find_element_by_xpath('/html/body').send_keys(Keys.CONTROL+Keys.END)
		time.sleep(randint(1,2))
		driver.find_element_by_xpath('/html/body').send_keys(Keys.CONTROL+Keys.END)
		time.sleep(randint(1,2))
		driver.find_element_by_xpath('/html/body').send_keys(Keys.CONTROL+Keys.END)
		time.sleep(randint(1,2))
		driver.find_element_by_xpath('/html/body').send_keys(Keys.CONTROL+Keys.HOME)
		time.sleep(randint(1,2))
		driver.find_element_by_xpath('/html/body').send_keys(Keys.CONTROL+Keys.HOME)
		time.sleep(randint(1,2))

		if not onlyneedimages:
			
			#--------------------------------------------------------------------------------------------------------------
			
			#get highlights
			
			time.sleep(randint(10,20))

			print("\nGetting Highlights")

			content = driver.page_source
			contentCopy = copy.deepcopy(content) #copy for later use in pricing

			time.sleep(randint(3,5))

			content = driver.page_source
			soup = BeautifulSoup(content,features="html.parser")

			productName = soup.find('div', attrs={'id':'skuTitle'}).get_text()

			highlightselement = driver.find_element_by_id("highlights")

			actions = ActionChains(driver)
			actions.move_to_element(highlightselement).perform()

			time.sleep(randint(1,5))

			#with open("/home/musaddiq/Desktop/Parts/5. Products/highlightsSoup.txt", 'w') as high:
			#	high.write(soup.get_text())
			#	high.close()

			highlightsRaw = [text for text in soup.find('div', attrs={'id':'highlights'}).stripped_strings]
			del highlightsRaw[0]

			i = 0
			while i < len(highlightsRaw):
				st = highlightsRaw[i]
				st = st[:-1]
				highlightsRaw[i] = st
				i += 2

			highlights = dict(zip(highlightsRaw[::2], highlightsRaw[1::2]))
			
			#--------------------------------------------------------------------------------------------------------------

			#function if string found in list
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

			#--------------------------------------------------------------------------------------------------------------

			#function to clean soup string
			
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

			#--------------------------------------------------------------------------------------------------------------

			#get Fitment Data
			try:
				print("\nGetting Fitment")

				vehicleFitment = []
				time.sleep(randint(10,15))

				fitmentelement = driver.find_element_by_id("vehicleFitment")
				actions = ActionChains(driver)
				actions.move_to_element(fitmentelement).perform()

				#--------------------------------------------------------------------------------------------------------------
				
				#getting page numbers				
				try:
				
					#get page numbers
					pageList = [text for text in soup.find('div', attrs={'id':'vehicleFitment'}).stripped_strings]
					pageList = pageList[len(pageList)-1]
					pageList1 = pageList[:pageList.index("|")]
					pages = [int(s) for s in pageList1.split() if s.isdigit()]

					pageList2 = pageList[pageList.index("|"):]
					totalItems = [int(s) for s in pageList2.split() if s.isdigit()]
					totalItems = totalItems[2]

					print(f"\nTotal Items To Gather = {totalItems}")

					start = pages[0]
					end = pages[1]
				except:
					totalItems = 0
					start = 0
					end = 1
					pass

				#--------------------------------------------------------------------------------------------------------------

				#get Fitment
				try:
					time.sleep(randint(1,2))
					print(f"\nGathering Fitment Data, Page 1 of {end}")
					newContent = driver.page_source
					newSoup = BeautifulSoup(newContent,features="html.parser")
					vehicleFitmentRaw = [text for text in newSoup.find('div', attrs={'id':'vehicleFitment'}).stripped_strings]

					if "Loading interface..." not in vehicleFitmentRaw:
						if not x_in_y(soupCleaner(vehicleFitmentRaw), vehicleFitment):
							vehicleFitment.extend(soupCleaner(vehicleFitmentRaw))
							print(soupCleaner(vehicleFitmentRaw))
							print("Got it!")
				except AttributeError:
					vehicleFitmentDict = "Universal Fitment"
					pass

				if not start == 0:

					for i in range(start+1,end+1):

						time.sleep(randint(10,15))
						print(f"\nGathering Fitment Data, Page {i} of {end}")

						driver.find_element_by_id("pagination-next").click()

						time.sleep(randint(2,4))

						start = time.time()

						while time.time() - start < 180:
							tempContent = driver.page_source
							tempSoup = BeautifulSoup(tempContent,features="html.parser")
							tempWaitList = [text for text in tempSoup.find('div', attrs={'id':'vehicleFitment'}).stripped_strings]

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

							currentPage = newstartfinal

							if "Loading interface..." not in tempWaitList:
								if not x_in_y(soupCleaner(tempWaitList), vehicleFitment):
									vehicleFitment.extend(soupCleaner(tempWaitList))
									print(soupCleaner(tempWaitList))
									print("\nGot it!")

							if "Loading interface..." not in tempWaitList and x_in_y(soupCleaner(tempWaitList), vehicleFitment) and currentPage == i:
								break

							if "Loading interface..." in tempWaitList:
								time.sleep(5)
								continue
				#--------------------------------------------------------------------------------------------------------------
				
				
				#close if not all fitment gathered
				if not (totalItems*3.5 <= len(vehicleFitment) <= totalItems*4.5) and not totalItems == 0:
					print(len(vehicleFitment))
					print(totalItems*4)
					print("\n Closing due to incomplete fitment")
					os.system('python3 close.py')


				#write to dict
				try:
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
			except NoSuchElementException:
				vehicleFitmentDict = "Not Available"
				pass
			
		#--------------------------------------------------------------------------------------------------------------
			
		#get product images
		print("\nGetting Images")
		driver.find_element_by_xpath('/html/body').send_keys(Keys.CONTROL+Keys.HOME)
		time.sleep(randint(1,2))
		driver.find_element_by_xpath('/html/body').send_keys(Keys.CONTROL+Keys.HOME)
		time.sleep(randint(1,2))
		driver.find_element_by_xpath('/html/body').send_keys(Keys.CONTROL+Keys.HOME)
		time.sleep(randint(1,2))
		driver.find_element_by_xpath('/html/body').send_keys(Keys.CONTROL+Keys.HOME)
		time.sleep(randint(1,2))

		try:
			imageContent = driver.page_source
			imageSoup = BeautifulSoup(imageContent,features="html.parser")
			imagesoup = imageSoup.findAll('div', attrs={'data-test':'carousel-viewer-wrap'})
			image_urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(imagesoup[0]))
			fullImages = []
			squareImages = image_urls
			for _ in image_urls:
				fullImages.append(_[:66] + _[137:])

			fullImageID = 1
			fullImagePaths = []
			for _ in fullImages:
				time.sleep(randint(1,5))
				if not os.path.exists("/home/musaddiq/Desktop/Parts/5. Products/Images/Product %s/Full"%(productID)):
					os.makedirs("/home/musaddiq/Desktop/Parts/5. Products/Images/Product %s/Full"%(productID))

				print("\nDownloading Image for Product from %s" %(_))
				imagePath = "/home/musaddiq/Desktop/Parts/5. Products/Images/Product %s/Full/Product %s Full Image %s"%(productID,productID,fullImageID)
				imagePaths = "./Images/Product %s/Full/Product %s Full Image %s"%(productID,productID,fullImageID)
				retryDownload = 0
				while retryDownload < 20:
					try:
						urllib.request.urlretrieve(_, imagePath)
						print("Downloaded Full Image %s" %(fullImageID))
						fullImagePaths.append(imagePaths)
						fullImageID += 1
						break
					except urllib.error.URLError:
						retryDownload += 1
						continue
					except urllib.error.HTTPError:
						retryDownload += 1
						break
					except Exception as e:
						retryDownload += 1
						print(e)
						continue
			'''
			squareImageID = 1
			squareImagePaths = []
			for _ in squareImages:
				time.sleep(randint(1,5))
				if not os.path.exists("/home/musaddiq/Desktop/Parts/5. Products/Images/Product %s/Square"%(productID)):
					os.makedirs("/home/musaddiq/Desktop/Parts/5. Products/Images/Product %s/Square"%(productID))

				print("Downloading Image for Product %s from %s" %(productName,_))
				imagePath = "/home/musaddiq/Desktop/Parts/5. Products/Images/Product %s/Square/Product %s Square Image %s"%(productID,productID,squareImageID)
				imagePaths = "./Images/Product %s/Square/Product %s Square Image %s"%(productID,productID,squareImageID)
				squareImagePaths.append(imagePaths)
				retryDownload = 0
				while retryDownload < 20:
					try:
						urllib.request.urlretrieve(_, imagePath)
						print("Downloaded Square Image")
						squareImageID += 1
						break
					except urllib.error.URLError:
						retryDownload += 1
						continue
					except urllib.error.HTTPError:
						retryDownload += 1
						break
					except Exception as e:
						retryDownload += 1
						print(e)
						continue
			'''
		except IndexError:
			try:
				try:
					imageContent = driver.page_source
					imageSoup = BeautifulSoup(imageContent,features="html.parser")
					imagesoup = imageSoup.findAll('div', attrs={'id':'my-gallery'})
					image_urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(imagesoup[0]))
					image_url_single = image_urls[0]
					print("\nOne Image Found!")
				except Exception as e:
					print(e)
					test = driver.find_elements_by_id("my-gallery")
					print("\nNo Images Found! Getting Standard Image ---------------------------------")
					image_url_single = "https://upload.wikimedia.org/wikipedia/en/f/f9/No-image-available.jpg"

				test = driver.find_elements_by_id("my-gallery")

				if not os.path.exists("/home/musaddiq/Desktop/Parts/5. Products/Images/Product %s/Full"%(productID)):
						os.makedirs("/home/musaddiq/Desktop/Parts/5. Products/Images/Product %s/Full"%(productID))
				imagePath = "/home/musaddiq/Desktop/Parts/5. Products/Images/Product %s/Full/Product %s Full Image 1"%(productID,productID)
				retryDownload = 0
				fullImagePaths = []
				imagePaths = "./Images/Product %s/Full/Product %s Full Image 1"%(productID,productID)
				while retryDownload < 20:
					time.sleep(randint(1,5))
					try:
						urllib.request.urlretrieve(image_url_single, imagePath)
						print("\nDownloaded Full Image 1")
						fullImagePaths.append(imagePaths)
						break
					except urllib.error.URLError:
						retryDownload += 1
						continue
					except urllib.error.HTTPError:
						retryDownload += 1
						break
					except Exception as e:
						retryDownload += 1
						print(e)
						continue
						
				'''
				if not os.path.exists("/home/musaddiq/Desktop/Parts/5. Products/Images/Product %s/Square"%(productID)):
					os.makedirs("/home/musaddiq/Desktop/Parts/5. Products/Images/Product %s/Square"%(productID))
				imagePath = "/home/musaddiq/Desktop/Parts/5. Products/Images/Product %s/Square/Product %s Square Image 1"%(productID,productID)
				retryDownload = 0
				while retryDownload < 20:
					time.sleep(randint(1,5))
					try:
						urllib.request.urlretrieve(image_url_single, imagePath)
						print("Downloaded 1 Square Image")
						break
					except urllib.error.URLError:
						retryDownload += 1
						continue
					except urllib.error.HTTPError:
						retryDownload += 1
						break
					except Exception as e:
						retryDownload += 1
						print(e)
						continue

				imagePaths = "./Images/Product %s/Square/Product %s Square Image 1"%(productID,productID)
				squareImagePaths = []
				squareImagePaths.append(imagePaths)
				'''
			except Exception as e:
				print(e)
				pass
			pass
		
		#--------------------------------------------------------------------------------------------------------------
		
		time.sleep(randint(5,7))

		#get product pricing
		if not onlyneedimages:

			pricingsoup = BeautifulSoup(contentCopy,features="html.parser")

			print("\nGetting Pricing")
			time.sleep(randint(1,4))

			try:
				pricingLocator = pricingsoup.find('div', attrs={'id':'skuTitle'}).next_sibling
				pricingLocator = pricingLocator.children
				pricingList = []
				for _ in pricingLocator:
					dummy = _
				for childs in dummy:
					pricingList.append(childs.get_text())
			except Exception as e:
				print(e)
				pass
			
			print(f"\nPricing list = {pricingList}")
			
			if "You Save" in pricingList[1]:
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
						pricingUSD = 0

				print(f"\nPricingUSD = {pricingUSD}")
				
				pricingSAR = float(pricingUSD)*3.75
				
				print(f"\nPricingSAR = {pricingSAR}")

				listPriceUSD = pricingList[1]
				groups = listPriceUSD.split(':')
				listPriceUSD = groups[len(groups)-1]
				#listPriceUSD = re.sub("[^\d\.]", "", listPriceUSD)
				if "," in listPriceUSD:
					listPriceUSD = listPriceUSD.replace(",","")
				try:
					listPriceUSD = float(listPriceUSD[2:])
				except ValueError:
					listPriceUSD = 0
					
				listPriceSAR = float(listPriceUSD)*3.75

				try:
					manfNum = pricingList[3]
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
						pricingUSD = 0

				pricingSAR = float(pricingUSD)*3.75

				listPriceUSD = pricingUSD
				listPriceSAR = pricingSAR

				try:
					manfNum = pricingList[2]
					manfNum = manfNum[manfNum.index("#")+1:]
				except ValueError:
					manfNum = "Not Available"
			
			#--------------------------------------------------------------------------------------------------------------
			
			#Getting Information
			print("\nGetting Information")
			infoelement = driver.find_element_by_id("productInfo")
			actions = ActionChains(driver)
			actions.move_to_element(infoelement).perform()
			time.sleep(randint(5,10))

			#content = driver.page_source
			#soup = BeautifulSoup(content,features="html.parser")

			#with open("/home/musaddiq/Desktop/Parts/5. Products/infoSoup.txt", 'w') as info:
				#info.write(soup.get_text())
				#info.close()

			information = soup.find('div', attrs={'id':'productInfo'})
			attributes_to_del = ["style", "class", "id", "target"]
			for attr_del in attributes_to_del:
					for p in information.find_all():
						if attr_del in p.attrs:
							del p.attrs[attr_del]
			productInfo = ""
			for child in information.children:
				productInfo = (str(child))
			
			#--------------------------------------------------------------------------------------------------------------
			
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
						}
					}
				}

			print(json.dumps(newProduct, indent = 2))	
			
			#--------------------------------------------------------------------------------------------------------------

			writing = json.dumps(newProduct, indent = 2)

			with open(productsFileName, 'w') as file:
				file.write(writing)
				file.close()
				print("\nSaved %s JSON to hard disk! :)" %productsFileName)

		with open("/home/musaddiq/Desktop/Parts/5. Products/doneURLs.txt", 'a') as urlfile:
			print("Added to done URLs list!")
			urlfile.write(productURL+"\n")
			urlfile.close()

		if 'driver' in locals():
			driver.quit()

	except Exception as e:
		print(e)
		os.system('python3 close.py')


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



