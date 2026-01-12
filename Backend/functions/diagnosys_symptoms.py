from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os 
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
groq_api_key=os.getenv('GROQ_API_KEY')
llm=ChatGroq(model='llama-3.1-8b-instant',api_key=groq_api_key)
parser=StrOutputParser()

def extract_symptoms(input_text:str):
    prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are a helpful medical assistant. "
     "Extract only the symptoms from the user's input. "
     "Return symptoms exactly as found in the text."
    ),
    ("user", "I have been facing headache and nausea since morning."),
    ("assistant", "headache, nausea"),

    ("user", "Lately I am experiencing chest pain and shortness of breath."),
    ("assistant", "chest pain, shortness of breath"),

    ("user", "{text}") 

    ])

    chain=prompt|llm|parser
    return chain.invoke({"text":input_text})



