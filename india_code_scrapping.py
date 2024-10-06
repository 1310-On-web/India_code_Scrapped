from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
import csv
import time
import os
import pandas as pd
import glob

# Get the absolute path of the download folder
current_directory = os.path.dirname(os.path.abspath(__file__))
download_dir = os.path.join(current_directory, "India_code_Downloads")

# If the download directory doesn't exist, create it
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

chrome_options = Options()
chrome_options.add_experimental_option('prefs', {
    "download.default_directory": download_dir,  # Set default download folder
    "download.prompt_for_download": False,  # Do not prompt for download
    "download.directory_upgrade": True,  # Automatically update to this directory
    "safebrowsing.enabled": True,  # Disable security prompts
    "plugins.always_open_pdf_externally": True  # Ensure PDFs are downloaded directly
})


# Path to your ChromeDriver
driver = webdriver.Chrome(options=chrome_options)

# Open IndiaCode website
driver.get('https://www.indiacode.nic.in/')
time.sleep(1)

nav_bar = driver.find_elements(By.XPATH, '//ul[@class="nav-menu"]/li')
# get the Browse centeral elememnts
browose_central_acts = driver.find_element(By.XPATH,'/html/body/header/div[4]/div/nav/ul[1]/li[4]')
browose_central_acts.click()
time.sleep(3)

data = []
try:
    ul_element = driver.find_element(By.XPATH, '/html/body/header/div[4]/div/nav/ul[1]/li[4]/ul')

    # Find all LI elements within the UL
    li_elements = ul_element.find_elements(By.TAG_NAME, 'li')

    # Iterate over each LI element
    for li in li_elements[1:2]:
        # Find the link (anchor tag) inside each LI element
        link = li.find_element(By.TAG_NAME, 'a')
        link.click()
        time.sleep(3)

        # Locate the select element using its full XPath
        select_element = driver.find_element(By.XPATH, '/html/body/main/div/div/div/div/div[1]/div/div[2]/form/select[2]')

        # Create a Select object for the dropdown
        select = Select(select_element)

        # Select the last option from the dropdown
        options = select.options
        select.select_by_index(len(options) - 1)  # Select the last option

        # Wait a moment to ensure the selection is registered (optional)
        time.sleep(1)

        # Locate and click on the 'Update' button using its XPath
        update_button = driver.find_element(By.XPATH, '/html/body/main/div/div/div/div/div[1]/div/div[2]/form/input[5]')
        update_button.click()

        # Additional wait to observe the action (optional)
        time.sleep(2)

        table_ul = driver.find_element(By.XPATH, '/html/body/main/div/div/div/div/div[3]/div[2]/ul')
        table_li_elements = table_ul.find_elements(By.TAG_NAME, 'li')
        
        for table_li_i in range(len(table_li_elements)):
            table_ul = driver.find_element(By.XPATH, '/html/body/main/div/div/div/div/div[3]/div[2]/ul')
            table_li_elements = table_ul.find_elements(By.TAG_NAME, 'li')
            driver.execute_script("arguments[0].scrollIntoView();", table_li_elements[table_li_i])
            link_table_li = table_li_elements[table_li_i].find_element(By.TAG_NAME, 'a')
            link_table_li.click()
            time.sleep(3)

            # now we are accessing the each file (row) in the page
            table = driver.find_element(By.XPATH, '/html/body/main/div/div/div[2]/div/table/tbody')

            # Get all rows in the table
            rows = table.find_elements(By.TAG_NAME, "tr")

            # Loop through each row in the table
            for i in range(len(rows)):
                # now we are accessing the each file (row) in the page
                table = driver.find_element(By.XPATH, '/html/body/main/div/div/div[2]/div/table/tbody')

                # Get all rows in the table
                rows = table.find_elements(By.TAG_NAME, "tr")

                driver.execute_script("arguments[0].scrollIntoView();", rows[i])
                # Get all cells (columns) in the current row
                cols = rows[i].find_elements(By.TAG_NAME, "td")
                
                # Click on the link in the last column
                if cols:
                    code_enactment_dt = cols[0].text
                    code_act_number = cols[1].text
                    code_name = cols[2].text
                    # Assuming that the last column contains a link (anchor tag)
                    last_column_link = cols[-1].find_element(By.TAG_NAME, "a")
                    code_url = last_column_link.get_attribute("href")
                    # print(code_enactment_dt,code_act_number,code_name,code_url)
                    
                    last_column_link.click()
                    # Optionally, you can add a small delay between clicks to avoid overwhelming the server
                    time.sleep(2)

                    # Act download button is clicked and file is downloaded.
                    code_download_button = driver.find_element(By.XPATH,'//*[@id="content"]/div[1]/div/div/div[1]/a')
                    code_download_button.click()
                    time.sleep(4)

                    # Get the list of all files in the directory, sorted by modification time (most recent first)
                    list_of_files = glob.glob(os.path.join(download_dir, '*')) 
                    latest_file = max(list_of_files, key=os.path.getctime)  # Get the latest file based on creation time
                    code_file_name = os.path.basename(latest_file)  # Extract just the file name from the path

                    # Append the row data to the list as a new row
                    data.append([code_enactment_dt, code_act_number, code_name, code_file_name, code_url])
                    
                    # Go back to the previous page
                    driver.back()
                    time.sleep(3)
            # Create a DataFrame from the list
            df = pd.DataFrame(data, columns=['Enactment Date', 'Act Number', 'Act Name','File Name', 'Download URL'])

            # Display or save the DataFrame
            print(df)
            driver.back()
            time.sleep(3)
            df.to_csv('final_data_India_Code.csv')

except Exception as e:
    print("An error occurred:", e)

driver.quit()
