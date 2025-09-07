"""
Command-line interface for interacting with Dexter.
Run this script to send queries to the Dexter backend from your terminal.
"""
import requests


def main():
    host = "http://localhost:8000"
    print("Dexter CLI. Type your request and press Enter. Ctrl+C to exit.")
    while True:
        try:
            query = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting Dexter CLI.")
            break
        if not query.strip():
            continue
        try:
            response = requests.post(f"{host}/query", json={"query": query})
            if response.ok:
                data = response.json()
                print(f"Dexter: {data.get('response')}")
            else:
                print(f"Error: {response.status_code} {response.text}")
        except Exception as e:
            print(f"Request failed: {e}")


if __name__ == "__main__":
    main()
