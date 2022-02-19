from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from time import sleep
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import pyperclip
import math

MY_ACCOUNT = "0xd810BCBE78D64e9AE343C49F3F04f49176fD870D"


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


def login(driver):
    handles = driver.window_handles
    target_handle = driver.window_handles[0]

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


def connect_to_metamask(driver):
    print("beginning to get connect to metamask")
    windows = driver.window_handles
    if len(windows) == 1:
        print("no metamask connection happened")
        return

    for window in windows:
        driver.switch_to.window(window)
        print('connecting:' + driver.title)
        if driver.title == 'MetaMask Notification':
            print("switch to metamask")
            buttons = driver.find_elements_by_xpath('//button')
            for button in buttons:
                if button.text == 'Connect':
                    print("connect to metamask")
                    button.click()
                    break


def handling_metamask(driver: webdriver):
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


def cleaner(driver: webdriver):
    print("cleaner is working")
    print("dealing with metamask")
    handling_metamask(driver)
    print("finish dealing metamask")

    print("dealing with modal widget")
    modal_div = ""
    try:
        modal_div = driver.find_element_by_xpath('//div[contains(@class, "modal") or contains(@class, "Modal")]')
    except(BaseException):
        print("no modal div in this widget")
        buttons = modal_div.find_elements_by_xpath('.//button')
        for button in buttons:
            try:
                button.click()
            except(BaseException):
                print("this button cannot be clicked")
    print("cleaner finished")



def unlock_metamask(driver: webdriver):
    try:
        button = driver.find_element_by_xpath("//button[contains(text(), Unlock)]")
        button.click()
    except(BaseException):
        print("FATAL: in unlock_metamask, I can't find unlock button")


def get_sc(driver):
    print("*********************the beginning of get SC*********************")
    cleaner(driver)


def get_href_from_webelement(links):
    hrefs = []
    for link in links:
        hrefs.append(link.get_attribute('href') + '\n')

    return hrefs


def clean_modal(driver):
    print("************************** clean_modal ***************************")
    try:
        node = driver.find_element_by_xpath('//div[contains(@class,"modal") or contains(@class,"Modal")]')
    except(BaseException):
        print("no modal div, we exit here")
        return
    # maybe not a button
    try:
        buttons = node.find_elements_by_xpath('.//button')
    except(BaseException):
        print("in the modal div, there is no button")
        return

    if not buttons:
        return
    for button in buttons:
        try:
            button.click()
        except(BaseException):
            print("can't click the button in modal div, go on Moran")

    print("finished clean")


def preparation(driver):
    connect_to_metamask(driver)
    sleep(10)
    driver.switch_to.window(driver.window_handles[0])
    try:
        driver.switch_to.alert.accept()
        sleep(1)
    except(BaseException):
        print("No alert, please go on Moran")
    driver.switch_to.window(driver.window_handles[0])
    # print("refreshing...")
    # driver.refresh()
    sleep(5)
    clean_modal(driver)
    sleep(5)


def has_mtmsk_notification(driver: webdriver):
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


def get_sc_directly(driver, js):
    print("************************ get_sc_directly *************************")
    assert js, "FATAL: the web link is empty"
    assert driver, "FATAL: the driver is empty"

    # preparation(driver)
    # driver.execute_script(js)
    # # sleep(20)
    # #
    # driver.close()
    # driver.switch_to.window(driver.window_handles[0])
    # WebDriverWait(driver, 500).until(WaitConnection())
    #
    # # preparation
    # connect_to_metamask(driver)
    # sleep(10)
    # print(len(driver.window_handles))
    # driver.switch_to.window(driver.window_handles[0])
    # try:
    #     driver.switch_to.alert.accept()
    #     sleep(1)
    # except(BaseException):
    #     print("No alert, please go on Moran")
    # driver.switch_to.window(driver.window_handles[0])
    # print("refreshing...")
    # driver.refresh()
    # sleep(5)
    # clean_modal(driver)
    # sleep(5)
    #################################################
    driver.execute_script(opening_script(js))
    print("now driver should be pointed to " + js)
    # you have to insure that there are only two pages
    # default_window = driver.current_window_handle
    # for window in driver.window_handles:
    #     if window == default_window:
    #         driver.switch_to.window(window)
    sleep(5)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    # try:
    #     WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, "//button")))
    # except(BaseException):
    #     print("there are no buttons in this page")
    #     return
    inputs = driver.find_elements_by_xpath('//input')
    buttons = driver.find_elements_by_xpath("//button[not(@href)]")
    divs = driver.find_elements_by_xpath("//div[not(@href)]")

    print("button number is " + str(len(buttons)))

    for button in buttons:
        name = ""
        try:
            name = button.text
        except(BaseException):
            try:
                name = button.get_attribute("value")
            except(BaseException):
                print("no name")
        print(name)
    counter = 0
    js = driver.current_url
    # begin to click button
    for button in buttons:
        # fill the blanks
        counter += 1
        for input_box in inputs:
            if input_box.text or input_box.get_attribute('value'):
                continue
            try:
                input_box.send_keys('1')
            except(BaseException):
                print("can't input value moran")

        # print("beginning to click button " + button.text + " in the page")
        try:
            button.click()
            sleep(5)
            clean_modal(driver)
            sleep(5)
        except(BaseException):
            print("can't click button " + str(counter))
        clean_modal(driver)
        sleep(5)
        if has_mtmsk_notification(driver):
            get_sc(driver)
            sleep(5)
        driver.switch_to.window(driver.window_handles[0])
        while driver.current_url != js:
            driver.back()
            sleep(10)

    for i in range(len(buttons)):
        # here we init all of the word register
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

        # then we can go on to click the button
        # the following part is to fill the input box
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

        # then begin to click the button
        name = get_text_from_element(buttons[i])
        print("we are dealing with button " + name)
        G_beta = G_beta.union(get_context_of_target(buttons[i]))
        handle_widget(driver, buttons[i], original_url)
        sleep(15)
        recover_state(driver, original_url)
        sleep(15)
        buttons = driver.find_elements_by_xpath("//button")
        inputs = driver.find_elements_by_xpath("//input")
        # buttons.reverse()

    divs = driver.find_elements_by_xpath("//div[not(@href)]")
    counter = 1
    for div in divs:
        for
    # begin to click div
    # counter = 1
    # for div in divs:
    #     for input_box in inputs:
    #         if input_box.text or input_box.get_attribute('value'):
    #             continue
    #         try:
    #             input_box.send_keys('1')
    #         except(BaseException):
    #             print("can't input value moran")
    #
    #     print("beginning to click div " + str(counter) + " in the page")
    #     try:
    #         div.click()
    #         if driver.current_url != js:
    #             driver.back()
    #         else:
    #             clean_modal(driver)
    #             sleep(10)
    #     except(BaseException):
    #         print("can't click div " + str(counter))
    #     counter += 1
    #     if has_mtmsk_notification(driver):
    #         get_sc(driver)
    #         sleep(2)


