from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from time import sleep
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import pyperclip


MY_ACCOUNT = "0xd810BCBE78D64e9AE343C49F3F04f49176fD870D"


class WebDriverException(Exception):
    """
    Base webdriver exception.
    """

    def __init__(self, msg=None, screen=None, stacktrace=None):
        self.msg = msg
        self.screen = screen
        self.stacktrace = stacktrace

    def __str__(self):
        exception_msg = "Message: %s\n" % self.msg
        if self.screen is not None:
            exception_msg += "Screenshot: available via screen\n"
        if self.stacktrace is not None:
            stacktrace = "\n".join(self.stacktrace)
            exception_msg += "Stacktrace:\n%s" % stacktrace
        return exception_msg


class WaitConnection():
    def __call__(self, driver: webdriver):
        default_window = driver.current_window_handle
        windows = driver.window_handles
        for window in windows:
            driver.switch_to.window(window)
            if driver.title == 'MetaMask Notification':
                driver.switch_to.window(default_window)
                return True
        driver.switch_to.window(default_window)
        raise WebDriverException("no metamask")


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


def handle_metamask(driver: webdriver):
    default_window = driver.current_window_handle
    windows = driver.window_handles
    print("the window number is " + str(len(windows)))
    for window in windows:
        driver.switch_to.window(window)
        print("we now switch to window " + driver.title)
        if driver.title == "MetaMask Notification":
            print("we are dealing with metamask")
            try:
                button = driver.find_element_by_xpath('//button[contains(text(), "签名")]')
                button.click()
                print("finished signature")
            except(BaseException):
                print("not signature")
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


def get_href_from_webelement(links):
    hrefs = []
    for link in links:
        hrefs.append(link.get_attribute('href') + '\n')

    return hrefs


def has_mtmsk_notification(driver: webdriver):
    print("checking whether metamask notification appeared")
    windows = driver.window_handles
    default_window = driver.current_window_handle
    flag = False

    for window in windows:
        driver.switch_to.window(window)
        if driver.title == "MetaMask Notification":
            flag = True
            break

    driver.switch_to.window(default_window)
    return flag


def get_root_web(url: str):
    http_index = 8 if url.startswith("https") else 7
    http_head = url[0:http_index]
    url = url[http_index:]
    return http_head + url[0: url.find('/')]


def link_clean(hrefs: [str], prefix: str):
    result = []
    for href in hrefs:
        if href.startswith(prefix):
            if href.find(".css") == -1 and href.find(".ico") == -1 and href.find(".js") == -1 \
                    and href.find(".pdf") == -1 and href.find("http") != -1:
                result.append(href)

    return result


def opening_script(href: str):
    return 'window.open(\"' + href + '\");'


def login_metamask():
    option = webdriver.ChromeOptions()
    option.add_extension('/home/zhao/.config/google-chrome/Default/Extensions/nkbihfbeogaeaoehlefnkodbefgpgknn/7.1.1_0.crx')
    driver = webdriver.Chrome(chrome_options=option)
    sleep(4)
    driver = login(driver)
    sleep(4)
    return driver


def handle_single_page(driver: webdriver):
    # TODO: remember to delete the following two lines before real test
    driver = webdriver.Chrome()

    divs = driver.find_elements_by_xpath("//div")

    for i in range(len(divs)):
        G_beta.clear()
        G_pi.clear()
        G_gama.clear()
        G_epsilon.clear()
        # first if there is not text on this button it is unnecessary for us to click it
        # because it has no semantics
        try:
            text = buttons[i].text
            G_pi.add(text)
        except:
            print("this one doesn't have semantics")
            continue

        for input_box in inputs:
            try:
                if input_box.text or input_box.get_attribute('value'):
                    continue
            except:
                print("can't get value")

                # this is default text
            text = ""
            # here we get placeholder attribute of the input_box
            try:
                text = input_box.get_attribute('placeholder')
                text = get_desired_text(text)
            except:
                text = "1"

            # then put the value into input_box
            try:
                input_box.send_keys(text)
                sleep(4)
            except:
                print("can't input value moran")
        # we have filled all of the input box
        name = get_text_from_element(divs[i])
        print("we are dealing with div " + name)
        G_beta = G_beta.union(get_context_of_target(divs[i]))
        handle_widget(driver, divs[i], original_url)
        sleep(15)
        recover_state(driver, original_url)
        sleep(15)
        buttons = driver.find_elements_by_xpath("//button")
        inputs = driver.find_elements_by_xpath("//input")


def handle_modal_page(driver: webdriver):
    print("we are dealing with modal page")
    try:
        modal_div = driver.find_element_by_xpath('//div[@class="ReactModalPortal"]')
        print("the div number is " + str(len(modal_div)))
        print("the div class is " + str(modal_div.get_attribute('class')))
        try:
            buttons = modal_div.find_elements_by_xpath('.//button')
            print("the button number is " + str(len(buttons)))
            for button in buttons:
                try:
                    button.click()
                except:
                    print("this button can't be click")
                    return
        except:
            print("there is no button in the div")
            return
    except:
        print("can not find modal class, we will return")
        return


def visit_all_pages(driver: webdriver, original_link: str):
    print("opening the pages")
    driver.execute_script(opening_script(original_link))
    # sleep(20)
    #
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    print("waiting for the pages loading, about 4 minutes")
    # try:
    #     # TODO: you have to test whether the next line is valid
    #     # TODO: it cost quiet a few time even when the condition is satisfied
    #     WebDriverWait(driver, 30).until(WaitConnection())
    # except(BaseException):
    #     print("this page doesn't load completely, take care!")

    sleep(240)
    print("do some preparation")
    # preparation(driver)
    hrefs = []
    web_elements = driver.find_elements_by_xpath('//*[@href]')
    print("I am visiting all pages")
    for element in web_elements:
        hrefs.append(element.get_attribute("href"))
    # hrefs = link_clean(hrefs, get_root_web(original_link))
    print("the following is all of the pages I collected")
    for href in hrefs:
        print(href)

    # for href in hrefs:
    #     print("we are visiting " + href)
    #     get_sc_directly(driver, href)


def main():
    driver = login_metamask()
    print("opening the dapp")
    driver.execute_script(opening_script("https://www.zed.run/buy"))
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    print("waiting for page load")
    try:
        WebDriverWait(driver, 50).until(WaitConnection())
    except BaseException:
        print("I catch the exception")
    handle_metamask(driver)
    sleep(10)
    print("we finally get here")
    buy_selector = (By.XPATH, '//*[@id="app"]/div/div[2]/main/section[2]/div/div/div/div[2]/button[2]')
    start_selector = (By.XPATH, '//*[@id="app"]/div/header/div/div[2]/div/button')
    try:
        button = WebDriverWait(driver, 20).until(EC.presence_of_element_located(start_selector))
        button.click()
        sleep(10)
        button = driver.find_element_by_xpath('/html/body/div[2]/div/div/div/div[1]/form/section/button')
        button.click()
        # handle_modal_page(driver)
        sleep(10)
        handle_metamask(driver)
    except:
        print("can't click button start")
    sleep(20)
    purchase_button = driver.find_element_by_xpath('//*[@id="app"]/div/div[2]/main/section[2]/div/div/div/div[2]/div/div/div/div/div/div[2]/a/button')
    purchase_button.click()
    sleep(10)
    try:
        button = WebDriverWait(driver, 20).until(EC.presence_of_element_located(buy_selector))
        button.click()
        sleep(10)
        handle_modal_page(driver)
        sleep(10)
        handle_metamask(driver)
    except:
        print("can't click button buy")

    sleep(400)

if __name__ == '__main__':
    main()
