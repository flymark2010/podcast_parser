from bs4 import BeautifulSoup
import json, glob, os
from modelscope.pipelines import pipeline
import numpy as np

def parse_html(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Get title
    title = soup.title.string.strip() if soup.title else ""

    # Get podcast-audio src
    audio_tag = soup.find("audio", id="podcast-audio")
    audio_src = ""
    if audio_tag:
        source_tag = audio_tag.find("source")
        if source_tag and source_tag.has_attr("src"):
            audio_src = source_tag["src"]

    # Get conversation list
    transcript_div = soup.find("div", id="transcript")
    conversation = []
    if transcript_div:
        for p in transcript_div.find_all("p"):
            span = p.find("span")
            if span:
                speaker = span.get_text(strip=True).replace(":", "")
                text = p.get_text(strip=True)
                # Remove speaker from text
                if text.startswith(span.get_text(strip=True)):
                    text = text[len(span.get_text(strip=True)):].lstrip(":：").strip()
                conversation.append({"speaker": speaker, "text": text})

    data = {
        "title": title,
        "audio": audio_src,
        "conversation": conversation,
    }

    return data

class CAMPlusPlus:
    def __init__(self):
        self.pipeline = pipeline(
            task='speaker-diarization',
            model='/workspace/models/iic/speech_campplus_speaker-diarization_common/',
            model_revision='v1.0.0',
            disable_update=True,
        )

    def __call__(self, wav_file, oracle_num=2):
        timeline = self.pipeline(wav_file, oracle_num=oracle_num)
        return to_json(timeline)
    
def to_json(obj):
    if isinstance(obj, dict):
        return {k: to_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_json(i) for i in obj]
    elif isinstance(obj, (np.integer, np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float32, np.float64)):
        return float(obj)
    else:
        return obj

def batch_process_timeline(path):
    model = CAMPlusPlus()

    files = glob.glob(os.path.join(path, "htmls", "*.html"))
    
    for file in files:
        print(f"Processing {file}...")
        filename = os.path.basename(file).replace(".html", "")
        output_file = os.path.join(path, "jsons", f"{filename}.json")
        if os.path.exists(output_file):
            print(f"Skipping {output_file}, already exists.")
            continue
        data = parse_html(file)
        data['timeline'] = model(data["audio"], oracle_num=2)

        with open(output_file, "w", encoding="utf-8") as out_file:
            json.dump(data, out_file, ensure_ascii=False, indent=2)


def single_process_timeline():
    filename = "解码孩子行为背后的心理密码-2ff904688b"
    html_file = f"htmls/{filename}.html"
    output_file = f"jsons/{filename}.json"
    data = parse_html(html_file, output_file)

    model = CAMPlusPlus()
    data['timeline'] = model(data["audio"], oracle_num=2)
    print(data['timeline'])
    print(type(data['timeline']))
    with open(output_file, "w", encoding="utf-8") as out_file:
        json.dump(data, out_file, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    batch_process_timeline('./podcasts')
