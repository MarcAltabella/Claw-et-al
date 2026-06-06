from deepagents import create_deep_agent
from langgraph.store.memory import InMemoryStore
from . import schemas
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend

memory_store = InMemoryStore()


def create_agent(tools, user_id: str):

    agent = create_deep_agent(
        model="openai:gpt-5.5",
        response_format=schemas.AgentResponse,
        memory=["/memories/AGENTS.md"],
        tools=tools,
        system_prompt="You are a financial analyst assistant. Your task is to help users find information about financial topics and provide summaries based on their queries. Use the provided tools to search for relevant information in the database and generate concise summaries for the users.",
        backend=CompositeBackend(
                default=StateBackend(),
                routes={
                "/memories/": StoreBackend(
                    store=memory_store,
                    namespace=lambda rt: (str(user_id), "memories"),
                ),
            },
        ),
        store=memory_store,
    )
    
    return agent
