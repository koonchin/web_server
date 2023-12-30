from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

import pandas as pd
from selenium import webdriver
import time,pyautogui,os

def main(vrich_user,vrich_password,database):
    driver = webdriver.Chrome('chromedriver.exe')
    
    driver.get('https://muslinpajamas.vrich619.com')
    time.sleep(1)
    a = driver.find_element_by_xpath('/html/body/div/b/div/form/div[1]/input')
    a.send_keys(vrich_user)
    b = driver.find_element_by_name('password')
    b.send_keys(vrich_password)
    b.send_keys(Keys.RETURN)
    driver.implicitly_wait(20)
    try:
        time.sleep(2)
        driver.get('https://muslinpajamas.vrich619.com/order/confirmTransfer')
        w = WebDriverWait(driver, 20)
        w.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div[3]/section[1]/div/div/h1/span/div/a'))).click()
        driver.implicitly_wait(30)
    except:
        pass
    driver.get('https://muslinpajamas.vrich619.com/productStock/export')

    time.sleep(5)
    driver.quit()

main('super','Chino002','')