import json
import os
import re

import requests


def clean_text(text: str) -> str:
    cleaned_text = re.sub("<[^>]*>", "", text)  # Remove HTML tags
    cleaned_text = cleaned_text.replace(
        "\\n", " "
    )  # Replace newline characters with spaces
    return cleaned_text


def _google_search(query: str, num_results=8) -> str:
    """
    Perform a Bing search and return the results as a JSON string.
    """
    print(f"_google_search:{query}")
    API_KEY = os.getenv("GOOGLE_API_KEY")
    API_CX = os.getenv("GOOGLE_API_CX")
    if API_KEY is None or API_CX is None:
        raise ValueError("Please configure GOOGLE_API_KEY and GOOGLE_API_CX in .env first!")

    # Bing Search API endpoint
    search_url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&q={query}&cx={API_CX}&start=0&num=10"

    response = requests.get(search_url)
    response.raise_for_status()
    search_results = response.json()

    # Extract the search result items from the response
    search_results = search_results.get("items", [])

    # Create a list of search result dictionaries with 'title', 'href', and 'body' keys
    search_results_list = [
        {
            "title": item["title"],
            "href": item["link"],
            "body": item["snippet"],
        }
        for item in search_results
    ]

    # Return the search results as a JSON string
    return search_to_view(search_results)


def search_to_view(results):
    view: str = ""
    for item in results:
        view = view + f"### [{item['title']}]({item['link']}) \n"
        view = view + f"{item['snippet']} \n"
    return view
