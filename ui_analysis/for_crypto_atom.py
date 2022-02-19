from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from time import sleep
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import pyperclip
import re
import math


G_alpha = set()
G_beta = set()
G_gama = set()
G_pi = set()
G_epsilon = set()

THREE_PARAMETER = 1
FOUR_PARAMETER = 2

CONNECT = 1
SIGNATURE = 2
GETDATA = 3
UNKNOWN = 4


def compare_url(original: str, target: str):
    if len(original) != len(target):
        return False
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


def opening_script(href: str):
    return 'window.open(\"' + href + '\");'


def back_to_target(driver: webdriver, target: str):
    windows = driver.window_handles
    default_window = ""
    print("this is the windows number " + str(len(windows)))
    if len(windows) == 1:
        print("we get in dealing single page procedure")
        while not compare_url(driver.current_url, target):
            print("the target url is " + target)
            print("the current url is " + driver.current_url)
            driver.back()
            print("we are back to the target")
            sleep(3)
    else:
        print("we get in dealing multiple pages procedure")
        for window in windows:
            driver.switch_to.window(window)
            if not compare_url(driver.current_url, target):
                driver.close()
            else:
                default_window = window
        driver.switch_to.window(default_window)


def get_link_every_frame(driver: webdriver):
    hrefs = driver.find_elements_by_xpath("//*[@href]")
    frames = driver.find_elements_by_tag_name("iframe")

    for frame in frames:
        try:
            driver.switch_to.frame(frame)
            hrefs.extend(driver.find_elements_by_xpath("//*[@href]"))
        except:
            print("In line 85, we can't switch to one frame")

    driver.switch_to.default_content()

    hrefs = new_clean_link(hrefs)
    #
    # for href in hrefs:
    #     try:
    #         print("this is the " + href.get_attribute("href"))
    #     except:
    #         continue

    return hrefs


def new_clean_link(hrefs):
    result = []
    hrefs.sort(key=get_attribute)

    # print("********************after the sort******************")
    # for href in hrefs:
    #     try:
    #         print("href is ", href.get_attribute("href"))
    #     except:
    #         print("none")

    hrefs = remove_duplicate(hrefs)
    for href in hrefs:
        try:
            link = href.get_attribute("href")
            if link.find(".css") == -1 and link.find(".ico") == -1 and link.find(".png") == -1 and link.find(
                    ".js") == -1 and link.find("javascript:") == -1:
                result.append(href)
        except:
            continue
    print("here is all of the href we can use")
    for href in result:
        print(href.get_attribute("href"))
    return result


def get_attribute(elem):
    href = ""
    try:
        href = elem.get_attribute("href")
        print("this is href ", href)
    except:
        # print("this one doesn't have href")
        # try:
        #     print(elem.text)
        # except:
        #     print("also doesn't have text")
        return href

    return href


def remove_duplicate(hrefs):
    length = hrefs.__len__()
    precious = ""
    start = 0
    print("**************************remove_duplicate******************")
    print("beginning: the length of hrefs is ", length)
    for i in range(0, int(length)):
        try:
            precious = hrefs[i].get_attribute("href")
            start = i
            break
        except:
            continue
    result = []
    for i in range(start, int(length)):
        try:
            current = hrefs[i].get_attribute("href")
            if not compare_url(precious, current):
                result.append(hrefs[i])
                precious = current
        except:
            continue

    print("ending: the length of hrefs is ", len(result))
    return result


def get_difference(original, current):
    return list(set(current) - set(original))


def handling_extra_button(original, driver):

    current = driver.find_elements_by_xpath('//button[not(contains(text(), "Cancel"))]')
    buttons = get_difference(original, current)
    inputs = driver.find_elements_by_xpath("//input")
    for input_box in inputs:
        try:
            if input_box.text or input_box.get_attribute('value'):
                continue
        except(BaseException):
            print("can't get value")

        # this is default text
        text = ""
        try:
            text = input_box.get_attribute('placeholder')
            text = get_desired_text(text)
        except:
            text = "1"

        # then put the value into input_box
        try:
            input_box.send_keys(text)
            sleep(4)
        except(BaseException):
            print("can't input value moran")

    for button in buttons:
        button.click()


def is_link_exist(driver: webdriver, url_set: set, original_website: str):
    flag = True
    original_window = driver.current_window_handle
    windows = driver.current_window_handle
    if len(windows) == 1:
        if driver.current_url not in url_set:
            url_set.add(driver.current_url)
            flag = False
    else:
        if len(windows) == 2:
            for window in windows:
                driver.switch_to.window(window)
                if compare_url(driver.current_url, original_website):
                    continue
                if driver.current_url not in url_set:
                    url_set.add(driver.current_url)
                    flag = False
        else:
            assert False, "Warning: there exists more than two windows"

    driver.switch_to.window(original_window)
    return flag


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


