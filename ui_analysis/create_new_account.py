from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from time import sleep
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import pyperclip


def wait_and_click(xpath, driver):
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(
        (By.XPATH, xpath))
    )
    driver.find_element_by_xpath(xpath).click()


def login(driver):
    handles = driver.window_handles
    target_handle = ''
    for handle in handles:
        driver.switch_to.window(handle)
        if driver.title != 'MetaMask':
            driver.close()
        else:
            target_handle = handle
    if target_handle != '':
        driver.switch_to.window(target_handle)
    else:
        assert False, "FATAL: you shut down the most important web page"

    wait_and_click("//*[@id=\"app-content\"]/div/div[3]/div/div/div/button", driver)
    wait_and_click("//*[@id=\"app-content\"]/div/div[3]/div/div/div[2]/div/div[2]/div[2]/button", driver)
    wait_and_click("//*[@id=\"app-content\"]/div/div[3]/div/div/div/div[5]/div[1]/header/button[2]", driver)

    WebDriverWait(driver, 20).until(EC.presence_of_element_located(
        (By.XPATH, "//*[@id=\"create-password\"]"))
    )
    driver.find_element_by_xpath("//*[@id=\"create-password\"]").send_keys("iamsmtwtfs")


    WebDriverWait(driver, 20).until(EC.presence_of_element_located(
        (By.XPATH, "//*[@id=\"confirm-password\"]"))
    )
    driver.find_element_by_xpath("//*[@id=\"confirm-password\"]").send_keys("iamsmtwtfs")

    wait_and_click("//*[@id=\"app-content\"]/div/div[3]/div/div/div[2]/form/div[3]/div", driver)
    wait_and_click("//*[@id=\"app-content\"]/div/div[3]/div/div/div[2]/form/button", driver)
    wait_and_click("//*[@id=\"app-content\"]/div/div[3]/div/div/div[2]/div[2]/button[1]", driver)

    return driver


def login_metamask():
    option = webdriver.ChromeOptions()
    option.add_extension('/home/zhao/.config/google-chrome/Default/Extensions/nkbihfbeogaeaoehlefnkodbefgpgknn/7.1.1_0.crx')
    driver = webdriver.Chrome(chrome_options=option)
    sleep(4)
    driver = login(driver)
    sleep(4)
    return driver


def main():
    driver = webdriver.Chrome()
    driver.get("https://axieinfinity.com/axie/18083")
    sleep(30)
    # divs = driver.find_elements_by_xpath("//div[not(div)]")
    # print("length of divs " + str(len(divs)))
    # for div in divs:
    #     try:
    #         print(div.get_attribute("class") + div.get_attribute("id"))
    #         if div.get_attribute("class") == "" and div.get_attribute("id") == "":
    #             buttons = div.find_elements_by_xpath("./button")
    #             for button in buttons:
    #                 print(button.text)
    #     except:
    #         print("no class")
    #
    # divs = driver.find_elements_by_xpath("//div")
    # print("length of divs is " + str(len(divs)))
    # for div in divs:
    #     try:
    #         print(div.get_attribute("class") + div.get_attribute("id"))
    #     except:
    #         continue
    #
    # print("all finished")
    divs = driver.find_elements_by_xpath("//div[not(div)]")
    for div in divs:
        if div.is_enabled():
            print(div.get_attribute("class"))
    sleep(10000)

if __name__ == '__main__':
    main()
