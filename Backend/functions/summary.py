from langchain_community.document_loaders import TextLoader
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains.summarize import load_summarize_chain
from langchain_groq import ChatGroq
from langchain_core.documents import Document
import os 
from dotenv import load_dotenv
load_dotenv()
groq_api_key=os.getenv('GROQ_API_KEY')
llm=ChatGroq(model='llama-3.1-8b-instant',api_key=groq_api_key)
def extract_summary(articles):
    # Handle both string and list inputs
    if isinstance(articles, str):
        # If it's a string, treat it as a single document
        docs = [Document(page_content=articles)]
    elif isinstance(articles, list):
        # If it's a list of dicts (articles), convert to Documents
        if articles and isinstance(articles[0], dict):
            docs = [Document(page_content=f"Title: {article['title']}\n\nAbstract: {article['abstract']}\n\nAuthors: {', '.join(article['authors'])}\n\nPublication Date: {article['publication_date']}") 
                    for article in articles]
        else:
            # If it's a list of strings or other format
            docs = [Document(page_content=str(article)) for article in articles]
    else:
        # Fallback for other types
        docs = [Document(page_content=str(articles))]
    final_documents=RecursiveCharacterTextSplitter(chunk_size=2000,chunk_overlap=100).split_documents(docs)
    chunks_prompt="""
    Please summarize the below speech:
    Speech:`{text}'
    Summary:
    """
    map_prompt_template=PromptTemplate(input_variables=['text'],
                                        template=chunks_prompt)
    final_prompt='''
    Provide the final summary of the entire speech with these important points.
    Add a Motivation Title,Start the precise summary with an introduction and provide the summary in number 
    points for the speech.
    Speech:{text}

    '''
    final_prompt_template=PromptTemplate(input_variables=['text'],template=final_prompt)
    

    chain=load_summarize_chain(
    llm=llm,
    chain_type="refine",
    verbose=True
    )
    output_summary=chain.invoke(final_documents)
    return output_summary