def handle_metamask(driver: webdriver):
    flag = False
    default_window = driver.current_window_handle
    windows = driver.window_handles
    ret_code = UNKNOWN

    for window in windows:
        driver.switch_to.window(window)
        if driver.title == "MetaMask Notification":
            flag = True
            try:
                button = driver.find_element_by_xpath('//button[contains(text(), "签名")]')
                button.click()
                print("finished signature")
                ret_code = SIGNATURE
            except(BaseException):
                print("not signature, try to connect to metamask")
                try:
                    button = driver.find_element_by_xpath('//button[contains(text(), "Connect")]')
                    button.click()
                    print("finished connection")
                    ret_code = CONNECT
                except(BaseException):
                    print("not connection to MetaMask")
                    try:
                        print("getting data......")
                        reject_button = driver.find_element_by_xpath('//button[contains(text(), "拒绝")]')
                        print("Successfully get reject_button")
                        data_button = driver.find_element_by_xpath('//li[contains(text(), "Data")]')
                        print("Successfully get data_button")
                        data_button.click()
                        print("Successfully click data_button")
                        # account_button = driver.find_element_by_xpath('//div[@class="sender-to-recipient__name"][2]')
                        account_button = driver.find_element_by_xpath('//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div[1]/div[2]/div/div')
                        print("Successfully get recipient name")
                        account_button.click()
                        print("Successfully click the recipient name")
                        account1 = pyperclip.paste()
                        account_button = driver.find_element_by_xpath('//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div[3]/div[2]/div/div')
                        print("Successfully get another user name")
                        account_button.click()
                        print("Successfully click the user name")
                        account2 = pyperclip.paste()
                        data_box = driver.find_element_by_xpath('//div[@class="confirm-page-container-content__data-box"][last()]')
                        print("get data_box successfully")
                        print("one account is " + account1)
                        print("another account is " + account2)
                        print("the abi is: " + str(data_box.text))
                        reject_button.click()
                    except(BaseException):
                        print("FATAL: unknown state")
                        try:
                            reject_button = driver.find_element_by_xpath('//button[contains(text(), "拒绝")]')
                            reject_button.click()
                        except:
                            print("we can't find reject button")
                    ret_code = GETDATA
            break
    if not flag:
        print("Attention: we did nothing in handling metamask")
    driver.switch_to.window(default_window)
    return ret_code


def get_differece_set(original: list, current: list):
    result = list(set(current) - set(original))
    return result


def compare_words_without_case(original: str, target: str):
    return original.upper() == target.upper()


def output_context(state: int):
    global G_beta
    global G_epsilon
    global G_gama
    global G_pi
    global G_alpha

    if state == THREE_PARAMETER:
        print("the alpha text is ", G_alpha)
        print("the beta text is ", G_beta)
        print("the pi text is ", G_pi)
    else:
        print("the alpha text is ", G_alpha)
        print("the pi text is ", G_pi)
        print("the gama text is ", G_gama)
        print("the epsilon text is ", G_epsilon)


def handle_widget(driver: webdriver, widget, original_url: str):
    global G_beta
    global G_epsilon
    global G_gama
    global G_pi
    global G_alpha

    original_window = driver.current_window_handle
    buttons = driver.find_elements_by_xpath("//button")
    flag = False
    ret_code = UNKNOWN

    try:
        print(widget)
        widget.click()
        print("I clicked the button")
    except:
        print("This widget can't be clicked")
        return

    sleep(120)
    buttons = get_differece_set(buttons, driver.find_elements_by_xpath("//button"))
    if not compare_url(original_url, driver.current_url):
        # Actually, there maybe still something wrong, for I didn't take the redirection into consideration
        print("this not the same page")
        return

    while has_mtmsk_notification(driver):
        flag = True
        ret_code = handle_metamask(driver)
        sleep(5)

    # we have handled the metamask, so return
    if flag:
        print("the ret_code is " + str(ret_code))
        if ret_code == CONNECT or ret_code == SIGNATURE:
            sleep(40)
            handle_widget(driver, widget, original_url)
        else:
            output_context(THREE_PARAMETER)
        return

    # prevent the driver's handle is changed in the handle_metamask procedure
    driver.switch_to.window(original_window)

    # if the widget can be click
    windows = driver.window_handles
    if len(windows) != 1:
        print("We have more than 1 window")
        return

    # new way to deal modal box
    button_name = ""
    for button in buttons:
        try:
            button_name = button.text
        except:
            continue
        try:
            if not compare_words_without_case(button_name, "CANCEL"):
                try:
                    button.click()
                except:
                    print("this button can't click")

                print("this will be deleted")
                sleep(5)
                if has_mtmsk_notification(driver):
                    print("we have metamask")
                else:
                    print("we don't have metamask")
                # # get all of the text
                G_epsilon.add(button_name)
                try:
                    G_gama = G_gama.union(get_context_of_target(button))
                except:
                    print("something wrong with line 426")
                while has_mtmsk_notification(driver):
                    print("I came here")
                    handle_metamask(driver)
                    sleep(3)
                output_context(FOUR_PARAMETER)
        except:
            print("this may not a button ")

    # now dealing with float window, maybe we can replace modal box handling with the function above
    # try:
    #     modal = driver.find_element_by_xpath("//div[contains(@class, 'modal') or contains(@class, 'Modal')]")
    #     try:
    #         buttons = modal.find_elements_by_xpath(".//button[not(contains(text(), 'Cancel'))]")
    #         for button in buttons:
    #             try:
    #                 button.click()
    #             except:
    #                 print("this button can't be clicked")
    #         # after click the button in modal, metamask can be called
    #         handle_metamask(driver)
    #         return
    #     except:
    #         print("There is no buttons in this modal")
    # except:
    #     print("We can't find widget modal")


