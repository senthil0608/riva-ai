"""
Script to trigger Google Classroom authentication.
"""
from tools.google_classroom_tool import get_classroom_service

import argparse
from tools.google_classroom_tool import get_classroom_service

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Authenticate with Google Classroom")
    parser.add_argument("--email", help="Student email to authenticate", required=True)
    args = parser.parse_args()
    
    print(f"Starting authentication flow for {args.email}...")
    service = get_classroom_service(args.email)
    if service:
        print(f"Authentication successful for {args.email}!")
    else:
        print(f"Authentication failed for {args.email}.")
