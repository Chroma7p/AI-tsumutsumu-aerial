from enum import Enum
from json import JSONDecodeError

import openai
import tiktoken
from typing import Callable
import json
from openai.types import chat
from openai._streaming import Stream  # noqa


class Role(Enum):
    system = "system"
    user = "user"
    assistant = "assistant"
    function = "function"
    tool = "tool"


class Model(Enum):
    gpt35 = "gpt-3.5-turbo"
    gpt35latest = "gpt-3.5-turbo-0125"
    gpt4 = "gpt-4"
    gpt4turbo = "gpt-4-turbo"
    gpt4vp = "gpt-4-vision-preview"
    gpt4p = "gpt-4-1106-preview"


class GPTFunctionProperty:
    def __init__(self, name: str, param_type: str, description: str, enum: Enum | None = None):
        self.name = name
        self.param_type = param_type
        self.description = description
        if enum is None:
            enum = []
        if isinstance(enum, Enum):
            self.enum = enum
        elif issubclass(type(enum), Enum):
            self.enum = [e.value for e in enum]
        else:
            self.enum = enum

    def to_json(self):
        if self.enum:
            return {"type": self.param_type,  "enum": self.enum}
        return {"type": self.param_type, "description": self.description}


class GPTFunctionParam:
    def __init__(self, properties: list[GPTFunctionProperty], required: list[GPTFunctionProperty]):
        self.properties = properties
        self.required = required

    def to_json(self):
        return {"type": "object", "properties": {prop.name: prop.to_json() for prop in self.properties}, "required": [prop.name for prop in self.required]}


class GPTFunction:
    def __init__(self, name: str, description: str, param: GPTFunctionParam, func: Callable):
        self.name = name
        self.description = description
        self.param = param
        self.func = func

    def to_json(self):
        obj = {"type": "function", "function": {
            "name": self.name, "description": self.description}}
        obj["function"]["parameters"] = self.param.to_json()
        return obj


