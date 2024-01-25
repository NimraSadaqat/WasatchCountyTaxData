from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager
import random
import time

parcel_ids = pd.read_csv('2022_wasatch_taxes (1).csv')['Parcel Number:'].tolist()[1:10]

def get_property_tax_details(parcel_id, driver):
    url = 'https://wasatch.utah.gov/Services/Information-Lookup-Services/Property-Tax-Information-Lookup/Current-Year-Property-Tax-Lookup?parc='+str(parcel_id)+'&ser=[%5E]&own=[%5E]&add=[%5E]' 
    driver.get(url)

    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        details_link = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Details")),
            EC.element_to_be_clickable((By.LINK_TEXT, "Details"))
        )
        details_link.click()

        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        return extract_table_data(table)

    except Exception as e:
        print(f"Error: {e}")
        return None

def extract_table_data(table):
    headers = [header.text for header in table.find_elements(By.TAG_NAME, "th")]
    rows = table.find_elements(By.TAG_NAME, "tr")

    data = []
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        data.append([cell.text for cell in cells])

    return pd.DataFrame(data, columns=headers) if headers else pd.DataFrame(data)

def process_and_format_data(df):
    df_transposed = df.iloc[:, :2].set_index(0).transpose()
    df_transposed.reset_index(drop=True, inplace=True)

    columns_indices = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 16, 17, 18, 19, 20, 23, 24, 25, 26]
    selected_columns = df_transposed.iloc[:, columns_indices]

    new_column_names = [
        'Tax Year', 'Parcel Number', 'Serial Number', 'Entry Number', 'Owner Name',
        'Owner Name 2', 'Mailing Address', 'Tax District', 'Tax District Rate', 'Recorders Office Acreage',
        'Tax Charge', 'Penalties Charged', 'Special Fees Charged', 'Tax Payments Received',
        'Taxes Abated', 'Balance Due', 'Escrow Processing Company', 'Property (Grid) Address',
        'Year Built', 'Brief Legal Taxing Description'
    ]

    selected_columns.columns = new_column_names
    return selected_columns

#importing proxy list
with open('Webshare_100_proxies.txt', 'r') as file:
    Proxies = file.readlines ()
Proxies = [x[:-23] for x in Proxies]

#Proxy credentials
proxy_username = 'qqdojcvg'
proxy_password = 'xghzyxuu4a6f'

service = Service(executable_path=ChromeDriverManager().install()) 

# other Chrome options
chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--ignore-certificate-errors-spki-list')
chrome_options.add_argument('--ignore-ssl-errors')
chrome_options.add_argument('--disable-proxy-certificate-handler')
chrome_options.add_argument('--allow-running-insecure-content')
chrome_options.add_argument("start-maximized")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# randomly extract a proxy
random_proxy = random.choice(Proxies)
print(random_proxy)

# Selenium Wire configuration to use a proxy
seleniumwire_options = {
    'proxy': {
        'http': f'http://{proxy_username}:{proxy_password}@{random_proxy}',
        'verify_ssl': False,
    },

}

driver = webdriver.Chrome(service=service, 
                        options=chrome_options,
                        seleniumwire_options=seleniumwire_options,
)


# Initialize an empty DataFrame for appending all results
all_data = pd.DataFrame()
counter = 1

# Loop through each parcel ID
for parcel_id in tqdm(parcel_ids):
    print(parcel_id)
    
    if counter%50 == 0:
        # randomly extract a proxy
        random_proxy = random.choice(Proxies)
        print(random_proxy)

        
        # Selenium Wire configuration to use a proxy
        seleniumwire_options = {
            'proxy': {
                'http': f'http://{proxy_username}:{proxy_password}@{random_proxy}',
                'verify_ssl': False,
            },

        }

        driver.close()
        driver.quit()

        driver = webdriver.Chrome(service=service, 
                                options=chrome_options,
                                seleniumwire_options=seleniumwire_options,
        )

    counter = counter+1    
    details = get_property_tax_details(parcel_id, driver)

    if details is not None:
        # Process and format data
        formatted_data = process_and_format_data(details)
        formatted_data.to_csv('2023_wasatch_taxes1.csv', mode='a', header=False, index=False)
        
driver.close()
driver.quit()
