""" 

Multi-Agent System Example: Trip Data Concierge

This example demonstrates a multi-agent system where a central "Trip Data Concierge Agent" orchestrates interactions between two specialized agents: a "Database Agent" that provides mock hotel data, and a "Concierge Agent" that offers personalized travel recommendations based on the database information. The Concierge Agent also utilizes a third agent, the "Food Critic Agent," to give witty restaurant suggestions.

                         +-----------------------------------------------------------+
                         |              🧭 Trip Data Concierge Agent                 |
                         |-----------------------------------------------------------|
                         |  Model: gemini-2.5-flash                                  |
                         |  Description:                                             |
                         |   Orchestrates database query and travel recommendation  |
                         |-----------------------------------------------------------|
                         |  🔧 Tools:                                                |
                         |   1. call_db_agent                                        |
                         |   2. call_concierge_agent                                 |
                         +-----------------------------------------------------------+
                                      /                                \
                                     /                                  \
                                    ▼                                    ▼
        +-------------------------------------------+    +---------------------------------------------+
        |            🔧 Tool: call_db_agent         |    |         🔧 Tool: call_concierge_agent        |
        |-------------------------------------------|    |---------------------------------------------|
        | Calls: db_agent                           |    | Calls: concierge_agent                       |
        |                                           |    | Uses data from db_agent for recommendations |
        +-------------------------------------------+    +---------------------------------------------+
                                |                                          |
                                ▼                                          ▼
       +--------------------------------------------+   +------------------------------------------------+
       |              📦 db_agent                   |   |             🤵 concierge_agent                  |
       |--------------------------------------------|   |------------------------------------------------|
       | Model: gemini-2.5-flash                    |   | Model: gemini-2.5-flash                         |
       | Role: Return mock JSON hotel data          |   | Role: Hotel staff that handles user Q&A        |
       +--------------------------------------------+   | Tools:                                          |
                                                         |  - food_critic_agent                           |
                                                         +------------------------------------------------+
                                                                                 |
                                                                                 ▼
                                                       +------------------------------------------------+
                                                       |          🍽️ food_critic_agent                  |
                                                       |------------------------------------------------|
                                                       | Model: gemini-2.5-flash                         |
                                                       | Role: Gives a witty restaurant recommendation   |
                                                       +------------------------------------------------+

"""

import asyncio
from google.adk.agents import Agent
from google.adk.tools import AgentTool
from google.adk.tools.tool_context import ToolContext
from utils.runner import run_agent_query, session_service, my_user_id