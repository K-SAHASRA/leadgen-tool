import os
import pandas as pd
from openai import OpenAI


client = OpenAI(
    api_key="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",  
    base_url="https://api.groq.com/openai/v1" 
)

MODEL_NAME = "llama3-70b-8192"  # might change it

def summarize_company(name, website, category):
    prompt = (
        f"Summarize what this company likely does, based on its name, website and category:\n\n"
        f"Name: {name}\nWebsite: {website}\nCategory: {category}\n\n"
        f"Give a short professional 1-2 sentence summary."
    )
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=100,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error summarizing {name}: {e}")
        return ""

def batch_summarize(input_filename="enriched_leads_linkedin.csv", output_filename="leads_with_company_summary.csv"):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "..", "data")

    input_path = os.path.join(data_dir, input_filename)
    output_path = os.path.join(data_dir, output_filename)

    if not os.path.exists(input_path):
        print(f"Input file not found: {input_path}")
        return

    df = pd.read_csv(input_path).head(10)

    print("Generating company summaries...")

    summaries = []
    for idx, row in df.iterrows():
        name = row.get("company_name", "")
        website = row.get("website", "")
        category = row.get("category", "")
        summary = summarize_company(name, website, category)
        summaries.append(summary)
        print(f"[{idx + 1}] {name} ➜ {summary}")

    df["company_summary"] = summaries
    df.to_csv(output_path, index=False)

    print(f"\nSummaries saved to: {output_path}")

if __name__ == "__main__":
    batch_summarize()
