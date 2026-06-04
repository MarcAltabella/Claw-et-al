from deepagents import create_deep_agent
from .tools import find_information

agent = create_deep_agent(
    model="openai:gpt-5.5",
    tools=[find_information],
    system_prompt="You are a financial analyst assistant. Your task is to help users find information about financial topics and provide summaries based on their queries. Use the provided tools to search for relevant information in the database and generate concise summaries for the users.",
)