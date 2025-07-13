# Plot Expander - LangChain/LangGraph Implementation Template

from typing import List, Dict, TypedDict, Annotated
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command
import operator

# Import our existing models
from plot_expander import (
    ExpandedPlotProposal, 
    VotingResult, 
    VotingResults,
    PlotExpanderOutput
)

# State for the expansion team discussion
class ExpansionState(TypedDict):
    genre: str
    plot: str
    team_name: str
    messages: Annotated[List[dict], operator.add]
    current_expansion: str
    final_proposal: ExpandedPlotProposal

# State for voting
class VotingState(TypedDict):
    all_proposals: Dict[str, ExpandedPlotProposal]
    votes: Annotated[List[VotingResult], operator.add]
    winner: str

def create_expansion_team_agent(agent_config: dict, model_name: str):
    """Create an agent for the expansion team"""
    model = ChatOpenAI(model=model_name, temperature=agent_config.get("temperature", 0.7))
    
    # Use structured output for the agent
    structured_model = model.with_structured_output(ExpandedPlotProposal)
    
    def agent_node(state: ExpansionState):
        # Build prompt with system prompt and current state
        system_prompt = agent_config["system_prompt"]
        
        prompt = f"""
{system_prompt}

Genre: {state["genre"]}
Plot: {state["plot"]}
Team: {state["team_name"]}

Previous discussion:
{state.get("messages", [])}

Please provide your contribution to the plot expansion.
"""
        
        # Get structured response
        response = structured_model.invoke(prompt)
        
        # Update state
        return {
            "messages": [{"role": agent_config["role"], "content": str(response)}],
            "current_expansion": response.expanded_plot
        }
    
    return agent_node

def create_voting_agent(agent_config: dict, model_name: str):
    """Create a voting council agent"""
    model = ChatOpenAI(model=model_name, temperature=agent_config.get("temperature", 0.3))
    
    # Use structured output for voting
    structured_model = model.with_structured_output(VotingResult)
    
    def voting_node(state: VotingState):
        system_prompt = agent_config.get("system_prompt", "You are a voting council member.")
        
        # Build voting prompt
        proposals_text = "\n\n".join([
            f"Team {name}:\n{proposal.expanded_plot}"
            for name, proposal in state["all_proposals"].items()
        ])
        
        prompt = f"""
{system_prompt}

Please evaluate these plot expansions and vote for the best one:

{proposals_text}

Consider the criteria: originality, coherence, market potential, character depth, thematic richness, and expandability.
"""
        
        # Get structured vote
        vote = structured_model.invoke(prompt)
        
        return {"votes": [vote]}
    
    return voting_node

def create_expansion_team_graph(team_config: dict):
    """Create a graph for one expansion team's internal discussion"""
    workflow = StateGraph(ExpansionState)
    
    # Add nodes for each agent in the team
    for agent_name, agent_config in team_config["agents"].items():
        agent_node = create_expansion_team_agent(
            agent_config, 
            team_config["model_name"]
        )
        workflow.add_node(agent_name, agent_node)
    
    # Define the flow: lead -> analyst -> consultant -> END
    workflow.add_edge(START, "lead_expander")
    workflow.add_edge("lead_expander", "story_analyst")
    workflow.add_edge("story_analyst", "creative_consultant")
    workflow.add_edge("creative_consultant", END)
    
    return workflow.compile()

def create_voting_council_graph(voting_config: dict, num_agents: int = 7):
    """Create a graph for the voting council"""
    workflow = StateGraph(VotingState)
    
    # Add voting agents
    for i in range(1, num_agents + 1):
        agent_key = f"agent_{i}"
        if agent_key in voting_config:
            agent_config = voting_config[agent_key]
            voting_node = create_voting_agent(
                agent_config,
                agent_config["model_name"]
            )
            workflow.add_node(agent_key, voting_node)
    
    # All agents vote in parallel
    workflow.add_edge(START, ["agent_1", "agent_2", "agent_3", "agent_4", "agent_5", "agent_6", "agent_7"])
    
    # All connect to END
    for i in range(1, num_agents + 1):
        workflow.add_edge(f"agent_{i}", END)
    
    return workflow.compile()

# Example usage template
async def expand_plot_with_langgraph(genre: str, plot: str, config: dict):
    """Main function to expand a plot using LangGraph"""
    
    all_proposals = {}
    
    # Step 1: Run each expansion team
    for team_key, team_config in config["expansion_teams"].items():
        print(f"Running expansion team: {team_config['name']}")
        
        # Create and run the team graph
        team_graph = create_expansion_team_graph(team_config)
        
        initial_state = {
            "genre": genre,
            "plot": plot,
            "team_name": team_config["name"],
            "messages": [],
            "current_expansion": "",
            "final_proposal": None
        }
        
        # Run the team discussion
        result = await team_graph.ainvoke(initial_state)
        
        # Store the proposal
        all_proposals[team_config["name"]] = result["final_proposal"]
    
    # Step 2: Run voting council
    print("Running voting council...")
    voting_graph = create_voting_council_graph(config["voting_council"])
    
    voting_state = {
        "all_proposals": all_proposals,
        "votes": [],
        "winner": ""
    }
    
    # Run the voting
    voting_result = await voting_graph.ainvoke(voting_state)
    
    # Count votes and determine winner
    vote_tally = {}
    for vote in voting_result["votes"]:
        team = vote.vote_for_team
        vote_tally[team] = vote_tally.get(team, 0) + 1
    
    winner = max(vote_tally, key=vote_tally.get)
    
    return {
        "all_proposals": all_proposals,
        "votes": voting_result["votes"],
        "winner": winner,
        "winning_proposal": all_proposals[winner]
    }

# Note: This is a template showing the proper LangGraph structure
# Actual implementation would need error handling, async support, etc.