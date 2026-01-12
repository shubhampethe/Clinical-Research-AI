from mcp.server.fastmcp import FastMCP 
from functions.diagnosys_symptoms import extract_symptoms
from functions.pubmed_articales import fetch_pubmed_articles_with_metadata
from functions.summary import extract_summary

mcp = FastMCP(
    name="Clinisight AI",
    host="0.0.0.0",
    port=8000,
)

@mcp.tool()
async def clinisight_ai(symptom_text):
    symptom = extract_symptoms(symptom_text)
    pubmed_article = fetch_pubmed_articles_with_metadata(" ".join(symptom))
    summary = extract_summary(pubmed_article[:3000])

    return {
        "symptom":symptom,
        "pubmed_summary" :summary
    }





if __name__ == "__main__":
    mcp.run(transport="streamable-http", mount_path="/mcp")
