from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from time import sleep
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import pyperclip

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


def login_metamask():
    option = webdriver.ChromeOptions()
    option.add_extension('/home/zhao/.config/google-chrome/Default/Extensions/nkbihfbeogaeaoehlefnkodbefgpgknn/7.1.1_0.crx')
    driver = webdriver.Chrome(chrome_options=option)
    sleep(4)
    driver = login(driver)
    sleep(4)
    return driver


def handle_metamask(driver: webdriver):
    print("we are handling metamask")
    default_window = driver.current_window_handle
    windows = driver.window_handles

    for window in windows:
        driver.switch_to.window(window)
        if driver.title == "MetaMask Notification":
            try:
                button = driver.find_element_by_xpath('//button[contains(text(), "签名")]')
                button.click()
                print("finished signature")
            except(BaseException):
                print("not signature, try to connect to metamask")
                try:
                    button = driver.find_element_by_xpath('//button[contains(text(), "Connect")]')
                    button.click()
                    print("finished connection")
                except(BaseException):
                    print("not connection to MetaMask")
                    try:
                        print("getting data......")
                        reject_button = driver.find_element_by_xpath('//button[contains(text(), "拒绝")]')
                        data_button = driver.find_element_by_xpath('//li[contains(text(), "Data")]')
                        data_button.click()
                        account_button = driver.find_element_by_xpath('//div[@class="sender-to-recipient__name"][last()]')
                        account_button.click()
                        data_box = driver.find_element_by_xpath('//div[@class="confirm-page-container-content__data-box"][last()]')
                        print("the account is " + pyperclip.paste())
                        print("the abi is: " + str(data_box.text))
                        reject_button.click()
                    except(BaseException):
                        print("FATAL: unknown state")
            break

    driver.switch_to.window(default_window)
    print("Handling finished")


def compare_url(original: str, target: str):
    length = len(original)
    length -= 1
    while original[length] == '/':
        length -= 1

    original = original[0:length + 1]

    length = len(target)
    length -= 1
    while target[length] == '/':
        length -= 1

    target = target[0:length + 1]

    return original == target


def get_attribute(elem):
    return elem.get_attribute("href")


def remove_duplicate(hrefs):
    length = hrefs.__len__()
    precious = hrefs[0].get_attribute("href")
    result = []
    for i in range(1, int(length)):
        current = hrefs[i].get_attribute("href")
        if not compare_url(precious, current):
            result.append(hrefs[i])
            precious = current
    return result


def new_clean_link(hrefs):
    result = []
    hrefs.sort(key=get_attribute)
    hrefs = remove_duplicate(hrefs)
    for href in hrefs:
        try:
            link = href.get_attribute("href")
            if link.find(".css") == -1 and link.find(".ico") == -1 and link.find(".png") == -1 and link.find(
                    ".js") == -1 and link.find("http") != -1:
                result.append(href)
        except:
            continue
    for temp in result:
        print(temp.get_attribute("href"))
    return result


def opening_script(href: str):
    return 'window.open(\"' + href + '\");'


def get_differece_set(original: list, current: list):
    result = list(set(current) - set(original))
    return result


def main():
    driver = login_metamask()
    driver.execute_script(opening_script("https://www.zed.run/home"))
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    sleep(30)
    handle_metamask(driver)
    buttons = driver.find_elements_by_xpath("//button")
    print("Now we have " + str(buttons) + " windows")
    button = driver.find_element_by_xpath("//*[@id=\"app\"]/div/header/div/div[2]/div/button")
    button.click()
    sleep(3)
    buttons = get_differece_set(buttons, driver.find_elements_by_xpath("//button"))
    button = driver.find_element_by_xpath("/html/body/div[2]/div/div/div/div[1]/form/section/button")
    print("we have " + str(buttons) + " buttons.")
    print("but the button we want to obtain is " + str(button))
    sleep(120)
    button.click()
    for button in buttons:
        print("this button's text is " + button.text)
        if button.text == "CANCEL":
            continue
        button.click()
        print("clicked")
    handle_metamask(driver)
    sleep(2000)


if __name__ == '__main__':
    main()
