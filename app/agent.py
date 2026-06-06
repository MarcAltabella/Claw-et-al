from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend


def create_agent(tools, user_id: str):

    agent = create_deep_agent(
        model="openai:gpt-5.5",
        memory=["/memories/AGENTS.md"],
        tools=tools,
        system_prompt="You are a financial analyst assistant. Your task is to help users find information about financial topics and provide summaries based on their queries. Use the provided tools to search for relevant information in the database and generate concise summaries for the users.",
        backend=CompositeBackend(
                default=StateBackend(),
                routes={
                "/memories/": StoreBackend(
                    namespace=lambda rt: (str(user_id), "memories"),
                ),
            },
        ),
    )
    
    return agent