from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, BitsAndBytesConfig
from huggingface_hub import snapshot_download
import torch
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.outputs import LLMResult


class CustomHandler(BaseCallbackHandler):
    def on_llm_end(self, result: LLMResult, **kwargs):
        print(f"LLM Output: {result.generations[0][0].text}")


# カスタムパイプラインの作成
class GemmaPipeline:
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.task = "text-generation"  # task属性を追加

    def __call__(self, prompt, max_new_tokens=9216):
        messages = [{"role": "user", "content": "".join(prompt)}]

        print(f"{messages=}")

        input_ids = self.tokenizer.apply_chat_template(messages, return_tensors="pt", return_dict=True).to(self.model.device)
        
        outputs = self.model.generate(**input_ids, max_new_tokens=max_new_tokens)
        rawResponse: str = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        print(f"{rawResponse=}")

        response = rawResponse.replace("user\n" + ("".join(prompt)).rstrip(), "").strip()

        print(f"{ {"generated_text": response} }")

        return [{"generated_text": response}]  # リストの中に辞書を返す 一行しかない場合はそのまま返す



class Gemma:

    model_id = "google/gemma-2-2b-it"
    download_path = snapshot_download(repo_id=model_id)

    tokenizer = AutoTokenizer.from_pretrained(download_path)
    model = AutoModelForCausalLM.from_pretrained(
        download_path,
        device_map="auto",
        quantization_config=BitsAndBytesConfig(load_in_8bit=True)
        ) 
    
    pipe = GemmaPipeline(model, tokenizer)
    llm = HuggingFacePipeline(pipeline=pipe)

if __name__ == '__main__':
    print(f"{Gemma.llm=}")