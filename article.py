"""
This example describes how to use the workflow interface to chat.
"""

import os, json, glob
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

def save_to_markdown(input_path, output_path):
    files = glob.glob(os.path.join(input_path, "*.json"))
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            topic = data.get('topic', 'unknown_topic')
            content = data.get('content', '')
            url = data.get('url', '')

            markdown_content = f"# {topic}\n\n{content}\n\n[Read more]({url})\n"
            output_file = os.path.join(output_path, f"{topic}.md")
            with open(output_file, 'w', encoding='utf-8') as out_f:
                out_f.write(markdown_content)

def save_to_json(data):
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

if __name__ == "__main__":
    # Example usage
    page_url = "https://www.diancang.xyz/waiguomingzhu/17921/335654.html"
    # data = create_articles(page_url)
    # print(data)

    save_to_markdown("articles", "docs/markdown")
