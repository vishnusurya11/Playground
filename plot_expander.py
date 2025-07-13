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
        ("Sci-Fi", "A Mars colony engineer uncovers a sealed vault labeled with a warning—written in her own handwriting, dated centuries ago."),
        ("Mystery", "A retired postman receives a letter he never delivered—postmarked from a town that no longer exists."),
        ("Horror", "A hiking group stumbles upon a perfectly preserved 1950s diner deep in the forest—and it's still open for service."),
        ("Fantasy", "A thief steals a magical blade that sings only when it’s near someone who has lied to them."),
        ("Romance", "Two people begin falling in love through handwritten notes left in borrowed library books—until one of them vanishes."),
        ("Thriller", "A bodyguard discovers the person she’s protecting is orchestrating the threats against them."),
        ("Adventure", "An explorer finds an ancient map tattooed on the bones of a long-dead sailor."),
        ("Historical Fiction", "A maid in 1800s London overhears a conspiracy that aligns exactly with a modern political scandal."),
        ("Noir", "A PI’s client is murdered—right after telling him she’s already been killed once before."),
        ("Cyberpunk", "A street-level fixer discovers a mind-hacking app that lets others upload memories into strangers without consent."),
        ("Post-Apocalyptic", "A traveler finds a town untouched by the apocalypse—because no one there knows it happened."),
        ("Supernatural", "A man inherits a watch that stops time—but only when he’s feeling regret."),
        ("Psychological Thriller", "A woman wakes up each day in a slightly different version of her life, with subtle changes—until the wrong people start noticing."),
        ("Western", "A bounty hunter chases a criminal into a desert town where time resets every sunrise."),
        ("Political Thriller", "A junior senator discovers that every major world leader is part of a centuries-old chess game."),
        ("Espionage", "A spy’s cover is blown when their fake life starts behaving like it’s real—and someone begins impersonating their ‘real’ identity."),
        ("Legal Drama", "A defense attorney is assigned a case where all evidence has been erased—even the crime itself."),
        ("Medical Drama", "A doctor discovers her patient has two sets of DNA—each with a different history."),
        ("Mythology", "A linguist deciphers a newly discovered epic that claims the gods never left—they just changed their names."),
        ("Satire", "In a world where corporations elect presidents directly, a janitor accidentally becomes the CEO of Earth."),
        ("Comedy", "A support group for side characters realizes none of them remember how their stories ended."),
        ("Coming-of-Age", "A teenager develops a rare condition where his dreams physically manifest each morning."),
        ("Gothic", "A governess is hired to care for a mute child in a crumbling manor—only to learn the child hasn’t been alive for years."),
        ("Urban Fantasy", "A food delivery app begins directing its riders into portals leading to magical realms."),
        ("Crime", "A former getaway driver discovers the abandoned safehouse he used as a rookie has been turned into a luxury Airbnb."),
        ("Military Fiction", "A soldier returns home to find their hometown under control of a private army—run by people who served under their name."),
        ("Steampunk", "An airship mechanic finds an engine blueprint in an old novel—and it works on dreams, not fuel."),
        ("Paranormal Romance", "A woman keeps seeing a stranger in her dreams—until she meets him at her grandfather’s funeral."),
        ("Time Travel", "A researcher builds a time machine that only works while she's asleep—and she wakes up in lives she never lived."),
        ("Magical Realism", "A fisherman catches the same fish every morning, no matter where he casts his line—and it always knows something new.")
    ]

    
    expander = PlotExpander()
    results = expander.expand_plot_list(plots)
    
    print(f"\n\nProcessed {len(results)} plots successfully!")
    print(f"All outputs saved to 'forge' directory")