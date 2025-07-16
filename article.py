"""
This example describes how to use the workflow interface to chat.
"""

import os, json, glob, time
from dotenv import load_dotenv  # 新增
from cozepy import COZE_CN_BASE_URL
from cozepy import Coze, TokenAuth, Message, ChatStatus, MessageContentType, WorkflowExecuteStatus

# 加载 .env 文件
load_dotenv()

class CozeClient:
    def __init__(self, workflow_id: str):
        # 从环境变量获取 token
        coze_api_token = os.getenv('COZE_API_TOKEN')
        # The default access is api.coze.com, but if you need to access api.coze.cn,
        # please use base_url to configure the api endpoint to access
        coze_api_base = COZE_CN_BASE_URL

        # Init the Coze client through the access_token.
        coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)
        
        self.coze = coze
        self.workflow_id = workflow_id

class ReaderClient(CozeClient):
    def __init__(self):
        super().__init__(workflow_id='7527581309394452526')

    def retrieve(self, page_url: str):
        """
        Read the content from the given page URL.
        :param page_url: The URL of the page to read.
        :return: A dictionary containing the content and metadata of the read page.
        """
        # Call the coze.workflows.runs.create method to create a workflow run.
        workflow = self.coze.workflows.runs.create(
            workflow_id=self.workflow_id,
            is_async=False,
            parameters={
                "page_url": page_url,
            }
        )
        return workflow
    
class WorkflowClient(CozeClient):
    def __init__(self):
        super().__init__('7526872708178772022')

    def submit_task(self, page_url: str):
        """
        Create articles from the given page URL.
        :param page_url: The URL of the page to create articles from.
        :return: A dictionary containing the content and metadata of the created articles.
        """

        # Call the coze.workflows.runs.create method to create a workflow run. The create method
        # is a non-streaming chat and will return a WorkflowRunResult class.
        workflow = self.coze.workflows.runs.create(
            workflow_id=self.workflow_id,
            is_async=True,
            parameters={
                "page_url": page_url,
            }
        )
        return workflow
    
    def history(self, execute_id: str):
        history = self.coze.workflows.runs.run_histories.retrieve(
            workflow_id=self.workflow_id,
            execute_id=execute_id
        )
        return history

def create_articles(page_url: str):
    client = WorkflowClient()
    workflow = client.submit_task(page_url)
    execute_id = workflow.execute_id

    while True:
        history = client.history(execute_id)
        if history.execute_status == WorkflowExecuteStatus.SUCCESS:
            break
        if history.execute_status == WorkflowExecuteStatus.FAILED:
            print("Workflow execution failed. Reason:", history.error_message)
            break

        time.sleep(5)


def retrieve_articles(page_url: str):
    client = ReaderClient()
    workflow = client.retrieve(page_url)

    try:
        data = json.loads(workflow.data)["output"]
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    
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

            markdown_content = f"{content}\n\n[Read more]({url})\n"
            output_file = os.path.join(output_path, f"{topic}.md")
            with open(output_file, 'w', encoding='utf-8') as out_f:
                out_f.write(markdown_content)

def get_title(content):
    return content.strip().split('\n')[0].strip().lstrip('# \t\n\r\f\v')

def save_to_json(data):
    for item in data:
        article = item['content']
        topic = item['title']
        title = get_title(article)
        item = {
            "topic": topic,
            "content": article,
            "url": item['page_url'],
            "title": title
        }

        json.dump(
            item,
            open(f"articles/{title}.json", "w", encoding="utf-8"),
            ensure_ascii=False,
            indent=2
        )

if __name__ == "__main__":
    # Example usage
    page_url = "https://www.diancang.xyz/waiguomingzhu/17921/335655.html"
    # create_articles(page_url)
    data = retrieve_articles(page_url)
    print(data)
    save_to_json(data)

    save_to_markdown("articles", "/workspace/project/podcast_articles/docs/文章/")
