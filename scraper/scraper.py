from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import pandas as pd
import os
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup as BS
from urllib.parse import urlparse, parse_qs
import random

# def find_linkedin(company_name):
#     query = f"site:linkedin.com/company {company_name} clutch"
#     url = f"https://www.bing.com/search?q={query}"
#     headers = {"User-Agent": "Mozilla/5.0"}

#     try:
#         response = requests.get(url, headers=headers, timeout=10)
#         time.sleep(random.uniform(2, 4))  # polite delay
#         soup = BS(response.text, "html.parser")
#         results = soup.select("li.b_algo h2 a")
#         for result in results:
#             href = result.get("href", "")
#             if "linkedin.com/company" in href and "/jobs" not in href and "/people" not in href:
#                 return href
#     except Exception as e:
#         print(f"Error searching LinkedIn for {company_name}: {e}")

#     return None



def scrape_with_selenium(pages=3):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)

    leads = []

    for page in range(1, pages + 1):
        url = f"https://clutch.co/agencies?page={page}"
        print(f"Loading {url} with Selenium")
        driver.get(url)
        time.sleep(5)  # waiting might inscrease not sure yet

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        listings = soup.select("div.provider")


        print(f"Loading {url} with Selenium")
        print(f"Found {len(listings)} listings on page {page}")

        for item in listings:
            name_tag = item.select_one("h3.provider__title a")
            name = name_tag.get_text(strip=True) if name_tag else None
            # insted of the profile on clutch it should fetch the actual website -done 
            # add another source other than cluthch
            # figure the linkdln part
            # what type of companys am i scraping??
            # in my search how can i select which type od companys to search ? like advert software etc etc.



            website_tag = item.select_one("a.website-link__item")
            website = None
            if website_tag and website_tag.has_attr('href'):
                raw_href = website_tag['href']
                parsed_url = urlparse(raw_href)
                website = parse_qs(parsed_url.query).get('u', [None])[0]


            location_tag = item.select_one(".provider__highlights-item.location")
            location = location_tag.get_text(strip=True) if location_tag else None

            rating_tag = item.select_one(".sg-rating__number")
            rating = rating_tag.get_text(strip=True) if rating_tag else None

            reviews_tag = item.select_one(".sg-rating__reviews")
            no_reviews = reviews_tag.get_text(strip=True) if reviews_tag else None

            employee_tag = item.select_one(".provider__highlights-item.employees-count")
            employee_size = employee_tag.get_text(strip=True) if employee_tag else None

            # linkedin_url = find_linkedin(name) if name else None
            # linkedin = find_linkedin(name)




            leads.append({
                "company_name": name,
                "website": website,
                "location": location,
                "rating": rating,
                "no_reviews": no_reviews,
                "employee_size": employee_size,
                # "linkedin": linkedin

            })


    driver.quit()
    return leads

if __name__ == "__main__":
    data = scrape_with_selenium(pages=3)
    df = pd.DataFrame(data)

    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    output_path = os.path.join(data_dir, "clutch_leads.csv")
    df.to_csv(output_path, index=False)

    print(f"Scraped {len(data)} leads. Saved to {output_path}")

