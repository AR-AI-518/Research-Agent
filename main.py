
from langchain.tools import tool
from tavily import TavilyClient
from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import time
from rich import print

import requests
import os
from dotenv import load_dotenv

# Load the variables from the .env file into the environment
load_dotenv()


tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


@tool
def get_search(query: str) -> str:
    '''Search the web for recent and reliable topic'''
    result = tavily.search(query=query, max_results=5)
    out = []
    for r in result['results']:
        out.append(
            f"URL: {r['url']}\nTitle: {r['title']}\nSnippet: {r['content'][:500]}"
        )
    return "\n\n".join(out)   # BUG FIX 1: return missing tha, function None de raha tha
 
 
@tool
def get_information(url: str) -> str:
    """Extract the main text content from a webpage URL."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0.0.0 Safari/537.36"
        )
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        return text[:3000]
    except Exception as e:
        return f"Error: {str(e)}"
 
 
model = ChatOpenAI(model='gpt-4o-mini') 
 
 
def search_agent():
    return create_agent(model=model, tools=[get_search])
 
 
def info_agent():
    return create_agent(model=model, tools=[get_information])
 
 
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.
 
Topic: {topic}
Research Gathered:
{research}
Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)
 
Be detailed, factual and professional."""),
])
writer_chain = writer_prompt | model | StrOutputParser()
 
 
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.
 
Report:
{report}
Respond in this exact format:
Score: X/10
Strengths:
- ...
- ...
Areas to Improve:
- ...
- ...
One line verdict:
..."""),
])
critic_chain = critic_prompt | model | StrOutputParser()
 
 
def get_research(inp: str) -> dict:
    state = {}
 
    # BUG FIX 3: agar search hi fail ho jaye to pura function crash ho jata tha
    try:
        print("Scraping URLs...")
        search_agent_instance = search_agent()
        search_result = search_agent_instance.invoke({
            "messages": [("user", f"Search the web for recent and reliable content about this: {inp}")]
        })
        state["search_result"] = search_result["messages"][-1].content
    except Exception as e:
        state["search_result"] = f"Search failed: {e}"
 
    try:
        print("Gathering information...")
        info_agent_instance = info_agent()
        research_result = info_agent_instance.invoke({
            "messages": [
                ("user",
                 f"Based on the following search results about '{inp}', "
                 f"pick the most relevant URL and scrape it for deeper content.\n\n"
                 f"Search Results:\n{state['search_result']}"
                )
            ]
        })
        state["research_result"] = research_result["messages"][-1].content
    except Exception as e:
        state["research_result"] = f"Scraping failed: {e}"
 
    combine_search = (
        f"Search Result:\n{state['search_result']}\n\n"
        f"Research Result:\n{state['research_result']}"
    )
 
    print("Writing report...")
    state["report"] = writer_chain.invoke({"topic": inp, "research": combine_search})
 
    print("Reviewing report...")
    state["feed_back"] = critic_chain.invoke({"report": state["report"]})
 
    return state
 
 
if __name__ == "__main__":
    inp = input("Make your research ")
    try:
        result = get_research(inp)
        print("\n" + "=" * 50)
        print(result["report"])
        print("\n" + "=" * 50)
        print(result["feed_back"])
    except Exception as e:
        print(f"An error occurred: {e}. Try again.")
