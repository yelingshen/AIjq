#!/usr/bin/env python3
"""Simple health check utility for local server endpoints."""
import argparse
import sys
import requests

def check_url(url, timeout=5):
    try:
        r = requests.get(url, timeout=timeout)
        return r.status_code, r.text[:500]
    except Exception as e:
        return None, str(e)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--url', required=True, help='Base url to check (e.g. http://127.0.0.1:5000/)')
    p.add_argument('--ask', help='Simple POST JSON to /ask (provide query string)')
    args = p.parse_args()

    status, body = check_url(args.url)
    if status is None:
        print(f'FAILED to reach {args.url}: {body}')
        sys.exit(2)
    print(f'OK {args.url} -> {status}')

    if args.ask:
        ask_url = args.url.rstrip('/') + '/ask'
        try:
            r = requests.post(ask_url, json={'query': args.ask}, timeout=10)
            print('ASK ->', r.status_code, r.text[:1000])
        except Exception as e:
            print('ASK FAILED ->', e)
            sys.exit(3)

if __name__ == '__main__':
    main()
