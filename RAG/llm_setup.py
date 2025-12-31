from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    temperature=0,
    api_key= "AIzaSyCMMm7skFh74Co58A4awJDk8oVglUlyaFs"
)
