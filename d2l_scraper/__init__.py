from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

class D2LScraper:
    def __init__(self, course, download_dir):
        self.course = course
        self.download_dir = download_dir
        self.driver = self.webdriver_setup()
        self.wait = WebDriverWait(self.driver, 10)

    def webdriver_setup(self):
        chrome_options = webdriver.ChromeOptions()
        #chrome_options.add_argument("--headless")  
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Download Handler
        os.makedirs(self.download_dir, exist_ok=True)

        prefs={}
        prefs["profile.default_content_settings.popups"]=0
        prefs["download.default_directory"]=self.download_dir
        chrome_options.add_experimental_option("prefs", prefs)

        # Start WebDriver
        service = Service(ChromeDriverManager().install()) 
        return webdriver.Chrome(service=service, options = chrome_options) 

    def open_webpage(self, url):
        self.driver.get(url)

    def click_element_bycss(self, css_selector, timeout=10):
        wait = WebDriverWait(self.driver, timeout)
        element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        self.driver.execute_script("arguments[0].scrollIntoView();", element)
        element.click()

    def click_element_byclass(self, class_name, timeout=10):
        wait = WebDriverWait(self.driver, timeout)
        element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, class_name)))
        self.driver.execute_script("arguments[0].scrollIntoView();", element)
        element.click()

    def select_element_bycss(self, css_selector, timeout=10):
        wait = WebDriverWait(self.driver, timeout)
        return  wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))

    def select_element_byclass(self, class_name, timeout=10):
        wait = WebDriverWait(self.driver, timeout)
        return  wait.until(EC.visibility_of_element_located((By.CLASS_NAME, class_name)))
    
    def wait_for_element_byclass(self, class_name, timeout=10):
        wait = WebDriverWait(self.driver, timeout)
        wait.until(lambda d: self.driver.find_element(By.CLASS_NAME, class_name).is_displayed())

    def wait_for_element_bycss(self, css_selector, timeout=10):
        wait = WebDriverWait(self.driver, timeout)
        wait.until(lambda d: self.driver.find_element(By.CSS_SELECTOR, css_selector).is_displayed())

    def login(self, email, password):
        self.open_webpage("https://elearn.etsu.edu/d2l/lp/auth/saml/initiate-login?entityId=https%3A%2F%2Fsts.windows.net%2F962441d5-5055-4349-bad3-baec43c3d741%2F&target=%2fd2l%2fhome")
        # Email
        email_input = self.select_element_bycss(f"input[type='email']")
        email_input.send_keys(email)
        email_input.send_keys(Keys.RETURN)

        # Password
        pass_input = self.select_element_bycss(f"input[type='password']")
        pass_input.send_keys(password)
        pass_input.send_keys(Keys.RETURN)
        
        # Wait for 2FA, if necessary
        self.wait_for_element_byclass("d2l-body-main-wrapper", 20)
            
    def quit(self):
        self.driver.quit()

class SubmissionScraper(D2LScraper):
    def __init__(self, course, assignment_name, download_dir):
        super().__init__(course, download_dir)
        self.assignment_name = assignment_name

    def get_submissions(self):
        time.sleep(2)

        # Open course dropbox
        self.open_webpage(f'https://elearn.etsu.edu/d2l/lms/dropbox/admin/folders_manage.d2l?ou={self.course}')

        # Open submissions for assignment
        self.click_element_bycss(f"a[title='View {self.assignment_name} submissions']")

        # Check the box for all submissions
        self.click_element_bycss(f"input[aria-label='Select all rows']")

        # First download button
        self.click_element_bycss(f"d2l-button-subtle[icon='tier1:download']")

        self.click_element_bycss( f"button[primary]", 300)
        
        # Wait for download to finish
        time.sleep(5)

    def get_feedback_file(self):
        time.sleep(2)

        # Open course dropbox
        self.open_webpage(f'https://elearn.etsu.edu/d2l/lms/dropbox/admin/folders_manage.d2l?ou={self.course}')

        # Open submissions for assignment
        self.click_element_bycss(f"a[title='View {self.assignment_name} submissions']")

        # Click on the first student submission
        self.click_element_bycss(f"a[title*='Go to Evaluation for']")

        # TODO
        # Download feedback attachment
        # Click the next button until we get all students

        time.sleep(200)

class ClasslistScraper(D2LScraper):
    def __init__(self, course, download_dir):
        D2LScraper.__init__(self, course, download_dir)

    def get_classlist(self):
        # Go to grades page
        self.open_webpage(f"https://elearn.etsu.edu/d2l/lms/grades/admin/importexport/export/options_edit.d2l?ou={self.course}")

        # Click radio button for both key fields
        self.click_element_bycss(f"input[type='radio'][value='3']")

        # Uncheck grade values
        self.click_element_bycss(f"input[name='PointsGrade']")

        # Check 'Last Name', 'First Name', 'Email'
        names = ['LastName', 'FirstName', 'Email']

        for name in names:
            self.click_element_bycss(f"input[name='{name}']")

        # Check the box for all grades twice to deselect all
        self.click_element_bycss(f"input[aria-label='Select all rows']")
        self.click_element_bycss(f"input[aria-label='Select all rows']")
        
        # Export to CSV
        self.click_element_bycss(f"button[id='z_a']")
        
        # Second download button
        self.click_element_bycss(f"button[primary]", 60)
        
        # Wait for download to finish
        time.sleep(15)

class QuizScraper(D2LScraper):
    def __init__(self, course, quiz_name, download_dir):
        D2LScraper.__init__(self, course, download_dir)
        self.quiz_name = quiz_name

    def get_quiz(self):
        time.sleep(2)

class GradesScraper(D2LScraper):
    def __init__(self, course, download_dir):
        D2LScraper.__init__(self, course, download_dir)

    def get_grades(self):
        # Go to grades page
        self.open_webpage(f"https://elearn.etsu.edu/d2l/lms/grades/admin/importexport/export/options_edit.d2l?ou={self.course}")

        # Click radio button for both key fields
        self.click_element_bycss(f"input[type='radio'][value='3']")

        # Check the box for all grades 
        self.click_element_bycss(f"input[aria-label='Select all rows']")
       
        # Export to CSV
        self.click_element_bycss(f"button[id='z_a']")

        # Second download button
        self.click_element_bycss(f"button[primary]", 60)
        
        # Wait for download to finish
        time.sleep(15)
