#########################################################################
### Absent Status Resolver - Program to automate the resolution of ######
### absent statuses by coding absent/unexcused. To be run after    ######
### manual coding has been completed for other statuses.  Will not ######
### overwrite any codes that have been input.                      ######
#########################################################################

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os, time

load_dotenv()

def ProcessDate(date):

    driver = webdriver.Chrome()

    # Initial loading, including log in and navigating to attendance wizard
    _initial_load(driver)

    # get to the correct context...
    frame = driver.find_element(By.ID, 'main-workspace')
    driver.switch_to.frame(frame)
    workspaceframe = driver.find_element(By.ID, 'frameWorkspace')
    driver.switch_to.frame(workspaceframe)
    edit_button = driver.find_element(By.CSS_SELECTOR, "input#mode[value='edit']")
    edit_button.click()

    # set the date
    _set_date(driver, date)
    
    # set the filter for absent unverified
    _set_filter(driver)

    # get the first student in the list; return false if none are found
    next = _select_first_student_in_list(driver)

    while next:
        _process_current_row(driver)
        _refresh_search(driver)
        next = _select_first_student_in_list(driver)

    driver.close()

def _initial_load(driver):
    # log in and navigate to attendance entry wizard
    print('Infinite Campus login...')
    driver.maximize_window()
    #driver.minimize_window()
    driver.get(os.getenv('INFINITECAMPUSLOGINURL'))

    usernameinput = driver.find_element(By.ID, 'username')
    usernameinput.send_keys(os.getenv('INFINITECAMPUSUSERNAME'))
    passwordinput = driver.find_element(By.ID, 'password')
    passwordinput.send_keys(os.getenv('INFINITECAMPUSPASSWORD'))
    signinbutton = driver.find_element(By.ID, 'signinbtn')
    signinbutton.click()

    time.sleep(5)
    driver.get('https://trumbullct.infinitecampus.org/campus/sis/campus-tools/attendance-wizard')
    time.sleep(5)

    # select the correct calendar
    button = driver.find_element(By.XPATH, '//*[@aria-label="Context Switcher"]')
    driver.execute_script("arguments[0].click();", button)
    time.sleep(1)
    button = driver.find_element(By.XPATH, '//kendo-dropdownlist[@aria-labelledby="school-label"]//button[@aria-label="Select"]')
    driver.execute_script("arguments[0].click();", button)
    time.sleep(1)

    trumbull_high_option = driver.find_element(By.XPATH, '//li[span[text()="Trumbull High School"]]')
    trumbull_high_option.click()
    time.sleep(1)
    button = driver.find_element(By.CLASS_NAME, 'button--primary')
    button.click()

def _set_date(driver, date):
    date_element = driver.find_element(By.ID, 'currentDateField')
    date_element.click()
    date_element.send_keys(Keys.CONTROL, 'a')
    date_element.send_keys(date)

def _set_filter(driver):
    status_element = driver.find_element(By.ID, 'status')
    status = Select(status_element)
    status.select_by_visible_text('Absent')
    excuse_element = driver.find_element(By.ID, 'excuse')
    excuse = Select(excuse_element)
    excuse.select_by_visible_text('Unknown')
    driver.execute_script("searchStudents();")

def _refresh_search(driver):
    driver.execute_script("searchStudents();")

def _select_first_student_in_list(driver):
    listframe = driver.find_element(By.ID, 'searchResultsFrame')
    driver.switch_to.frame(listframe)
    try:
        # attempt to select first student; if it fails, then we must be done
        firstStudent = driver.find_element(By.XPATH, '/html/body/table/tbody/tr[1]/td/a')
        if firstStudent.text.strip() != "":
            firstStudent.click()
            next = True
        else:
            next = False
    except:
        next = False
    _switch_to_workspace_frame(driver)
    return next

def _process_current_row(driver):
    editframe = driver.find_element(By.ID, 'editModeFrame')
    driver.switch_to.frame(editframe)

    rows = driver.find_elements(By.XPATH, '//tbody/tr')
    # Loop through each row
    for row in rows:
        try:
            dirty_flag = row.find_elements(By.XPATH, './/input[@type="hidden" and starts-with(@id, "dirty")]')

            if dirty_flag:
                code_column = row.find_element(By.XPATH, './/td[2]/div/a/span')
                status_column = row.find_element(By.XPATH, ".//td[3]/div/a/span")
                
                # Check if Code is blank and Excuse is "Absent"
                if code_column.text.strip() == "" and status_column.text.strip().lower() == "absent":
                    auoption = row.find_element(By.XPATH, ".//td[2]/select/option[contains(text(), 'AU: Absent - Unexcused/Unverified')]")
                    auoption.click()

        except Exception as e:
            continue
    
    # Save the new values
    driver.execute_script("parent.saveThisAttendance();")
    
    # return to workspace frame
    _switch_to_workspace_frame(driver)

def _switch_to_workspace_frame(driver):
    driver.switch_to.default_content()
    frame = driver.find_element(By.ID, 'main-workspace')
    driver.switch_to.frame(frame)
    workspaceframe = driver.find_element(By.ID, 'frameWorkspace')
    driver.switch_to.frame(workspaceframe)