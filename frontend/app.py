import sys
import os
import streamlit as st
import pandas as pd
from urllib.parse import urlparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from enrichment.enrichment import enrich_dataframe_with_linkedin
from scoring.scoring import score_lead, assign_tier
from profile_summarizer.summarize_company import summarize_company
from ai_tag_generation.ai_tag_generation import generate_tags 

st.set_page_config(page_title="LeadGen AI", layout="wide")


st.markdown("""
    <style>
        .element-container:has(.stDataFrame) .stDataFrame div[data-testid="stHorizontalBlock"] {
            overflow-x: auto !important;
        }
        .stDataFrame table {
            white-space: nowrap !important;
        }
    </style>
""", unsafe_allow_html=True)

DATA_PATH = "../data/combined_leads.csv"
CATEGORIES = [
    "advertising",
    "software",
    "marketing",
    "digital-marketing",
    "social-media-marketing"
]

st.title("LeadGen AI - Explore Leads")
st.markdown("Select a category and click search to view filtered leads.")

selected_category = st.selectbox("Select a Category", CATEGORIES)


if "filtered_df" not in st.session_state:
    st.session_state.filtered_df = None
if "enriched_df" not in st.session_state:
    st.session_state.enriched_df = None
if "scored_df" not in st.session_state:
    st.session_state.scored_df = None
if "summary_df" not in st.session_state:
    st.session_state.summary_df = None
if "tags_df" not in st.session_state:
    st.session_state.tags_df = None
if "active_view" not in st.session_state:
    st.session_state.active_view = "score"  # default view i have to think about it

def make_short_link(url):
    if pd.isna(url) or not isinstance(url, str) or not url.strip():
        return ""
    parsed = urlparse(url)
    short = parsed.netloc.replace("www.", "")
    return f"[{short}]({url})"

# Search Leads
if st.button("Search Leads"):
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        filtered_df = df[df["category"].str.lower() == selected_category.lower()]
        if not filtered_df.empty:
            st.session_state.filtered_df = filtered_df.reset_index(drop=True)
            st.session_state.enriched_df = None
            st.session_state.scored_df = None
            st.session_state.summary_df = None
        else:
            st.warning(f"No leads found for category: {selected_category}")
            st.session_state.filtered_df = None
    else:
        st.error("Could not find the combined_leads.csv file.")

# Filtered Leads View
if st.session_state.filtered_df is not None:
    display_df = st.session_state.filtered_df.copy()
    display_df.index += 1
    display_df["website"] = display_df["website"].apply(make_short_link)

    st.markdown("### Filtered Leads")
    st.markdown(display_df.to_markdown(index=True), unsafe_allow_html=True)

    csv = st.session_state.filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Filtered Leads as CSV",
        data=csv,
        file_name=f"{selected_category}_leads.csv",
        mime="text/csv"
    )

    if st.button("Enrich Leads with LinkedIn"):
        with st.spinner("Enriching leads..."):
            enriched_df = enrich_dataframe_with_linkedin(st.session_state.filtered_df, limit=10)
            enriched_csv_path = os.path.join("../data", "enriched_leads_linkedin.csv")
            enriched_df.to_csv(enriched_csv_path, index=False)

            st.session_state.enriched_df = enriched_df.copy()
            st.session_state.scored_df = None
            st.session_state.summary_df = None
            st.success("Leads enriched with LinkedIn data.")

