
from openai import OpenAI
import os
import pandas as pd

from groq import Groq  
import json

client = OpenAI(
    api_key="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", 
    base_url="https://api.groq.com/openai/v1" 
)
MODEL_NAME = "llama3-70b-8192"

def generate_tags(summary):
    prompt = f"""Based on the company description below, return 3 to 5 relevant lowercase tags that describe the company. Use hyphens for multi-word tags. Only output a JSON list.

Description:
\"\"\"
{summary}
\"\"\"
"""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=100,
        )
        content = response.choices[0].message.content.strip()
        
        tags_list = json.loads(content)

        return tags_list
    except Exception as e:
        print(f"❌ Error generating tags: {e}")
        return "[]"

def process_tags():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "..", "data", "leads_with_company_summary.csv")
    output_path = os.path.join(base_dir, "..", "data", "leads_with_summary_and_tags.csv")

    if not os.path.exists(data_path):
        print("❌ Input file not found.")
        return

    df = pd.read_csv(data_path)
    df = df.head(10)  
    print("🏷️ Generating AI tags...")
    df["ai_tags"] = df["company_summary"].fillna("").apply(generate_tags)

    df.to_csv(output_path, index=False)
    print(f"✅ Tags saved to {output_path}")

if __name__ == "__main__":
    process_tags()