def get_root_web(url: str):
    http_index = 8 if url.startswith("https") else 7
    http_head = url[0:http_index]
    url = url[http_index:]
    return http_head + url[0: url.find('/')]


def link_clean(hrefs: [str], prefix: str):
    result = []
    for href in hrefs:
        if href.startswith(prefix):
            if href.find(".css") == -1 and href.find(".ico") == -1 and href.find(".js") == -1 and href.find(".pdf") == -1:
                result.append(href)

    return result


def opening_script(href: str):
    return 'window.open(\"' + href + '\");'


def visit_all_pages(driver: webdriver, original_link: str):
    print("opening the pages")
    driver.execute_script(opening_script(original_link))
    # sleep(20)
    #
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    print("waiting for the pages")
    # try:
    #     # TODO: you have to test whether the next line is valid
    #     # TODO: it cost quiet a few time even when the condition is satisfied
    #     WebDriverWait(driver, 30).until(WaitConnection())
    # except(BaseException):
    #     print("this page doesn't load completely, take care!")

    sleep(300)
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


def get_text_from_element(element, target, threshold):

    text = ""
    try:
        text = element.text
    except:
        try:
            text = element.get_attribute("value")
        except:
            print("we have no idea moran")

    return text


def main():
    # here we login
    # desired_capabilities = DesiredCapabilities.CHROME
    # desired_capabilities["pageLoadStrategy"] = "none"
    option = webdriver.ChromeOptions()
    option.add_extension('/home/zhao/.config/google-chrome/Default/Extensions/nkbihfbeogaeaoehlefnkodbefgpgknn/7.1.1_0.crx')
    driver = webdriver.Chrome(chrome_options=option)
    # driver.implicitly_wait(20)
    sleep(4)
    driver = login(driver)
    sleep(4)
    driver.execute_script(opening_script("http://amaurymartiny.com/login-with-metamask-demo/"))
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    sleep(10)

    email = driver.find_element_by_xpath("//*[@id=\"root\"]/div/div/div/button[3]")

    parent = email.parent
    siblings = parent.find_elements_by_xpath(".//*")
    for element in siblings:
        print("*****************************")
        text = get_text_from_element(element, email, 10)
        if text != "":
            print(text)

    # visit_all_pages(driver, "https://opensea.io/category/cryptocars-2")

    sleep(100000)


    # get_SC_from_mizhen(driver)
    # javascripts = ['window.open("https://www.cryptoatoms.org/market")',
    #                'window.open("https://cryptofighters.io/market")',
    #                'window.open("https://cryptoserval.io/animal-market")',
    #                'window.open("https://opensea.io/")',
    #                'window.open("https://blockchaincuties.com/pets_sell")',
    #                'window.open("https://axieinfinity.com/marketplace")',
    #                'window.open("https://superrare.co/artwork-v2/assange\'d-4659")',
    #                'window.open("https://www.zed.run/release")',
    #                'window.open("https://exoplanets.io/marketplace/")'
    #                ]

    # driver.switch_to.window(driver.window_handles[0])
    # window = driver.window_handles[0]
    # buttons = driver.find_elements_by_xpath("//button")
    # for button in buttons:
    #     button.click()
    #

    # get all of the href
    # counter = 1
    # for js in javascripts:
    #     file_name = str(counter) + '.txt'
    #     file = open(file_name, mode='w')
    #     driver.execute_script(js)
    #     driver.close()
    #     sleep(60)
    #     driver.switch_to.window(driver.window_handles[0])
    #     connect_to_metamask(driver)
    #     sleep(60)
    #     links = driver.find_elements_by_xpath('//*[@href]')
    #     hrefs = get_href_from_webelement(links)
    #     file.write("".join(hrefs))
    #     counter += 1
    #     file.close()

# Metamask Notification
# button Connect

# TODO:divide the pages into two categories, one is the directly clicked
# TODO:the other is the indirectly clicked


if __name__ == '__main__':
    main()



# there are something wrong:
# 点击到最后一层时有可能会有控件导致网页跳转，这种情况将会导致后续的按钮不可点击
# 除此之外，get_sc无法处理请求metamask签名的情况，会导致程序异常退出
