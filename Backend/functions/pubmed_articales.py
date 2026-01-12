import requests
from bs4 import BeautifulSoup

def fetch_pubmed_articles_with_metadata(
    query: str,
    max_results: int = 3,
    use_mock_if_empty: bool = True,
) -> list[dict]:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; PubMedClient/1.0; youremail@example.com)"
    }
    headers = {"User-Agent": "Mozilla/5.0"}

    # Clean the raw query: remove non-letter characters and normalize spaces
    raw = query.strip()
    # Example: if your input comes as "============ back pain"
    # or includes multiple spaces/newlines
    cleaned = " ".join(raw.split())          # collapse multiple spaces/newlines
    # Optionally strip leading punctuation like '='
    cleaned = cleaned.lstrip("=:-_")         # adjust as needed

    if not cleaned:
        return []

    formatted_query = f'"Back pain"[Title/Abstract]'

    # Step 1: ESearch – get PMIDs
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

    search_params = {
        "db": "pubmed",
        "term": formatted_query,
        "retmax": max_results,
        "retmode": "json",
        "tool": "MyPubMedClient",
        "email": "youremail@example.com",
    }

    try:
        search_resp = requests.get(
            search_url, params=search_params, headers=headers, timeout=10
        )
        search_resp.raise_for_status()
        search_json = search_resp.json()
        print(search_json)

        id_list = search_json.get("esearchresult", {}).get("idlist", [])
        if not id_list:
            if use_mock_if_empty:
                return [{
                    "title": "Simulated Study on Fever",
                    "abstract": "This is a simulated abstract on the treatment of fever in adults.",
                    "authors": ["John Doe", "Jane Smith"],
                    "publication_date": "March 2024",
                    "article_url": "https://pubmed.ncbi.nlm.nih.gov/12345678/"
                }]
            return []

        ids = ",".join(id_list)

        # Step 2: EFetch – get full XML records
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ids,
            "retmode": "xml",
            "tool": "MyPubMedClient",
            "email": "youremail@example.com",
        }

        fetch_resp = requests.get(
            fetch_url, params=fetch_params, headers=headers, timeout=10
        )
        fetch_resp.raise_for_status()

        soup = BeautifulSoup(fetch_resp.text, "lxml-xml")
        articles_xml = soup.find_all("PubmedArticle")

        articles_info = []
        for article, pmid in zip(articles_xml, id_list):
            article_metadata = article.find("Article")
            journal_issue = article.find("JournalIssue")
            pub_date_tag = journal_issue.find("PubDate") if journal_issue else None

            # Title
            title_tag = article_metadata.find("ArticleTitle") if article_metadata else None
            title = title_tag.get_text(strip=True) if title_tag else "No title"

            # Abstract
            abstract_tag = article_metadata.find("Abstract") if article_metadata else None
            abstract = (
                abstract_tag.get_text(separator=" ", strip=True)
                if abstract_tag
                else "No abstract available"
            )

            # Authors
            authors = []
            for author in article_metadata.find_all("Author") if article_metadata else []:
                last = author.find("LastName")
                fore = author.find("ForeName")
                if last and fore:
                    authors.append(f"{fore.get_text()} {last.get_text()}")
                elif last:
                    authors.append(last.get_text())
            if not authors:
                authors = ["No authors listed"]

            # Publication date
            pub_date = "No date"
            if pub_date_tag:
                year = pub_date_tag.find("Year")
                month = pub_date_tag.find("Month")
                if year and month:
                    pub_date = f"{month.get_text()} {year.get_text()}"
                elif year:
                    pub_date = year.get_text()

            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

            articles_info.append(
                {
                    "title": title,
                    "abstract": abstract,
                    "authors": authors,
                    "publication_date": pub_date,
                    "article_url": url,
                }
            )

        if not articles_info and use_mock_if_empty:
            return [{
                "title": "Simulated Study on Fever",
                "abstract": "This is a simulated abstract on the treatment of fever in adults.",
                "authors": ["John Doe", "Jane Smith"],
                "publication_date": "March 2024",
                "article_url": "https://pubmed.ncbi.nlm.nih.gov/12345678/"
            }]

        return articles_info

    except Exception as e:
        if use_mock_if_empty:
            return [{
                "title": "Simulated Study on Fever",
                "abstract": "This is a simulated abstract on the treatment of fever in adults.",
                "authors": ["John Doe", "Jane Smith"],
                "publication_date": "March 2024",
                "article_url": "https://pubmed.ncbi.nlm.nih.gov/12345678/"
            }]
        else:
            return [{"message": f"Error: {e}"}]
