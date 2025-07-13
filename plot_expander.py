# Plot Expander - Multi-Agent System with Voting (Modular Version)

from typing import List, Tuple
from datetime import datetime
from pathlib import Path
import json
import os
from dotenv import load_dotenv

from config import config
from schemas import PlotExpanderOutput
from team_manager import TeamManager
from voting_strategies import VotingStrategyFactory

# Load environment variables
load_dotenv()


class PlotExpander:
    """Main plot expander using the modular architecture"""
    
    def __init__(self, config_path: str = "model_teams_config.json"):
        self.team_manager = TeamManager(config_path)
        self.output_dir = config.get_output_directory()
        self.output_dir.mkdir(exist_ok=True)
        self.voting_strategy = "standard"  # Default voting strategy
    
    def save_plot_output(self, plot_id: str, output: PlotExpanderOutput):
        """Save plot expansion output to forge folder"""
        filename = config.get_file_name(output.genre, output.original_plot)
        filepath = self.output_dir / filename
        
        # Convert Pydantic model to dict and save as JSON
        output_dict = output.model_dump()
        with open(filepath, 'w') as f:
            json.dump(output_dict, f, indent=2)
        
        print(f"Saved plot expansion to: {filepath}")
        return filepath
    
    def print_voting_summary(self, output: PlotExpanderOutput):
        """Print voting summary in a clear, readable format"""
        summary = output.voting_results.voting_summary
        
        print("\n" + "="*80)
        print("COMPREHENSIVE VOTING SUMMARY")
        print("="*80)
        
        # 1. Vote Distribution
        print("\n📊 VOTE DISTRIBUTION:")
        print("-" * 40)
        for team, count in summary["vote_distribution"].items():
            winner_mark = " 🏆" if team == output.voting_results.winning_team else ""
            print(f"  {team}: {count} votes{winner_mark}")
        
        # 2. Agent Votes
        print("\n🗳️ AGENT VOTING DETAILS:")
        print("-" * 40)
        for agent, details in summary["agent_votes"].items():
            print(f"  {agent}:")
            print(f"    → Voted for: {details['voted_for']}")
            print(f"    → Model: {details['model_used']}")
            print(f"    → Total score given: {details['total_score']}")
        
        # 3. Team Average Scores
        print("\n📈 TEAM AVERAGE SCORES:")
        print("-" * 40)
        for team, scores in summary["team_avg_scores"].items():
            print(f"  {team}:")
            for criterion, avg_score in scores.items():
                if criterion != "total_avg":
                    print(f"    - {criterion}: {avg_score}")
            print(f"    📊 Overall Average: {scores.get('total_avg', 0)}")
        
        # 4. Voting Patterns
        print("\n🔍 VOTING PATTERNS:")
        print("-" * 40)
        patterns = summary["voting_patterns"]
        print(f"  Most unanimous criteria: {', '.join(patterns['unanimous_criteria'])}")
        print(f"  Most divisive criteria: {', '.join(patterns['most_divisive_criteria'])}")
        
        print("\n  Model voting preferences:")
        for model, prefs in patterns["model_preferences"].items():
            print(f"    {model}:")
            for team, count in prefs.items():
                print(f"      - {team}: {count} vote(s)")
        
        # 5. Quick summary dict
        print("\n📋 QUICK SUMMARY DICT:")
        print("-" * 40)
        quick_summary = {
            "winner": output.voting_results.winning_team,
            "vote_count": summary["vote_distribution"],
            "agent_votes": {
                agent: details["voted_for"] 
                for agent, details in summary["agent_votes"].items()
            }
        }
        print(json.dumps(quick_summary, indent=2))
        
        # 6. Winning expansion details
        print("\n🏆 WINNING EXPANSION DETAILS:")
        print("-" * 40)
        selected = output.selected_expansion
        print(f"Team: {selected['team_name']}")
        print(f"Model: {selected['model_used']}")
        print(f"Title: {selected['title']}")
        print(f"Logline: {selected['logline']}")
        print(f"Main Characters: {len(selected['main_characters'])}")
        for char in selected['main_characters'][:2]:  # Show first 2 characters
            print(f"  - {char['name']} ({char['role']})")
        print(f"Themes: {', '.join(selected['themes'])}")
        print(f"Unique Hooks: {', '.join(selected['unique_hooks'][:2])}")  # Show first 2 hooks
        print(f"Complexity: {selected['estimated_complexity']}/10")
    
    def expand_single_plot(self, genre: str, plot: str) -> PlotExpanderOutput:
        """Main function: Expand one plot through full process"""
        start_time = datetime.now()
        
        # Step 1: Each team expands the plot
        all_expansions = self.team_manager.expand_plot(genre, plot)
        
        if not all_expansions:
            raise ValueError("No expansions were generated!")
        
        # Step 2: Voting council evaluates and votes
        print("\nVoting council is evaluating all expansions...")
        voting_results = self.team_manager.conduct_voting(all_expansions, self.voting_strategy)
        
        # Step 3: Select winning expansion
        winning_expansion = all_expansions[voting_results.winning_team]
        
        # Step 4: Create output with consolidated selected_expansion
        selected_expansion = {
            "team_name": winning_expansion.team_name,
            "model_used": winning_expansion.model_used,
            "title": winning_expansion.title,
            "logline": winning_expansion.logline,
            "main_characters": [
                {
                    "name": char.name,
                    "role": char.role,
                    "description": char.description
                } for char in winning_expansion.main_characters
            ],
            "plot_summary": winning_expansion.plot_summary,
            "central_conflict": winning_expansion.central_conflict,
            "story_beats": {
                "opening": winning_expansion.story_beats.opening,
                "catalyst": winning_expansion.story_beats.catalyst,
                "midpoint": winning_expansion.story_beats.midpoint,
                "crisis": winning_expansion.story_beats.crisis,
                "resolution": winning_expansion.story_beats.resolution
            },
            "ending": winning_expansion.ending,
            "key_elements": winning_expansion.key_elements,
            "potential_arcs": winning_expansion.potential_arcs,
            "themes": winning_expansion.themes,
            "unique_hooks": winning_expansion.unique_hooks,
            "estimated_complexity": winning_expansion.estimated_complexity
        }
        
        end_time = datetime.now()
        output = PlotExpanderOutput(
            original_plot=plot,
            genre=genre,
            all_expanded_plots=all_expansions,
            voting_results=voting_results,
            selected_expansion=selected_expansion,
            timestamp=start_time.isoformat(),
            processing_time=(end_time - start_time).total_seconds()
        )
        
        # Step 5: Save to file
        plot_id = f"{genre.lower()}_{abs(hash(plot))}"
        self.save_plot_output(plot_id, output)
        
        # Step 6: Print voting summary
        self.print_voting_summary(output)
        
        return output
    
    def expand_plot_list(self, plot_list: List[Tuple[str, str]]) -> List[PlotExpanderOutput]:
        """Process multiple plots"""
        results = []
        
        # Print active teams info
        team_info = self.team_manager.get_team_info()
        counts = self.team_manager.get_team_count()
        
        print("\n" + "="*80)
        print("ACTIVE TEAMS AND CONFIGURATION")
        print("="*80)
        print(f"\n📚 Expansion Teams ({counts['expansion_teams']} active):")
        for team in team_info['expansion_teams']:
            print(f"  - {team}")
        print(f"\n🗳️ Voting Council ({counts['voting_agents']} active):")
        for agent in team_info['voting_agents']:
            print(f"  - {agent}")
        print("="*80)
        
        for genre, plot in plot_list:
            print(f"\n{'='*60}")
            print(f"Processing: {genre} - {plot}")
            print(f"{'='*60}")
            
            result = self.expand_single_plot(genre, plot)
            results.append(result)
            
            # Voting summary is already printed in expand_single_plot
        
        return results


