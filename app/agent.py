from deepagents import create_deep_agent
from langgraph.store.memory import InMemoryStore
from . import schemas
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from dotenv import load_dotenv

load_dotenv()

memory_store = InMemoryStore()
AGENT_MODEL = "google_genai:gemini-2.5-flash"

def create_agent(tools, user_id: str):

    agent = create_deep_agent(
        model=AGENT_MODEL,
        response_format=schemas.AgentResponse,
        memory=["/memories/AGENTS.md"],
        tools=tools,
        system_prompt="You are a machine learning researcher. Your task is to help users find information about research topics and provide summaries based on their queries. Use the provided tools to search for relevant information in the database and generate concise summaries for the users. Do not return information unrelated to research.",
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