def recover_state(driver: webdriver, original_url: str):
    '''
    :param driver:
    :param original_url:
    :type: remember the driver should be pointed to the original page
    :return:
    '''
    current_handle = driver.current_window_handle
    current_url = driver.current_url
    window_handles = driver.window_handles

    # this is to get rid of modal box
    driver.refresh()
    print("current_url is " + current_url)
    # the first step we back the page to the original one
    # by this way we can also close all of the modal box in the original window
    # first close all of the windows which doesn't belong to the original one
    for window in window_handles:
        driver.switch_to.window(window)
        if window != current_handle:
            driver.close()

    driver.switch_to.window(current_handle)

    # second back to the orignal page
    if not compare_url(current_url, original_url):
        back_to_target(driver, original_url)
    print("we finished here")


def get_text_from_element(element):
    text = ""
    try:
        text = element.text
    except:
        try:
            text = element.get_attribute("value")
        except:
            print("we have no idea moran")

    return text


def split_sentence_to_word(sentence: str):
    return set(sentence.split())


def is_near_to_target(element, target):
    element_x = element.location["x"]
    element_y = element.location["y"]
    target_x = target.location["x"]
    target_y = target.location["y"]
    distance = math.sqrt(math.pow((element_x - target_x), 2) + math.pow((element_y - target_y), 2))

    if distance > 100:
        return False
    return True


def get_context_of_target(target):
    # first we should get the sibling context
    target_context = set()

    context_elements = target.find_elements_by_xpath(".//following-sibling::*")
    for element in context_elements:
        target_context = target_context | set(get_text_from_element(element).split())

    context_elements = target.find_elements_by_xpath(".//preceding-sibling::*")
    for element in context_elements:
        target_context = target_context | set(get_text_from_element(element).split())

    # second we should get parent context
    context_elements = target.find_elements_by_xpath(".//parent::*")
    for element in context_elements:
        first_line = get_text_from_element(element).split("\n")[0]
        if len(first_line) != 0:
            target_context = target_context | set(first_line.split())
            break

        children = element.find_elements_by_xpath(".//*")
        for child in children:
            target_context = target_context | set(get_text_from_element(child).split())

        # now judge whether there are at least 3 words
        if len(target_context) > 3:
            break

    return target_context


