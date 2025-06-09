from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import pandas as pd
import os
from urllib.parse import urlparse, parse_qs


# Define category URLs - so far only 3 categories

CATEGORY_URLS = {
    "advertising": "https://clutch.co/agencies?page=",
    "software": "https://clutch.co/developers?page=",
    "marketing": "https://clutch.co/agencies/digital-marketing?page="
}



# Scraper Function

def scrape_category(category_name, base_url, pages=1):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)

    leads = []

    for page in range(1, pages + 1):
        url = f"{base_url}{page}"
        print(f"\n loading: {url}")
        driver.get(url)
        time.sleep(5)  # wait for js maybe reduce have to look at it

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        listings = soup.select("div.provider")

        print(f" found {len(listings)} listings on page {page} in '{category_name}'")

        for item in listings:
            
            name_tag = item.select_one("h3.provider__title a")
            name = name_tag.get_text(strip=True) if name_tag else None

            # insted of the profile on clutch it should fetch the actual website -done 
            # add another source other than cluthch
            # figure the linkdln part
            # what type of companys am i scraping?? - done categorized them 
            # in my search how can i select which type od companys to search ? like advert software etc etc.- done


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

            
            leads.append({
                "company_name": name,
                "website": website,
                "location": location,
                "rating": rating,
                "no_reviews": no_reviews,
                "employee_size": employee_size,
                "category": category_name,  
                "source": "Clutch"
                # why not in blue think about it where the variable name is
            })

    driver.quit()
    return leads

# goodfirm logiv


GOODFIRMS_CATEGORY_URLS = {
    "software": "https://www.goodfirms.co/directory/languages/top-software-development-companies?page=",
    "digital-marketing": "https://www.goodfirms.co/directory/marketing-services/top-digital-marketing-companies?page=",
    "social-media-marketing": "https://www.goodfirms.co/directory/marketing-services/top-digital-marketing-companies/social-media-marketing?page="
}



def scrape_goodfirms(category_name, base_url, pages=1):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)

    leads = []

    for page in range(1, pages + 1):
        url = f"{base_url}{page}"
        print(f"Loading GoodFirms page: {url}")
        driver.get(url)
        time.sleep(5)  # wait for JS

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        headers = soup.select("div.firm-header-wrapper")
        infos = soup.select("div.firm-information-wrapper")

        print(f"Found {len(headers)} headers and {len(infos)} info blocks on page {page}")

        for header, company in zip(headers, infos):
            # Company Name & Website
            name_tag = header.select_one("h3.firm-name a.visit-website")
            name = name_tag.get_text(strip=True) if name_tag else None
            website = name_tag['href'] if name_tag and name_tag.has_attr('href') else None

            rating_tag = header.select_one("span.rating-number")
            rating = rating_tag.get_text(strip=True) if rating_tag else None

            reviews_tag = header.select_one("a.visit-profile")
            no_reviews = reviews_tag.get_text(strip=True) if reviews_tag else None

            services = company.select_one("div.firm-services")
            employee_tag = services.select_one("div.firm-employees span") if services else None
            employee_size = employee_tag.get_text(strip=True) if employee_tag else None

            location_tag = services.select_one("div.firm-location span") if services else None
            location = location_tag.get_text(strip=True) if location_tag else None

            if not name or not website:
                continue

            leads.append({
                "company_name": name,
                "website": website,
                "location": location,
                "rating": rating,
                "no_reviews": no_reviews,
                "employee_size": employee_size,
                "category": category_name,
                "source": "goodfirms"
            })

    driver.quit()
    return leads






# main block calling the scrapers and merging the csvs

if __name__ == "__main__":
    all_leads = []

    for category_name, base_url in CATEGORY_URLS.items():
        print(f"\n Scraping category: {category_name}")
        leads = scrape_category(category_name, base_url, pages=1)
        all_leads.extend(leads)

    df = pd.DataFrame(all_leads)

    # csv part make sure the directory is the root one and no the scraper one .
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    output_path = os.path.join(data_dir, "clutch_leads.csv")
    df.to_csv(output_path, index=False)

    print(f"\nDone. Scraped {len(all_leads)} total leads and saved to: {output_path}")
    

    # csv for good frame
    # Now scrape GoodFirms
    print("\nScraping GoodFirms...")
    goodfirms_all_leads = []
    for category_name, base_url in GOODFIRMS_CATEGORY_URLS.items():
        print(f"\nScraping GoodFirms category: {category_name}")
        goodfirms_leads = scrape_goodfirms(category_name, base_url, pages=1)
        goodfirms_all_leads.extend(goodfirms_leads)  # <-- use goodfirms_leads here
    
    print(f"Scraped {len(goodfirms_all_leads)} GoodFirms leads.")

    # Save GoodFirms leads in separate CSV under lead-gen/data/
    os.makedirs(data_dir, exist_ok=True)
    goodfirms_output_path = os.path.join(data_dir, "goodfirms_leads.csv")
    pd.DataFrame(goodfirms_all_leads).to_csv(goodfirms_output_path, index=False)

    print(f"Saved GoodFirms leads to: {goodfirms_output_path}")

        # Combine both CSVs into one
    clutch_df = pd.read_csv(output_path)
    goodfirms_df = pd.read_csv(goodfirms_output_path)

    combined_df = pd.concat([clutch_df, goodfirms_df], ignore_index=True)

    combined_output_path = os.path.join(data_dir, "combined_leads.csv")
    combined_df.to_csv(combined_output_path, index=False)

    print(f"Combined Clutch + GoodFirms leads saved to: {combined_output_path}")

    

