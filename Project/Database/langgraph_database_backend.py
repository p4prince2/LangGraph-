from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import sqlite3


load_dotenv()

llm =  ChatOpenAI(
    model="gpt-4o-mini",   # you can also use e.g. "aAnthropic/claude-3.5-sonnet"
    base_url="https://openrouter.ai/api/v1",
    temperature=0.7,api_key="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"
)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

conn=sqlite3.connect(database='chatbot.db',check_same_thread=False)

# Checkpointer
checkpointer = SqliteSaver (conn=conn)

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

def retreve_threds_All():
    all=set()
    for checkpoint in checkpointer.list(None):
        all.add(checkpoint.config['configurable']['thread_id'])

    return list(all)