def handle_single_link(driver: webdriver):
    global G_beta
    global G_epsilon
    global G_gama
    global G_pi
    global G_alpha

    original_url = driver.current_url
    print("original_url is " + original_url)
    if len(driver.window_handles) != 1:
        assert False, "Warning: Line 368, we have two page here, can't deal"
    inputs = driver.find_elements_by_xpath("//input")

    buttons = driver.find_elements_by_xpath("//button")
    print("the button number is " + str(len(buttons)))
    # now we begin to deal with all of these buttons
    print("the followings are the buttons text")
    file_name = "./test.txt"
    with open(file_name, "a+") as f:
        f.writelines(original_url + "\n")
        f.writelines("the followings are the buttons text\n")
        for temp in buttons:
            try:
                text = temp.text
                if text != " " and text != "\n" and text != "":
                    text = "[" + text + "]"
                    print(text, end=' ')
                    text += ","
                    f.write(text)

            except:
                continue
        f.write("\n")
        print("")
        if len(buttons) != 0:
            print("the followings are context")
            print(get_all_context_of_page(driver))
            f.write("the followings are context\n")
            f.write(str(get_all_context_of_page(driver)) + "\n")


    # for i in range(len(buttons)):
    #     # here we init all of the word register
    #     G_beta.clear()
    #     G_pi.clear()
    #     G_gama.clear()
    #     G_epsilon.clear()
    #     # first if there is not text on this button it is unnecessary for us to click it
    #     # because it has no semantics
    #     original_url = driver.current_url
    #     try:
    #         text = buttons[i].text
    #         print("we are dealing with ", text)
    #         G_pi.add(text)
    #     except:
    #         print("this one doesn't have semantics")
    #         continue
    #
    #     # then we can go on to click the button
    #     # the following part is to fill the input box
    #     for input_box in inputs:
    #         try:
    #             if input_box.text or input_box.get_attribute('value'):
    #                 continue
    #         except:
    #             print("can't get value")
    #
    #         # this is default text
    #         text = ""
    #         # here we get placeholder attribute of the input_box
    #         try:
    #             text = input_box.get_attribute('placeholder')
    #             text = get_desired_text(text)
    #         except:
    #             text = "1"
    #
    #         # then put the value into input_box
    #         try:
    #             input_box.send_keys(text)
    #             sleep(4)
    #         except:
    #             print("can't input value moran")
    #     # we have filled all of the input box
    #
    #     # then begin to click the button
    #     name = get_text_from_element(buttons[i])
    #     print("we are dealing with button " + name)
    #     G_beta = G_beta.union(get_context_of_target(buttons[i]))
    #     handle_widget(driver, buttons[i], original_url)
    #     sleep(15)
    #     recover_state(driver, original_url)
    #     sleep(15)
    #     buttons = driver.find_elements_by_xpath("//button")
    #     inputs = driver.find_elements_by_xpath("//input")
    # buttons.reverse()
    # the following is used to handle divs

    # divs = driver.find_elements_by_xpath("//div[not(div)]")
    # print("we have " + str(len(divs)) + " divs, they are")
    # for div in divs:
    #     print(div.text)
    # for i in range(len(divs)):
    #     G_beta.clear()
    #     G_pi.clear()
    #     G_gama.clear()
    #     G_epsilon.clear()
    #     # first if there is not text on this button it is unnecessary for us to click it
    #     # because it has no semantics
    #     try:
    #         text = divs[i].text
    #         G_pi.add(text)
    #     except:
    #         print("this one doesn't have semantics")
    #         continue
    #
    #     for input_box in inputs:
    #         try:
    #             if input_box.text or input_box.get_attribute('value'):
    #                 continue
    #         except:
    #             print("can't get value")
    #
    #             # this is default text
    #         text = ""
    #         # here we get placeholder attribute of the input_box
    #         try:
    #             text = input_box.get_attribute('placeholder')
    #             text = get_desired_text(text)
    #         except:
    #             text = "1"
    #
    #         # then put the value into input_box
    #         try:
    #             input_box.send_keys(text)
    #             sleep(4)
    #         except:
    #             print("can't input value moran")
    #     # we have filled all of the input box
    #     name = get_text_from_element(divs[i])
    #     print("we are dealing with div " + name)
    #     G_beta = G_beta.union(get_context_of_target(divs[i]))
    #     handle_widget(driver, divs[i], original_url)
    #     sleep(15)
    #     recover_state(driver, original_url)
    #     sleep(15)
    #     divs = driver.find_elements_by_xpath("//div")
    #     inputs = driver.find_elements_by_xpath("//input")


