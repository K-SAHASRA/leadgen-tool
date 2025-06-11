
# LeadGen AI

LeadGen AI is a streamlined web application designed to help users explore, enrich, score, and analyze sales leads with the help of AI. The app integrates LinkedIn enrichment, AI-powered company summaries, lead scoring, and AI-generated tags to provide actionable insights for lead generation and marketing teams.

## Features

### 1. Lead Exploration and Filtering

* Users can select a business category from predefined options.
* The app filters leads based on the selected category from a combined leads dataset.
* Filtered leads are displayed in a readable markdown table with clickable website links.
* Option to download the filtered leads as a CSV file.

### 2. LinkedIn Data Enrichment

* Users can enrich filtered leads with LinkedIn data to get additional details like company profiles and LinkedIn URLs.
* The enriched leads are displayed in a table with clickable website and LinkedIn links.
* Enriched data can be downloaded as a CSV for further use.

### 3. Lead Scoring and Tiering

* Leads enriched with LinkedIn data can be scored based on various criteria defined in the scoring module.
* Scores are translated into lead tiers to categorize lead quality.
* Users can view scored leads with company name, rating, lead score, and tier.
* Download option for the scored leads summary CSV.

### 4. AI-Generated Company Summaries

* Generate concise, professional summaries of companies based on their name, website, and category using AI (OpenAI / Groq LLaMA models).
* Summaries are displayed in a scrollable data table for easy reading.
* Option to download all company summaries as a CSV.

### 5. AI Tag Generation

* Using the AI-generated company summaries, the app can create relevant descriptive tags for each company.
* Tags are generated in a clean JSON list format.
* Tags help users quickly identify key business focuses or specialties.
* Tags can be downloaded in CSV format.

### User Interface

* The app uses Streamlit for a simple, interactive web interface.
* Buttons toggle between views: filtered leads, enriched leads, scored leads, company summaries, and AI-generated tags.
* Data tables are formatted for readability with clickable links and download buttons.
* Horizontal scrolling is supported where needed for wide tables.

---

## Getting Started

1. **Data Setup**
   Place your combined leads CSV file in the `data` folder, named `combined_leads.csv`. Ensure it contains at least the following columns:

   * `company_name`
   * `website`
   * `category` (used for filtering)

2. **API Keys**
   Make sure to provide your OpenAI API key and set the correct base URL in the relevant Python modules for AI summarization and tag generation.

3. **Running the App**
   From the frontend folder, run:

   ```bash
   streamlit run app.py
   ```

4. **Workflow**

   * Select a category and click **Search Leads**.
   * Enrich leads with LinkedIn data by clicking **Enrich Leads with LinkedIn**.
   * Score leads or generate company summaries and AI tags using the respective buttons.
   * Download any generated CSV files as needed.

---

## Project Folder Structure

```
lead-gen/
├── data/
│   ├── combined_leads.csv                 # Input dataset of combined leads
│   ├── enriched_leads_linkedin.csv        # Output file after LinkedIn enrichment
│   ├── leads_with_company_summary.csv     # Leads data with generated company summaries
│   ├── leads_with_summary_and_tags.csv    # Leads data with summaries and AI-generated tags
│   └── scored_leads.csv                   # Leads data scored
├── scraper/
│   └── scraper_new.py                     # Web scraping logic to fetch leads from sources like Clutch
├── enrichment/
│   └── enrichment.py                      # Functions to enrich leads with LinkedIn data
├── scoring/
│   └── scoring.py                         # Lead scoring and tier assignment logic
├── profile_summarizer/
│   └── summarize_company.py               # AI-powered company summary generation
├── ai_tag_generation/
│   └── ai_tag_generator.py                # AI tag generation based on company summaries
├── frontend/
│   └── app.py                             # Streamlit app for user interface and filtering
└── README.md                              # Project documentation and instructions

```

---

## Notes

* The AI models require a valid API key and connection to the OpenAI-compatible endpoint.
* The app currently processes a limited number of leads for enrichment and tagging to control API usage and runtime.
* The UI is designed for ease of use with toggles to switch between different views and results.

