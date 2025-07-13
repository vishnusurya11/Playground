#!/usr/bin/env python3
"""
League Management Utility for EpicWeaver
Manage league tables, seasons, and data
"""

import argparse
from league_system import LeagueSystem


def main():
    parser = argparse.ArgumentParser(description="Manage EpicWeaver League Tables")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show league statistics')
    
    # Reset command
    reset_parser = subparsers.add_parser('reset', help='Reset league to fresh state')
    reset_parser.add_argument('--no-archive', action='store_true', 
                             help='Skip archiving current data')
    
    # New season command
    season_parser = subparsers.add_parser('new-season', help='Start a new season')
    
    # Prune command
    prune_parser = subparsers.add_parser('prune', help='Prune old data to reduce file size')
    prune_parser.add_argument('--keep', type=int, default=100,
                             help='Number of recent entries to keep (default: 100)')
    
    args = parser.parse_args()
    
    # Initialize league system
    league = LeagueSystem()
    
    if args.command == 'stats':
        stats = league.get_league_stats()
        print("\n📊 LEAGUE STATISTICS")
        print("=" * 40)
        print(f"Season: {stats['season']}")
        print(f"Teams: {stats['total_teams']}")
        print(f"Voters: {stats['total_voters']}")
        print(f"Total Matches: {stats['total_matches']}")
        print(f"File Size: {stats['file_size_kb']} KB")
        print(f"Last Updated: {stats['last_updated']}")
        
    elif args.command == 'reset':
        print("\n🔄 RESETTING LEAGUE")
        print("=" * 40)
        archive = not args.no_archive
        if league.reset_league(archive_current=archive):
            print("✅ League successfully reset!")
        else:
            print("❌ Failed to reset league")
            
    elif args.command == 'new-season':
        print("\n🆕 STARTING NEW SEASON")
        print("=" * 40)
        if league.start_new_season():
            print("✅ New season started successfully!")
        else:
            print("❌ Failed to start new season")
            
    elif args.command == 'prune':
        print(f"\n✂️  PRUNING OLD DATA (keeping last {args.keep} entries)")
        print("=" * 40)
        pruned = league.prune_old_data(keep_last_n=args.keep)
        if pruned > 0:
            print("✅ Pruning completed successfully!")
        else:
            print("ℹ️  No data needed pruning")
            
    else:
        parser.print_help()


if __name__ == "__main__":
    main()