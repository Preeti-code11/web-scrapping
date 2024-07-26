import time
import csv
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor

class ProductDetailsTest(unittest.TestCase):
    def setUp(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--log-level=3')  # Suppress logging output

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)
        self.product_details_list = []

    def clean_html(self, html):
        """Remove extra spaces and newlines from HTML."""
        return ' '.join(html.split())

    def click_element(self, xpath, retries=3):
        """Click an element if it's clickable, with retry mechanism."""
        for attempt in range(1):
            try:
                element = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                element.click()
                return
            except Exception as e:
                print(f"Attempt {attempt+1} failed to click element with xpath {xpath}: {e}")
                time.sleep(2)
        try:
            element = self.driver.find_element(By.XPATH, xpath)
            self.driver.execute_script("arguments[0].click();", element)
            print(f"Clicked element with JavaScript for xpath {xpath}")
        except Exception as e:
            print(f"Failed to click element with JavaScript for xpath {xpath}: {e}")

    

    def extract_product_details(self, href):
        """Extract product details from a given product page."""
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get(href)
        driver.maximize_window()
        try:
            try:
                cookies_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.termly-styles-button-a4543c.t-acceptAllButton'))
                )
                if cookies_button.is_displayed():
                    cookies_button.click()
                    print("Cookies acceptance button clicked.")
            except:
                pass
            product_species_name = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@class="mercierProduct-species"]'))
            ).text
            product_name = driver.find_element(By.XPATH, '//*[@class="mercierProduct-name"]').text

            main_img_url = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@class="mercierProduct-mainImage js-mercierProduct-mainImage cbp-singlePage mercierProduct-mainImage-active"]//picture//img'))
            ).get_attribute('src')

            try:
                self.click_element('//*[@id="app-content"]/main/div/div[1]/div[3]/div[2]/a[1]')
                second_img_url = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@class="mercierProduct-mainImage js-mercierProduct-mainImage cbp-singlePage mercierProduct-mainImage-active"]//picture//img'))
                ).get_attribute('src')
            except Exception as e:
                print(f"Error while clicking image arrows: {e}")
                second_img_url = main_img_url  # fallback to main image if the second image fails

            driver.execute_script("window.scrollTo(0, 500)")

            # Initialize tab contents as "null"
            tab_elements = {
                'all_tabs_html': 'null',
                'active_tab_heading_html': 'null',
                'active_tab_html': 'null',
                'other_tab_heading_html': 'null',
                'other_tab_html': 'null',
                'solid_tab_heading_html': 'null',
                'solid_tab_html': 'null'
            }

            # Attempt to capture each element's HTML
            tab_paths = {
                'all_tabs_html': '//*[@class="mercierProducts-tabs"]',
                'active_tab_heading_html': '//*[@class="mercierProduct-tabToggler js-mercierProduct-tabToggler mercierProduct-tabToggler-active"]',
                'active_tab_html': '//*[@class="mercierProduct-tabContent mercierProduct-tabContent-active"]',
                'other_tab_heading_html': '//*[@class="mercierProduct-tabToggler js-mercierProduct-tabToggler "]',
                'solid_tab_heading_html': '//*[@class="mercierProduct-tabToggler js-mercierProduct-tabToggler "]'
            }

            for key, xpath in tab_paths.items():
                try:
                    tab_elements[key] = self.clean_html(WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    ).get_attribute('outerHTML'))
                except:
                    pass

            # Attempt to capture other tab content if possible
            try:
                self.click_element('//*[@id="app-content"]/main/div/div[2]/div/div[2]/div[1]/a[2]')
                tab_elements['other_tab_html'] = self.clean_html(WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@class="mercierProduct-tabContent mercierProduct-tabContent-active"]'))
                ).get_attribute('outerHTML'))
            except:
                pass

            try:
                self.click_element('//*[@id="app-content"]/main/div/div[2]/div/div[2]/div[1]/a[3]')
                tab_elements['solid_tab_html'] = self.clean_html(WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@class="mercierProduct-tabContent mercierProduct-tabContent-active"]'))
                ).get_attribute('outerHTML'))
            except:
                pass

            # Store product details in a dictionary
            product_details = {
                'product_species_name': product_species_name,
                'product_name': product_name,
                'main_img_url': main_img_url,
                'second_img_url': second_img_url,
                **tab_elements
            }

            # Append the dictionary to the list
            self.product_details_list.append(product_details)
            print(f"Successfully extracted product details for: {product_name}")

        except Exception as e:
            print(f"Error extracting product details: {e}")

        driver.quit()

    def test_product_details(self):
        """Test method to extract product details from the website."""
        driver = self.driver
        driver.get('https://mercier-wood-flooring.com/ca/en/hardwood-flooring/')

        # Accept cookies if the button is present
        try:
            cookies_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.termly-styles-button-a4543c.t-acceptAllButton'))
            )
            if cookies_button.is_displayed():
                cookies_button.click()
                print("Cookies acceptance button clicked.")
        except:
            pass

        containers = driver.find_elements(By.XPATH, '//*[@id="app-content"]/main/div/div[2]/div/div[2]/article')
        print(f"Found {len(containers)} products.")

        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=5) as executor:
            hrefs = [container.find_element(By.XPATH, './/*[@class="sample-detailsLink not_searchable"]').get_attribute('href') for container in containers]
            executor.map(self.extract_product_details, hrefs)

    def tearDown(self):
        """Tear down the test environment and save the product details to a CSV file."""
        self.driver.quit()

        # Write the product details to a CSV file
        csv_file = "product_details.csv"
        csv_columns = [
            'product_species_name', 'product_name', 'main_img_url', 'second_img_url', 'all_tabs_html',
            'active_tab_heading_html', 'active_tab_html', 'other_tab_heading_html', 'other_tab_html',
            'solid_tab_heading_html', 'solid_tab_html'
        ]

        try:
            with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                writer.writeheader()
                for data in self.product_details_list:
                    writer.writerow(data)
                print(f"Data successfully written to {csv_file}")
        except IOError as e:
            print(f"I/O error when writing to the CSV file: {e}")

if __name__ == "__main__":
    unittest.main()
