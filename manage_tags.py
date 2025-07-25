#!/usr/bin/env python3
import argparse
from database import NFCDatabase
from datetime import datetime

def list_tags(db):
    """List all registered tags"""
    tags = db.list_tags()
    
    if not tags:
        print("No tags registered yet.")
        return
    
    print("\nRegistered NFC Tags:")
    print("-" * 80)
    print(f"{'UID':<25} {'Name':<20} {'HTML File':<20} {'Last Access':<15}")
    print("-" * 80)
    
    for tag in tags:
        uid, name, html_file, last_access = tag
        last_access_str = last_access if last_access else "Never"
        print(f"{uid:<25} {name:<20} {html_file:<20} {last_access_str:<15}")

def add_tag(db, uid, name, html_file, description):
    """Add a new tag"""
    # Format UID
    uid = uid.upper()
    if not ':' in uid:
        # Add colons if not present
        uid = ':'.join([uid[i:i+2] for i in range(0, len(uid), 2)])
    
    success = db.add_tag(uid, name, html_file, description)
    
    if success:
        print(f"Successfully added tag: {uid}")
        print(f"  Name: {name}")
        print(f"  HTML File: {html_file}")
        print(f"  Description: {description}")
    else:
        print(f"Failed to add tag. UID {uid} may already exist.")

def show_logs(db, tag_uid=None, limit=20):
    """Show access logs"""
    logs = db.get_access_log(tag_uid, limit)
    
    if not logs:
        print("No access logs found.")
        return
    
    print("\nAccess Logs:")
    print("-" * 70)
    print(f"{'UID':<25} {'Name':<20} {'Access Time':<25}")
    print("-" * 70)
    
    for log in logs:
        uid, name, access_time = log
        print(f"{uid:<25} {name:<20} {access_time:<25}")

def interactive_add(db):
    """Interactive mode to add a tag"""
    print("\nInteractive Tag Addition")
    print("Scan the NFC tag now, or enter its UID manually...")
    
    uid = input("Tag UID (e.g., 04:5C:7B:2A:6C:50:80): ").strip()
    if not uid:
        print("Cancelled.")
        return
    
    name = input("Tag name: ").strip()
    if not name:
        print("Cancelled.")
        return
    
    html_file = input("HTML filename (e.g., info.html): ").strip()
    if not html_file:
        print("Cancelled.")
        return
    
    description = input("Description (optional): ").strip()
    
    add_tag(db, uid, name, html_file, description)

def main():
    parser = argparse.ArgumentParser(description='NFC Tag Management Tool')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all registered tags')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new tag')
    add_parser.add_argument('uid', help='Tag UID (e.g., 04:5C:7B:2A:6C:50:80)')
    add_parser.add_argument('name', help='Tag name')
    add_parser.add_argument('html_file', help='HTML filename')
    add_parser.add_argument('--description', default='', help='Tag description')
    
    # Interactive add command
    interactive_parser = subparsers.add_parser('interactive', help='Add tag interactively')
    
    # Logs command
    logs_parser = subparsers.add_parser('logs', help='Show access logs')
    logs_parser.add_argument('--uid', help='Filter by tag UID')
    logs_parser.add_argument('--limit', type=int, default=20, help='Number of logs to show')
    
    args = parser.parse_args()
    
    # Initialize database
    db = NFCDatabase()
    
    if args.command == 'list':
        list_tags(db)
    elif args.command == 'add':
        add_tag(db, args.uid, args.name, args.html_file, args.description)
    elif args.command == 'interactive':
        interactive_add(db)
    elif args.command == 'logs':
        show_logs(db, args.uid, args.limit)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
