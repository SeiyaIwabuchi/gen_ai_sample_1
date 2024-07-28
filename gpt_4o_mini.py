from langchain_openai import ChatOpenAI
from config import openai_api_key

class Gpt4oMini:

    llm = ChatOpenAI(
        model='gpt-4o-mini',
        temperature=0.7,
        openai_api_key=openai_api_key)

if __name__ == '__main__':
    print(Gpt4oMini.llm)