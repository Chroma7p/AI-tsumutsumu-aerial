from dotenv import load_dotenv
import os
from chatgpt import Message, Role, Chat, Model, GPTFunction, GPTFunctionParam, GPTFunctionProperty
import asyncio
from uuid import uuid4
from qdrant_client import QdrantClient
from qdrant_client.http import models
from openai import OpenAI
import time
import json


def get_embedding(text, model="text-embedding-ada-002"):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"),
                    organization=os.getenv("OPENAI_ORG_KEY"))
    text = text.replace("\n", " ")
    try:
        return client.embeddings.create(input=[text], model=model, timeout=30).data[0].embedding
    except:
        time.sleep(30)
        return get_embedding(text, model)


SAVE_MEMORY_PROMPT = """\
## save_memory 
この機能は、私の記憶を保存するための機能です。\
引数は
- `memory_name` : 保存する記憶の名前
- `memory_content` : 保存する記憶の内容
- `memory_type` : 保存する記憶の種類(任意、デフォルトは`other`)


"""

memory_name_prop = GPTFunctionProperty(
    "memory_name", "string", "保存する記憶の名前を入力してください")
memory_content_prop = GPTFunctionProperty(
    "memory_content", "string", "保存する記憶の内容を入力してください")
memory_type_prop = GPTFunctionProperty(
    "memory_type", "string", "保存する記憶の種類を入力してください")
save_memory_params = GPTFunctionParam([memory_name_prop, memory_content_prop, memory_type_prop],
                                      required=[memory_name_prop, memory_content_prop])


LOAD_MEMORY_PROMPT = """\
## load_memory
この機能は、私の記憶を検索するための機能です。\
引数は
- `memory_name` : 検索する記憶の情報

"""


load_memory_name_prop = GPTFunctionProperty(
    "memory_name", "string", "検索する記憶の名前を入力してください")
load_memory_params = GPTFunctionParam([load_memory_name_prop],
                                      required=[load_memory_name_prop])

print(os.getcwd())
with open("./src/prompts/tsumugi_normal.txt", "r", encoding="utf-8") as f:
    TSUMUGI_PROMPT = f.read()

with open("./src/prompts/tsumugi_reply.txt", "r", encoding="utf-8") as f:
    TSUMUGI_REPLY = f.read()

MEMORY_TYPE_PROMPT = """\
## memory_type
記憶のタイプは以下の通りです。
記録、検索の際は以下のタイプの中から選んでください。
- `person` : 人物に関する情報
- `place` : 地名に関する情報
- `event` : イベントに関する情報
- `object` : 物体に関する情報
- `concept` : 概念に関する情報
- `talk_history` : 会話履歴
- `other` : その他の情報
"""


class Mode:
    tsumugi = "tsumugi"
    chatgpt = "chatgpt"


class Channel:
    def __init__(self, bot, channel_id, mode: Mode = Mode.tsumugi, model: Model = Model.gpt4turbo, functions: list[GPTFunction] = []) -> None:
        self.channelID = channel_id
        self.mode = mode
        self.functions = functions
        self.bot = bot
        self.model = model

        default_functions: list[GPTFunction] = [
            GPTFunction("save_memory", SAVE_MEMORY_PROMPT,
                        save_memory_params, self.save_memory),
            GPTFunction("load_memory", LOAD_MEMORY_PROMPT, load_memory_params, self.load_memory)]
        self.functions.extend(default_functions)

        print(GPTFunction("save_memory", SAVE_MEMORY_PROMPT,
                          save_memory_params, self.save_memory).to_json())
        base_prompt: list[Message] = [
            Message(Role.system, TSUMUGI_PROMPT+SAVE_MEMORY_PROMPT +
                    LOAD_MEMORY_PROMPT+MEMORY_TYPE_PROMPT),
            Message(Role.assistant, "こんにちは！あーしは埼玉ギャルの春日部つむぎだよ！"),
            Message(Role.user, "君のことを教えて！"),
            Message(
                Role.assistant, "あーしは埼玉県の高校に通う18歳のギャルで、身長155㎝だよ。誕生日は11月14日で、好きな食べ物はカレー。趣味は動画配信サイトの巡回だよ。"),
            Message(Role.user, "よろしくね！"),
            Message(Role.assistant, "よろしく！")
        ]
        self.chat = Chat(api_key=os.environ["OPENAI_API_KEY"],
                         model=self.model, functions=functions if functions else None, base_prompts=base_prompt, token_limit=128000)
        if mode == Mode.tsumugi:
            self.chat.base_prompts = base_prompt

    def save_memory(self, memory_name: str, memory_content: str, memory_type: str = "general") -> str:
        print("save_memory")
        qdrant_client = QdrantClient(
            host=os.environ["QDRANT_HOST"], port=os.environ["QDRANT_PORT"])

        qdrant_client.upsert(
            collection_name="memories",
            points=[
                models.PointStruct(
                    id=str(uuid4()),
                    vector=get_embedding(memory_name),
                    payload={"memory_name": memory_name,
                             "memory_content": memory_content, "memory_type": memory_type}
                )
            ]
        )

        return "記憶を保存したよ！"

    def load_memory(self, memory_name: str) -> str:
        print("load_memory")
        qdrant_client = QdrantClient(
            host=os.environ["QDRANT_HOST"], port=os.environ["QDRANT_PORT"])
        result = qdrant_client.search(
            collection_name="memories",
            query_vector=get_embedding(memory_name),
            limit=5,
            with_payload=True
        )

        result = [r for r in result if r.score >= 0.8]
        if len(result) == 0:
            return "記憶が見つからなかったよ！"
        else:
            return json.dumps({r.payload["memory_name"]: r.payload["memory_content"] for r in result})
