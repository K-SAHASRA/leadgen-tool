import pandas as pd
import os

INPUT_FILE = os.path.join("..", "data", "enriched_leads_linkedin.csv")
OUTPUT_FILE = os.path.join("..", "data", "scored_leads.csv")

def score_lead(row):
    score = 0

    # Company size
    size = str(row.get("employee_size", "")).lower()
    if "11" in size or "51" in size or "200" in size:
        score += 20
    elif "1" in size and "10" in size:
        score += 10

    # Industry / Category
    industry = str(row.get("category", "")).lower()
    if any(keyword in industry for keyword in ["advertising", "marketing", "saas", "software"]):
        score += 30

    # Location
    location = str(row.get("location", "")).lower()
    if any(country in location for country in ["canada", "usa", "united states"]):
        score += 20

    # Website
    if pd.notna(row.get("website")) and "http" in str(row.get("website")):
        score += 10

    # LinkedIn
    if pd.notna(row.get("linkedin_url")) and "linkedin.com" in str(row.get("linkedin_url")):
        score += 10

    return score

def assign_tier(score):
    if score >= 75:
        return "Hot"
    elif score >= 50:
        return "Warm"
    else:
        return "Cold"

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Input file not found: {INPUT_FILE}")
        return

    df = pd.read_csv(INPUT_FILE)

    print("Scoring leads...")
    df["lead_score"] = df.apply(score_lead, axis=1)
    df["lead_tier"] = df["lead_score"].apply(assign_tier)

    output_columns = [
        "company_name", "website", "location", "rating", "no_reviews",
        "employee_size", "category", "source", "linkedin_url",
        "lead_score", "lead_tier"
    ]
    df.to_csv(OUTPUT_FILE, index=False, columns=output_columns)
    print(f"Scored leads saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