def handle_all_link(driver: webdriver):
    global G_beta
    global G_epsilon
    global G_gama
    global G_pi
    global G_alpha

    print("**********************handle all link*********************")
    original_website = driver.current_url
    print("the original web site is " + original_website)
    hrefs = get_link_every_frame(driver)
    hrefs = hrefs[3:]
    length = len(hrefs)

    for counter in range(length):
        # here we initial all of the word register
        G_alpha.clear()
        G_beta.clear()
        G_gama.clear()
        G_pi.clear()
        G_epsilon.clear()
        href = hrefs[counter]
        try:
            website = href.get_attribute("href")
            print("we are clicking " + website)
            text = "UNKNOWN"
            try:
                text = hrefs[counter].text.splite()
            except:
                print("Attention: we didn't get the link name")
            G_alpha.add(text)
            try:
                href.click()
                sleep(20)
                website = driver.current_url
                handle_single_link(driver)
                sleep(5)
                recover_state(driver, website)
            except:
                print("this link can't be click")
        except:
            print("we can't get the href from website widget")

        # one line below maybe not useful
        back_to_target(driver, original_website)
        # TODO: HERE SHOULD BE A LONG DELAY
        sleep(200)
        hrefs = get_link_every_frame(driver)
        hrefs = hrefs[3:]

    # atags = driver.find_elements_by_xpath("//a")
    # length = len(atags)
    # for counter in range(length):
    #     # here we init all of the word register
    #     G_alpha.clear()
    #     G_beta.clear()
    #     G_gama.clear()
    #     G_pi.clear()
    #     G_epsilon.clear()
    #     a = atags[counter]
    #
    #     try:
    #         website = a.get_attribute("href")
    #         print("we are clicking " + website)
    #         text = "UNKNOWN"
    #         try:
    #             text = a.text.splite()
    #         except:
    #             print("Attention: we didn't get the link name")
    #         G_alpha.add(text)
    #         try:
    #             a.click()
    #             sleep(5)
    #             handle_single_link(driver)
    #             sleep(5)
    #             recover_state(driver, website)
    #         except:
    #             print("this link can't be click")
    #     except:
    #         print("we can't get the href from website widget")
    #
    #     back_to_target(driver, original_website)
    #     sleep(2)
    #     atags = driver.find_elements_by_xpath("//a")


def wait_and_click(xpath, driver):
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(
        (By.XPATH, xpath))
    )
    driver.find_element_by_xpath(xpath).click()


def login(driver):
    handles = driver.window_handles
    target_handle = ''
    WebDriverWait(driver, 60).until(WaitWelcomePage(), "you need more time to wait welcome page")
    sleep(2)
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
    # chrome_prefs = {}
    # option.experimental_options["prefs"] = chrome_prefs
    # chrome_prefs["profile.default_content_settings"] = {"images": 2}
    # chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
    prefs = {
        'profile.default_content_setting_values': {
            'images': 2,
            # 'javascript': 2,
            'stylesheet': 2
        }
    }
    option.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(chrome_options=option)
    sleep(10)
    driver = login(driver)
    sleep(4)
    return driver


def open_chrome():
    options = webdriver.ChromeOptions()
    options.add_extension('/home/zhao/.config/google-chrome/Default/Extensions/nkbihfbeogaeaoehlefnkodbefgpgknn/7.1.1_0.crx')
    prefs = {
        'profile.default_content_setting_values': {
            'images': 2,
            # 'javascript': 2,
            'stylesheet': 2
        }
    }
    options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(chrome_options=options)
    sleep(10)
    driver = login(driver)
    sleep(3)
    return driver


def get_desired_text(text:str):
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


class WaitWelcomePage:
    def __call__(self, driver: webdriver):
        default_window = driver.current_window_handle
        windows = driver.window_handles
        for window in windows:
            driver.switch_to.window(window)
            if driver.title == 'MetaMask':
                driver.switch_to.window(default_window)
                return True
        driver.switch_to.window(default_window)


def get_all_context_of_page(driver: webdriver):

    widgets = driver.find_elements_by_xpath("/*")
    result = []
    for widget in widgets:
        try:
            text = widget.text
            result.append(str.split(text))
        except:
            print("here we can't get the text")

    return result


def handle_all_links(driver: webdriver):
    hrefs = get_link_every_frame(driver)
    print("this is the result of main page")
    print(get_all_context_of_page(driver))
    for href in hrefs:
        driver.execute_script(opening_script(get_attribute(href)))
        sleep(2)
        if len(driver.window_handles) == 1:
            print("this is the result of " + driver.title + " :")
            print(get_all_context_of_page(driver))
            driver.back()
        else:
            driver.switch_to.window(driver.window_handles[1])
            print("title of the web page we handle " + driver.title + " :")
            print(driver.title)
            print("this is the result of " + driver.title + " :")
            print(get_all_context_of_page(driver))
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        sleep(1)


def main():
    website = "https://www.cryptoatoms.org/market"
    driver = login_metamask()
    driver.execute_script(opening_script(website))
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    print("attention we will enter the first waiting")
    sleep(10)
    print("first waiting accomplished")
    # driver.maximize_window()
    handle_metamask(driver)
    print("after handle metamask")
    # try:
    #     driver.refresh()
    # except:
    #     print("refresh timeout, but you can go on")
    # driver.refresh() when dealing the note dapp master

    # print("you have 120 seconds to login")
    # sleep()
    # handle_single_link(driver)

    print("you have 120 seconds to login")
    sleep(250)
    handle_all_link(driver)
    print("we have finished in main")

    sleep(10000)

if __name__ == '__main__':
    main()

