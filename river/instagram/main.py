from selenium import webdriver
from time import sleep
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class InstaBot:


    def __init__(self, username, pw):
        self.username = username
        self.pw = pw

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--incognito")
        #options.add_argument('headless')
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        #self.driver = webdriver.Ie() # .Chrome()


        #self.driver.set_page_load_timeout(10)
        #self.driver.implicitly_wait(1)
        #self.driver.maximize_window()

        self.driver.get('https://instagram.com')
        sleep(2)

        self.driver.find_element_by_xpath("//input[@name=\"username\"]").send_keys(username)
        self.driver.find_element_by_xpath("//input[@name=\"password\"]").send_keys(pw)
        self.driver.find_element_by_xpath('//button[@type="submit"]').click()
        sleep(4)
        self.driver.find_element_by_xpath("//button[contains(text(), 'Not Now')]") .click()


    def get_unfollowers(self):
        self.driver.find_element_by_xpath("//a[contains(@href,'/{}')]".format(self.username)).click()
        sleep(2)
        self.driver.find_element_by_xpath("//a[contains(@href,'/following')]") \
            .click()
        following = self._get_names()
        self.driver.find_element_by_xpath("//a[contains(@href,'/followers')]") \
            .click()
        followers = self._get_names()
        not_following_back = [user for user in following if user not in followers]
        print(not_following_back)

    def _get_names(self):
        sleep(2)
        sugs = self.driver.find_element_by_xpath('//h4[contains(text(), Suggestions)]')
        self.driver.execute_script('arguments[0].scrollIntoView()', sugs)
        sleep(2)
        scroll_box = self.driver.find_element_by_xpath("/html/body/div[4]/div/div[2]")
        last_ht, ht = 0, 1
        while last_ht != ht:
            last_ht = ht
            sleep(1)
            ht = self.driver.execute_script("""
                arguments[0].scrollTo(0, arguments[0].scrollHeight); 
                return arguments[0].scrollHeight;
                """, scroll_box)
        links = scroll_box.find_elements_by_tag_name('a')
        names = [name.text for name in links if name.text != '']
        # close button
        self.driver.find_element_by_xpath("/html/body/div[4]/div/div[1]/div/div[2]/button") \
            .click()
        return names

    def get_to_follow(self):
        self.driver.find_element_by_xpath("//a[contains(@href,'/{}')]".format(self.username)).click()
        sleep(2)
        self.driver.find_element_by_xpath("//a[contains(@href,'/followers')]").click()
        sleep(2)

        self.driver.find_element_by_xpath("/html/body/div[4]/div/div[2]/div[3]/a").click()

        buttons = self.driver.find_elements_by_xpath('//button[text()="Follow"]')
        i = 0
        try:
            sleep(5)
            buttons = self.driver.find_elements_by_xpath('//button[text()="Follow"]')
            for button in buttons:
                button.click()
                i += 1
                print (i)
        except: print ('Error')

    def close(self):
        self.driver.close()


for i in range(10):
    my_bot = InstaBot('sgvolpe12020', 'tableta2')
    try:

        #my_bot.get_unfollowers()
        my_bot.get_to_follow()
    except :
        print ('Error')
        sleep(60)

    finally:my_bot.close()