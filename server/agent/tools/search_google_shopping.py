from langchain_community.utilities import SerpAPIWrapper
from langchain_core.tools import tool


@tool
def search_google_shopping(query: str) -> dict:
    """
    Expand search with Google Shopping

    Input: Product name or description.
    Example query: `"Blue cotton shirt, size M"`
    Returns: First result from the search.
    """

    search = SerpAPIWrapper(
        params={
            "engine": "google_shopping",
            "num": 1,
        }
    )
    results = search.run(query)

    if not results:
        return results

    first_result = results[0]
    return {
        "name": first_result.get("name", ""),
        "price": first_result.get("price", ""),
        "description": first_result.get("description", ""),
        "source": first_result.get("source", ""),
        "images": [first_result.get("thumbnail", "")],
        "url": first_result.get("product_link", ""),
    }

    # mock for save quotas
    # return {
    #     "name": "Mock Product Name",
    #     "price": "$100",
    #     "description": "Mock Product Description",
    #     "source": "Mock Source",
    #     "images": ["https://example.com/image.jpg"],
    #     "url": "https://example.com/product",
    # }
