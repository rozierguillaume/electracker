import os
from selenium import webdriver 
import os, base64

from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(ChromeDriverManager().install())

#os.environ["PATH"] = "$PATH:/chemin/vers/le/dossier/de/geckodriver"
#driver = webdriver.Chrome() 
driver.get("http://electracker.fr")

from PIL import Image


element = driver.find_element_by_id("myDiv")

location = element.location
size = element.size

driver.save_screenshot("shot.png")

x = location['x']
y = location['y']
w = size['width']
h = size['height']
width = x + w
height = y + h

im = Image.open('shot.png')
im = im.crop((int(x), int(y), int(width), int(height)))
im.save('image.png')