# Enriched Leads View
if st.session_state.enriched_df is not None:
    enriched_df_display = st.session_state.enriched_df.copy()
    enriched_df_display.index += 1
    enriched_df_display["website"] = enriched_df_display["website"].apply(make_short_link)
    enriched_df_display["linkedin_url"] = enriched_df_display["linkedin_url"].apply(
        lambda x: f"[LinkedIn]({x})" if pd.notnull(x) and x else ""
    )

    st.markdown("### Enriched Leads with LinkedIn URLs")
    st.markdown(enriched_df_display.to_markdown(index=True), unsafe_allow_html=True)

    enriched_csv = st.session_state.enriched_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Enriched Leads as CSV",
        data=enriched_csv,
        file_name="enriched_leads_linkedin.csv",
        mime="text/csv"
    )

    
    col1, col2, col3 = st.columns(3)


    # Score Button
    if col1.button("Score Leads"):
        with st.spinner("Scoring leads..."):
            scored_df = st.session_state.enriched_df.copy()
            scored_df["lead_score"] = scored_df.apply(score_lead, axis=1)
            scored_df["lead_tier"] = scored_df["lead_score"].apply(assign_tier)
            st.session_state.scored_df = scored_df.copy()
            st.session_state.active_view = "score"
            st.success("Leads scored!")

    # Generate Button
    if col2.button("Generate Profile Summaries"):
        with st.spinner("Generating company summaries..."):
            enriched_df = st.session_state.enriched_df.copy()
            summaries = []
            for _, row in enriched_df.iterrows():
                summary = summarize_company(
                    row.get("company_name", ""),
                    row.get("website", ""),
                    row.get("category", "")
                )
                summaries.append(summary)
            enriched_df["company_summary"] = summaries
            st.session_state.summary_df = enriched_df[["company_name", "company_summary"]].copy()
            st.session_state.active_view = "summary"
            st.success("Summaries generated.")


    if col3.button("Generate AI Tags"):
        if st.session_state.summary_df is None:
            st.warning("Please generate company summaries first!")
        else:
            with st.spinner("Generating AI tags..."):
                summary_df = st.session_state.summary_df.copy()
                tags_list = []
                for summary in summary_df["company_summary"]:
                    tags = generate_tags(summary)
                    if isinstance(tags, list):
                        tags_list.append(", ".join(tags))
                    else:
                        tags_list.append("")
                summary_df["ai_tags"] = tags_list
                st.session_state.tags_df = summary_df.copy()
                st.session_state.active_view = "tags"
                st.success("AI tags generated.")


# Display
if st.session_state.active_view == "score" and st.session_state.scored_df is not None:
    st.markdown("### Scored Leads Summary")
    display_scored = st.session_state.scored_df.copy()
    display_scored.index += 1
    display_scored = display_scored[["company_name", "rating", "lead_score", "lead_tier"]]
    st.dataframe(display_scored, use_container_width=True)

    scored_csv = display_scored.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Scored Leads Summary CSV",
        data=scored_csv,
        file_name="scored_leads_summary.csv",
        mime="text/csv"
    )





elif st.session_state.active_view == "summary" and st.session_state.summary_df is not None:
    st.markdown("### Company Profile Summaries")
    summary_df = st.session_state.summary_df.copy()
    summary_df.index += 1
    
    styled_table = summary_df.style.set_table_styles([
        {'selector': 'th.col0, td.col0', 'props': [('min-width', '220px')]},
        {'selector': 'th.col1, td.col1', 'props': [('min-width', '600px')]},
    ]).to_html()
    
    st.markdown(styled_table, unsafe_allow_html=True)
    
    summary_csv = summary_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Company Summaries CSV",
        data=summary_csv,
        file_name="company_summaries.csv",
        mime="text/csv"
    )





elif st.session_state.active_view == "tags" and st.session_state.tags_df is not None:
    st.markdown("### AI Generated Tags for Companies")
    tags_df = st.session_state.tags_df.copy()
    tags_df.index += 1
    
    
    display_tags_df = tags_df[["company_name", "ai_tags"]]
    
    st.dataframe(display_tags_df, use_container_width=True)

    tags_csv = display_tags_df.to_csv(index=True).encode("utf-8")
    st.download_button(
        label="Download AI Tags CSV",
        data=tags_csv,
        file_name="ai_tags.csv",
        mime="text/csv"
    )