class Message:
    """
    メッセージのクラス
    メッセージごとにロールと内容とトークンを保持する
    """

    def __init__(self, role: Role, content: str, token: int = 0, name: str = "", img: list[str] | None = None, tool_call_id: str | None = None, tool_calls: dict = {}):
        self.role: Role = role
        self.content: str = content
        if not self.content:
            self.content = ""
        self.token: int = token
        if token == 0:
            self.calc_token()
        self.name: str = name
        if img is None:
            self.img: list[str] = []
        else:
            self.img: list[str] = img

        self.tool_calls: dict = tool_calls

        self.tool_call_id: str | None = tool_call_id

    def msg2dict(self) -> dict:
        if self.tool_calls:
            return {"role": self.role.name, "content": self.content, "tool_calls": self.tool_calls}
        if self.tool_call_id and self.role == Role.tool:
            return {"role": self.role.name, "content": self.content, "tool_call_id": self.tool_call_id, "name": self.name}
        if self.role == Role.function:
            return {"role": self.role.name, "content": self.content, "name": self.name}
        if len(self.img) > 0:
            return {"role": self.role.name, "content": [{"type": "text", "text": self.content}]+[{"type": "image_url", "image_url": self.img[i]} for i in range(len(self.img))]}
        return {"role": self.role.name, "content": self.content}

    def set_token(self, token: int) -> None:
        self.token = token

    def msg2str(self) -> str:
        return f"{self.role.name} : {self.content}"

    def __str__(self) -> str:
        return str(self.msg2dict())
        # return self.msg2str()

    def calc_token(self):
        """Returns the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo-0301")
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        if self.content:
            try:
                self.token = len(encoding.encode(self.content))
            except UnicodeEncodeError:
                pass
        else:
            self.token = 0


class ResponseFunctionCall:
    def __init__(self, name: str, arguments: str):
        self.name: str = name
        self.arguments: dict = json.loads(arguments)


class Response:
    """
    レスポンスのクラス
    必要な情報を雑にまとめる
    """

    def __init__(self, response: chat.ChatCompletion):
        self.choices = response.choices
        if self.choices:
            self.messages: list[Message] = [Message(Role(
                choice.message.role), choice.message.content)for choice in self.choices]
        self.created = response.created
        self.id = response.id
        self.model = response.model
        self.completion_tokens = response.usage.completion_tokens
        self.prompt_tokens = response.usage.prompt_tokens
        if self.choices[0].message.tool_calls:
            self.function_call = self.choices[0].message.tool_calls[0].function
        else:
            self.function_call = None
        if self.function_call:
            try:
                self.function_call = ResponseFunctionCall(
                    self.function_call.name, self.function_call.arguments)
            except JSONDecodeError:
                print(self.function_call.arguments)
                exit()

        """
        print(self.choices)
        print(self.messages)
        print(self.created)
        print(self.id)
        print(self.model)
        print(self.completion_tokens)
        print(self.prompt_tokens)
        """


class Chat:
    """
    チャットのクラス
    """

    def __init__(self, api_key: str, organization: str | None = None, model: Model = Model.gpt35, functions: list[GPTFunction] | None = None, base_prompts: list[Message] | None = None, token_limit: int = 4096, n: int = 1, thin_out_flag: bool = False) -> None:
        self.organization: str | None = organization
        self.history: list[Message] = []
        self.model: Model = model
        self.token_limit: int = token_limit
        self.n: int = n
        self.thin_out_flag: bool = thin_out_flag
        self.api_key: str = api_key
        self.functions: list[GPTFunction] = functions
        self.base_prompts: list[Message] | None = base_prompts
        openai.api_key = self.api_key
        if self.organization:
            openai.organization = self.organization
        self.client = openai.OpenAI()

    def add(self, message: list[Message] | Message, output: bool = False) -> None:
        """
        トークログの末尾にメッセージを追加
        """

        if type(message) is list:
            if output:
                for msg in message:
                    print(msg)
            self.history.extend(message)
        elif type(message) is Message:
            self.history.append(message)
            if output:
                print(message)
        else:
            raise Exception("can't add anything that is not a message")

    def completion(self, output: bool = False) -> Message:
        """
        現在の履歴の状態で返信を得る
        戻り値はMessageクラス
        """

        print(self.make_log())

        response = self.create()

        if response.function_call:
            for func in self.functions:
                if func.name == response.function_call.name:
                    params = {param.name: response.function_call.arguments[param.name]
                              for param in func.param.properties if param.name in response.function_call.arguments}
                    func_result = func.func(**params)
                    result = Message(Role.system, func_result, name=func.name)
                    self.add(result)
                    return self.completion(output=output)
            else:
                print("no function")
                exit()
        completion_token = response.completion_tokens
        reply: Message = response.messages[0]
        reply.set_token(completion_token)
        self.add(reply)
        if output:
            print(reply)
        return reply

    def send(self, message: str | Message, role: Role = Role.user, output: bool = False) -> Message:
        """
        メッセージを追加して送信して返信を得る
        messageがMessageクラスならそのまま、strならMessageクラスに変換して送信
        add+completionみたいな感じ
        戻り値はMessageクラス
        """
        if type(message) is str:
            message = Message(role, message)

        if self.get_now_token() + len(message.content) > self.token_limit:
            # トークン超過しそうなら良い感じに間引くかエラーを吐く
            if self.thin_out_flag:
                self.thin_out()
            else:
                raise Exception("token overflow")

        self.add(message, output=output)
        reply = self.completion(output=output)
        self.history.append(reply)
        return reply

    def send_stream(self, message: str | Message, role: Role = Role.user, output: bool = False):
        print("send_stream", self.functions)
        if type(message) is str:
            message = Message(role, message)
        if message.content:
            if self.get_now_token() + len(message.content) > self.token_limit:
                # トークン超過しそうなら良い感じに間引くかエラーを吐く
                if self.thin_out_flag:
                    self.thin_out()
                else:
                    raise Exception("token overflow")
        self.add(message, output=output)
        openai.api_key = self.api_key
        log = self.make_log()
        if self.organization:
            openai.organization = self.organization
        if self.functions:
            response: Stream[chat.ChatCompletionChunk] = self.client.chat.completions.create(
                model=self.model.value,
                messages=log,
                max_tokens=1000,
                tools=[func.to_json()
                       for func in self.functions] if self.functions else None,
                tool_choice="auto",
                n=self.n,
                stream=True,
            )
        else:
            response: Stream[chat.ChatCompletionChunk] = self.client.chat.completions.create(
                model=self.model.value,
                messages=log,
                n=self.n,
                stream=True,
            )
        content = ""
        tool_name = {
            "name": "",
            "arguments": ""
        }
        tool_call_id = None

        for chunk in response:
            if type(chunk) is not chat.ChatCompletionChunk:
                continue
            delta = chunk.choices[0].delta
            role = delta.role
            content = delta.content
            print(f"role:{role}")
            if delta.tool_calls:
                print(delta.tool_calls[0].function.to_json())
                print(tool_name)
                if tool_call_id is None:
                    tool_call_id = delta.tool_calls[0].id
                if "name" in delta.tool_calls[0].function.to_dict():
                    tool_name["name"] += delta.tool_calls[0].function.name
                if "arguments" in delta.tool_calls[0].function.to_dict():
                    tool_name["arguments"] += delta.tool_calls[0].function.arguments
            else:
                if delta.content:
                    content += delta.content
                    yield delta.content
        print("stream end")
        if tool_name["name"]:
            arguments = json.loads(tool_name["arguments"])
            for func in self.functions:
                print(func.name, tool_name)
                if func.name == tool_name["name"]:
                    try:
                        reply = func.func(**arguments)
                    except Exception as e:
                        print(e)
                        reply = "エラーが発生しました"
                # print(f"func:{func.name} reply:{reply}")
                    try:
                        tool_calls = [{
                            "id": tool_call_id,
                            "function": tool_name,
                            "type": "function"
                        }]
                        print(tool_calls)
                        msg = Message(Role.assistant, None,
                                      tool_calls=tool_calls)
                        self.add(msg)
                        reply = Message(Role.tool, reply,
                                        name=func.name, tool_call_id=tool_call_id)
                        for i in self.send_stream(reply):
                            yield i
                    except Exception as e:
                        print(e)
                        reply = "エラーが発生しました"
                    break

        self.add(Message(Role.user, content))

    def make_log(self) -> list[dict]:
        """
        メッセージインスタンスのリストをAPIに送信する形式に変換
        """
        return [hist.msg2dict() for hist in self.base_prompts+self.history if hist.msg2dict()]

    def get_now_token(self) -> int:
        """
        現在のトークン数を取得
        """
        return sum([x.token for x in self.base_prompts+self.history])

    def thin_out(self, n: int | None = None) -> None:
        """
        トークログをTOKEN_LIMITに基づいて8割残すように先頭から消す
        引数nで減らす分のトークン数を指定
        """
        if not n:
            limit = self.token_limit * 0.8
        else:
            limit = self.token_limit - n
        now_token = self.get_now_token()
        remove_token = 0
        remove_index = 0
        while now_token - remove_token > limit:
            remove_token += self.history[remove_index].token
            remove_index += 1
        self.history = self.history[remove_index:]

    def create(self) -> Response:
        """
        openaiのAPIを叩く
        """
        openai.api_key = self.api_key
        if self.organization:
            openai.organization = self.organization
        log = self.make_log()
        try:
            # print(log)
            if self.functions:
                response = self.client.chat.completions.create(
                    model=self.model.value,
                    messages=log,
                    tools=[func.to_json()
                           for func in self.functions] if self.functions else None,
                    tool_choice="auto",
                    n=self.n,
                    max_tokens=1000,
                )
            else:
                response = self.client.chat.completions.create(
                    model=self.model.value,
                    messages=log,
                    n=self.n,
                    max_tokens=1000,
                )
        except Exception as e:
            print(e)
            exit()
        else:
            print(response)
        try:
            return Response(response)
        except Exception as e:
            print(e)
            print(response)
            exit()

    def get_history(self) -> str:
        """
        会話ログをテキスト化
        """
        text: str = ""

        for i, msg in enumerate(self.history):
            text += f"{i:03}:{msg.msg2str()[:-20]}\n"

        return text

    def remove(self, index: int) -> None:
        """
        ログの一部削除
        """
        if not 0 <= index < len(self.history):
            raise Exception("index out of range")

        self.history = [self.history for i,
                        _ in enumerate(self.history) if (i+1) != index]

    def reset(self):
        """
        ログの全削除
        """
        self.history = []
