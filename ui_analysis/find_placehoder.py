from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from time import sleep
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import re


G_set = set()

def get_clean_text(text:str):
    float_pattern = "^\d+(\.\d+)?"
    address_pattern = "0x[0-9a-f]{40}|0x[0-9A-F]{40}$"
    email_pattern = "^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$"

    flag = False
    if not re.match(float_pattern, text):
        print("not float pattern")
    else:
        print("this is float")
        flag = True
    if not re.match(address_pattern, text):
        print("not address pattern")
    else:
        print("this is address")
        flag = True
    if not re.match(email_pattern, text):
        print("not email pattern")
    else:
        print("this is email")
        text = "Sun" + text
        flag = True

    if not flag:
        text = "as12oj2oi3oosdo2ojio"

    return text


def login(driver):
    handles = driver.window_handles
    target_handle = ''
    for handle in handles:
        driver.switch_to.window(handle)
        if driver.title != 'MetaMask':
            driver.close()
        else:
            target_handle = handle

    driver.switch_to.window(target_handle)

    # wait_element(driver, "//*[@id=\"app-content\"]/div/div[3]/div/div/div/button")

    # dealing first page
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(
        (By.XPATH, "//*[@id=\"app-content\"]/div/div[3]/div/div/div/button"))
    )
    driver.find_element_by_xpath("//*[@id=\"app-content\"]/div/div[3]/div/div/div/button").click()

    # dealing next page
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(
        (By.XPATH, "//*[@id=\"app-content\"]/div/div[3]/div/div/div[2]/div/div[2]/div[1]/button"))
    )
    driver.find_element_by_xpath("//*[@id=\"app-content\"]/div/div[3]/div/div/div[2]/div/div[2]/div[1]/button").click()

    # dealing next page
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(
        (By.XPATH, "//*[@id=\"app-content\"]/div/div[3]/div/div/div/div[5]/div[1]/header/button[2]"))
    )
    driver.find_element_by_xpath("//*[@id=\"app-content\"]/div/div[3]/div/div/div/div[5]/div[1]/header/button[2]").click()

    # dealing next page
    WebDriverWait(driver, 30).until(EC.presence_of_element_located(
        (By.XPATH, "//*[@id=\"app-content\"]/div/div[3]/div/div/form/button"))
    )
    input_box = driver.find_element_by_xpath("//*[@id=\"app-content\"]/div/div[3]/div/div/form/div[4]/textarea")
    input_box.send_keys("local album slight reopen muscle lottery that blanket poem gun unfair fork")
    pwd_box = driver.find_element_by_xpath("//*[@id=\"password\"]")
    pwd_box.send_keys("iamsmtwtfs")
    confirm_box = driver.find_element_by_xpath("//*[@id=\"confirm-password\"]")
    confirm_box.send_keys("iamsmtwtfs")
    check_box = driver.find_element_by_xpath("//*[@id=\"app-content\"]/div/div[3]/div/div/form/div[7]/div")
    check_box.click()
    submit = driver.find_element_by_xpath("//*[@id=\"app-content\"]/div/div[3]/div/div/form/button")
    submit.click()
    # driver.implicitly_wait(60)

    # dealing next page
    WebDriverWait(driver, 200).until(EC.presence_of_element_located(
        (By.XPATH, "//*[@id=\"app-content\"]/div/div[3]/div/div/button"))
    )
    submit = driver.find_element_by_xpath("//*[@id=\"app-content\"]/div/div[3]/div/div/button")
    submit.click()

    return driver


def opening_script(href:str):
    return 'window.open(\"' + href + '\");'


def login_metamask():
    option = webdriver.ChromeOptions()
    option.add_extension('/home/zhao/.config/google-chrome/Default/Extensions/nkbihfbeogaeaoehlefnkodbefgpgknn/7.1.1_0.crx')
    driver = webdriver.Chrome(chrome_options=option)
    sleep(4)
    driver = login(driver)
    sleep(4)
    return driver


def get_difference(original, current):
    return list(set(current) - set(original))

def test(widget):
    try:
        widget.click()
    except:
        print("can't click")


def get_split_string(target: str):
    array = target.split()
    return array[0]


def get_text_from_element(element):

    text = ""
    try:
        text = element.text
    except:
        try:
            text = element.get_attribute("value")
        except:
            print("we have no idea moran")
    if text != "":
        text = get_split_string(text)

    return text


def get_set():
    result = set()
    result.add("hello")
    result.add("world")
    return result


def main():
    driver = webdriver.Chrome()
    driver.get("https://blockchaincuties.com/pets_sell")
    hrefs = driver.find_elements_by_xpath("//*[@href]")
    frames = driver.find_elements_by_tag_name("iframe")

    for frame in frames:
        driver.switch_to.frame(frame)
        hrefs.extend(driver.find_elements_by_xpath("//*[@href]"))

    driver.switch_to.default_content()

    for href in hrefs:
        print("this is the " + href.get_attribute("href"))

    sleep(10000)



if __name__ == '__main__':
    main()
