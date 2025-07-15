"""
This example describes how to use the workflow interface to chat.
"""

import os, json
from dotenv import load_dotenv  # 新增
from cozepy import COZE_CN_BASE_URL
from cozepy import Coze, TokenAuth, Message, ChatStatus, MessageContentType  # noqa

# 加载 .env 文件
load_dotenv()

def create_articles(page_url: str):
    """
    Create articles from the given page URL.
    :param page_url: The URL of the page to create articles from.
    :return: A dictionary containing the content and metadata of the created articles.
    """
    # 从环境变量获取 token
    coze_api_token = os.getenv('COZE_API_TOKEN')
    # The default access is api.coze.com, but if you need to access api.coze.cn,
    # please use base_url to configure the api endpoint to access
    coze_api_base = COZE_CN_BASE_URL

    # Init the Coze client through the access_token.
    coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)

    # Create a workflow instance in Coze, copy the last number from the web link as the workflow's ID.
    workflow_id = '7526872708178772022'

    # Call the coze.workflows.runs.create method to create a workflow run. The create method
    # is a non-streaming chat and will return a WorkflowRunResult class.
    workflow = coze.workflows.runs.create(
        workflow_id=workflow_id,
        parameters={
            "page_url": page_url,
        }
    )

    try:
        data = json.loads(workflow.data)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        data = {
            "raw": workflow.data
        }
    return data

if __name__ == "__main__":
    # Example usage
    page_url = "https://www.diancang.xyz/waiguomingzhu/17921/335654.html"
    # data = create_articles(page_url)
    data = json.load(open('data.json', 'r', encoding='utf-8'))
    # print(data)
    
    for topic, article in zip(data['topics'], data['articles']):
        item = {
            "topic": topic,
            "content": article,
            "url": data['url'],
        }

        json.dump(
            item,
            open(f"articles/{topic}.json", "w", encoding="utf-8"),
            ensure_ascii=False,
            indent=2
        )
