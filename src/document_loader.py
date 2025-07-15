import bs4
from langchain_community.document_loaders import WebBaseLoader
from langchain_unstructured import UnstructuredLoader


def web_loader(page_url):
    loader = UnstructuredLoader(web_url=page_url)
    
    page_content = ''
    doc = None
    for doc in loader.load():
        if isinstance(doc, bs4.element.Tag):
            page_content += doc.get_text(separator="\n", strip=True) + "\n"
        else:
            page_content += doc.page_content + "\n"
    
    if not doc:
        raise ValueError("No content loaded from the provided URL.")

    return {
        "content": page_content.strip(),
        "metadata": doc.metadata,
    }

if __name__ == "__main__":
    # Example usage
    page_url = "https://www.diancang.xyz/waiguomingzhu/17921/335652.html"
    print(web_loader(page_url))