# Example usage
if __name__ == "__main__":
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key in the .env file")
        exit(1)
    
    # Example plot list
    plots = [
        ("Sci-Fi", "A quantum physicist finds a message embedded in cosmic background radiation—signed with her name and dated five minutes into the future."),
        ("Mystery", "An antique collector finds a diary that describes a murder from 1912—written in his own handwriting."),
        ("Horror", "A babysitter realizes the nursery rhymes the child sings are recounting her darkest memories, word for word."),
        ("Fantasy", "A librarian discovers a hidden shelf that lends books no one else can see—each one recounting a life she never lived."),
        ("Historical Fiction", "A Civil War soldier's letters start predicting battles days before they occur—signed by a general who never existed."),
        ("Crime", "A forensic accountant discovers a series of shell companies whose board members have all been missing persons for decades."),
        ("Psychological Thriller", "A woman wakes up each morning in a new version of her apartment—same layout, but different memories and relationships."),
        ("Noir", "A private investigator is hired to follow someone—only to realize he's tailing himself in a version of the city that shouldn't exist."),
        ("Adventure", "A spelunker finds ancient carvings of modern machines deep in a cave system untouched for millennia."),
        ("Post-Apocalyptic", "A survivor in a flooded Earth finds a functioning lighthouse—run by an AI still waiting for a captain that never returned."),
        ("Romantic Suspense", "A man starts receiving love letters from someone who claims to have known him in a past life—letters written in his own style."),
        ("Urban Fantasy", "A delivery driver realizes his route maps out forgotten ley lines—and each package changes the energy of the city."),
        ("Political Thriller", "An intern discovers that classified files from different eras all refer to the same mysterious advisor—who hasn't aged in seventy years."),
        ("Supernatural", "A radio repairman hears broadcasts from people who died years ago—reporting news that hasn't happened yet."),
        ("Cyberpunk", "A street-level hacker stumbles onto a neural ad-stream that starts inserting memories of a life he never lived—one he wants back.")
    ]
    
    expander = PlotExpander()
    results = expander.expand_plot_list(plots)
    
    print(f"\n\nProcessed {len(results)} plots successfully!")
    print(f"All outputs saved to 'forge' directory")