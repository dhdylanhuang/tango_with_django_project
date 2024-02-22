import json
import requests
# Add your Microsoft Account Key to a file called bing.key
def read_bing_key(): 
    """
    reads the BING API key from a file called 'bing.key'
    returns: a string which is either None, i.e. no key found, or with a key
    remember to put bing.key in your .gitignore file to avoid committing it.
    See Python Anti-Patterns - it is an awesome resource to improve your python code
    Here we using "with" when opening documents
    http://bit.ly/twd-antipattern-open-files
    """
    bing_api_key = None 
    try:
        with open('bing.key', 'r') as f:
            bing_api_key = f.readline().strip()
    except FileNotFoundError:
        try:
            with open('../bing.key', 'r') as f:
                bing_api_key = f.readline().strip()
        except FileNotFoundError:
            raise IOError('bing.key file not found')

    if not bing_api_key:
        raise KeyError('Bing key not found')

    return bing_api_key

def run_query(search_terms):
    try:
        bing_key = read_bing_key()
        search_url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {'Ocp-Apim-Subscription-Key': bing_key}
        params = {'q': search_terms, 'textDecorations': True, 'textFormat': 'HTML'}
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()

        search_results = response.json()

        results = []
        for result in search_results.get('webPages', {}).get('value', []):
            results.append({
                'title': result.get('name', ''),
                'link': result.get('url', ''),
                'summary': result.get('snippet', '')
            })

        return results

    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        return None

def main():
    query = input("Enter your search query: ")
    results = run_query(query)

    if results is not None:
        for i, result in enumerate(results, start=1):
            print(f"\nResult {i}:\nTitle: {result['title']}\nLink: {result['link']}\nSummary: {result['summary']}")

if __name__ == '__main__':
    main()
