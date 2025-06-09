import os
import time
import requests
import pandas as pd
from urllib.parse import urlparse

# SerpAPI Key
SERPAPI_API_KEY = "629a595b0e90ad59c10a64c4da1afe60420c595765945c2532b383ed411c1c23"

LIMIT = 10 

def extract_domain(url):
    try:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        return domain.replace("www.", "").split(".")[0] if domain else ""
    except:
        return ""

def search_linkedin_company_url(company_name, website):
    query_name = company_name.strip() if company_name else extract_domain(website)

    if not query_name:
        return None

    search_query = f"{query_name} site:linkedin.com/company"
    print(f"Searching: {search_query}")

    params = {
        "q": search_query,
        "api_key": SERPAPI_API_KEY,
        "engine": "google",
        "num": 3
    }

    try:
        response = requests.get("https://serpapi.com/search", params=params)
        results = response.json()

        for result in results.get("organic_results", []):
            link = result.get("link", "")
            title = result.get("title", "").lower()
            if "linkedin.com/company" in link and query_name.lower() in title:
                return link
    except Exception as e:
        print(f"Error searching for {company_name or website}: {e}")

    return None

def enrich_leads_with_linkedin(input_filename="combined_leads.csv", output_filename="enriched_leads_linkedin.csv"):
    # Resolve file paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "..", "data")
    os.makedirs(data_dir, exist_ok=True)

    input_path = os.path.join(data_dir, input_filename)
    output_path = os.path.join(data_dir, output_filename)

    if not os.path.exists(input_path):
        print(f"Input file not found: {input_path}")
        return

    df = pd.read_csv(input_path)
    df = df.head(LIMIT)

    enriched_rows = []

    print("Starting LinkedIn enrichment...")

    for idx, row in df.iterrows():
        company_name = str(row.get("company_name", "")).strip()
        website = str(row.get("website", "")).strip()

        if not company_name and not website:
            print(f"Skipping row {idx} (no company name or website)")
            continue

        print(f"Processing [{idx + 1}/{LIMIT}]: {company_name or extract_domain(website)}")

        linkedin_url = search_linkedin_company_url(company_name, website)

        print(f"LinkedIn URL: {linkedin_url if linkedin_url else 'Not found'}")

        row["linkedin_url"] = linkedin_url or ""
        enriched_rows.append(row)

        time.sleep(2)  # Respect API rate limit

    enriched_df = pd.DataFrame(enriched_rows)
    enriched_df.to_csv(output_path, index=False)

    print(f"Enriched data saved to {output_path}")

if __name__ == "__main__":
    enrich_leads_with_linkedin()
