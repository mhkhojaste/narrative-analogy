import json
import numpy as np
import os


# os.environ["CUDA_VISIBLE_DEVICES"] = "1,2"

# os.environ['TRANSFORMERS_CACHE'] = "../../../cache"
# os.environ['HF_HOME'] = "../../../cache"



import time
import openai
import base64
import requests
# import ollama
from transformers import AutoModelForCausalLM, AutoTokenizer
from vllm import LLM, SamplingParams

import torch

## Define dicts
model_short_dict = {"Qwen3-1.7B":"Qwen1_", "Llama-3.1-8B":"Llama8_", "Qwen3-8B":"Qwen8_", "Qwen3-8B-vllm":"Qwen8vllm_", "Llama-3.1-8B-vllm":"Llama8vllm_"}
task_abstraction_short = {"timeline_extraction": "timeline", "conceptual_abstraction_level0": "conceptual0", "conceptual_abstraction_level1": "conceptual1",
        "evaluative_abstraction": "evaluative", "arc_abstraction": "arc","stage_abstraction": "stage"}




## Functions
def read_json_file(file_path):
    with open(file_path) as f:
        data = json.load(f)
    return data
    

config = read_json_file("../config.json")


# openai_key = config['openai_key']
# openai.api_key =openai_key
# DEEPSEEK_API_URL = config['DEEPSEEK_API_URL']
# DEEPSEEK_API_KEY = config['DEEPSEEK_API_KEY']
# headers = {
#     "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
#     "Content-Type": "application/json"
# }

# huggingface_key = config['huggingface_key']


_qwen_model = None
_qwen_tokenizer = None

_qwen3_8_model = None
_qwen3_8_tokenizer = None

_qwen3_8_model_vllm = None
_qwen3_8_tokenizer_vllm = None

_llama31_8_model_vllm = None
_llama31_8_tokenizer_vllm = None

_llama3_model = None
_llama3_tokenizer = None

def get_qwen_model():
    global _qwen_model, _qwen_tokenizer
    if _qwen_model is None or _qwen_tokenizer is None:
        model_name = "Qwen/Qwen3-1.7B"
        _qwen_tokenizer = AutoTokenizer.from_pretrained(model_name)
        _qwen_model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map="auto"
        )
    return _qwen_model, _qwen_tokenizer
    
    
def get_qwen3_8_model():
    global _qwen3_8_model, _qwen3_8_tokenizer
    if _qwen3_8_model is None or _qwen3_8_tokenizer is None:
        model_name = "Qwen/Qwen3-8B"
        _qwen3_8_tokenizer = AutoTokenizer.from_pretrained(model_name)
        _qwen3_8_model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map="auto"
        )
    return _qwen3_8_model, _qwen3_8_tokenizer

def get_qwen3_8_model_vllm():
    
    global _qwen3_8_model_vllm, _qwen3_8_tokenizer_vllm
    if _qwen3_8_model_vllm is None or _qwen3_8_tokenizer_vllm is None:
        model_name = "Qwen/Qwen3-8B"
        _qwen3_8_tokenizer_vllm = AutoTokenizer.from_pretrained(model_name)
        _qwen3_8_model_vllm = LLM(
            model="Qwen/Qwen3-8B",
            trust_remote_code=True,     
            tensor_parallel_size=2,     
            dtype="float16",            
            gpu_memory_utilization=0.90, #0.9
            max_model_len=8000,         
            enforce_eager=True,
            max_num_batched_tokens=30000           
        )
    return _qwen3_8_model_vllm, _qwen3_8_tokenizer_vllm

def get_llama31_8_model_vllm():
    global _llama31_8_model_vllm, _llama31_8_tokenizer_vllm
    if _llama31_8_model_vllm is None or _llama31_8_tokenizer_vllm is None:
        model_name = "meta-llama/Meta-Llama-3.1-8B-Instruct"
        _llama31_8_tokenizer_vllm = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        _llama31_8_model_vllm = LLM(
            model=model_name,
            trust_remote_code=True,
            tensor_parallel_size=2,       # same settings as Qwen
            dtype="float16",
            gpu_memory_utilization=0.90,
            max_model_len=8000,
            enforce_eager=True,
            max_num_batched_tokens=30000,
        )
    return _llama31_8_model_vllm, _llama31_8_tokenizer_vllm

    
def get_llama3_model(model_name="meta-llama/Llama-3.1-8B-Instruct"):
    global _llama3_model, _llama3_tokenizer
    if _llama3_model is None or _llama3_tokenizer is None:
        _llama3_tokenizer = AutoTokenizer.from_pretrained(model_name)
        _llama3_model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map="auto"
        )
    return _llama3_model, _llama3_tokenizer


def get_free_gpu():
    os.system('nvidia-smi -q -d Memory |grep -A4 GPU|grep Used >tmp')
    memory_available = [-int(x.split()[2]) for x in open('tmp', 'r').readlines()]
    os.system("rm tmp")
    GPU_id = int(np.argmax(memory_available))
    print("using GPU{}".format(GPU_id))
    return GPU_id




def write_json_file(data, file_path):
    with open(file_path, 'w', encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def read_jsonl_file(file_path):
    with open(file_path) as f:
        data = [json.loads(line) for line in f]
    return data

def write_jsonl_file(data, file_path):
    with open(file_path, 'w') as f:
        for obj in data:
            line = json.dumps(obj)
            f.write(line + '\n')
            


def login_huggingface(access_token):
    from huggingface_hub import login
    login(token=access_token)
    
# login_huggingface(huggingface_key)

def query_ollama(prompt, model='gemma3:12b'):
  messages=[]
  messages.append({"role": "system", "content": prompt})
  response = ollama.chat(model, messages=messages)
  return response['message']['content'].strip()
 

def query_gpt(prompt,model='gpt-4o-mini-2024-07-18',system_prompt = 'You are a helpful AI assistant. '):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': prompt}],
        n=1,
        temperature=0,
        max_tokens=2048,
    )

    output = response['choices'][0]['message']['content']
    
    return output
    

def query_deepseek(prompt):
  payload = {
    "model": "deepseek-chat",  
    "messages": [
        {"role": "system", "content": 'You are a helpful AI assistant.'},
        {"role": "user", "content": prompt}
    ],
    "temperature": 0.2,
    "max_tokens": 500,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0
  }

  try:
    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        response_data = response.json()
        response_s1 = response_data['choices'][0]['message']['content']
        return response_s1.strip()
    else:
        print(f"Error: {response.status_code} - {response.text}")

  except requests.exceptions.RequestException as e:
    raise Exception(f"An error occurred: {e}")

def query_qwen(prompt, model_name):
    if model_name == "Qwen3-1.7B":
        model, tokenizer = get_qwen_model()
    elif model_name == "Qwen3-8B":
        model, tokenizer = get_qwen3_8_model()
        
    messages = [{"role": "user", "content": prompt}]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=2000,
        do_sample=False
    )
    output_ids = generated_ids[0][model_inputs.input_ids.shape[1]:]
    output = tokenizer.decode(output_ids, skip_special_tokens=True).strip()
    return output

def query_qwen_vllm(prompt, model_name):
    if model_name == "Qwen3-8B":
        model, tokenizer = get_qwen3_8_model_vllm()
    sampling_params = SamplingParams(
    temperature=0.6, top_p=0.95, top_k=20, max_tokens=1024
    )
    messages = [{"role": "user", "content": prompt}]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,  
    )

    outputs = model.generate([text], sampling_params)
    return outputs[0].outputs[0].text

def tokenise_vllm_batch(prompt):
    global _qwen3_8_tokenizer_vllm
    if _qwen3_8_tokenizer_vllm is None:
        model_name = "Qwen/Qwen3-8B"
        _qwen3_8_tokenizer_vllm = AutoTokenizer.from_pretrained(model_name)

    tokenizer = _qwen3_8_tokenizer_vllm

    messages = [{"role": "user", "content": prompt}]
    ids = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        enable_thinking=False,  
    )
    L = len(ids)
    return L


def query_model_vllm_batch(prompts, model_name):
    if model_name == "Qwen3-8B":
        model, tokenizer = get_qwen3_8_model_vllm()
    elif model_name == "Llama-3.1-8B":
        model, tokenizer = get_llama31_8_model_vllm()

    sampling_params = SamplingParams(
    temperature=0.0, max_tokens=3000
    )

    texts = []
    for p in prompts:
        msgs = [{"role": "user", "content": p}]
        if "Qwen" in model_name:
            t = tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        else:  # Llama or others
            t = tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)

        texts.append(t)

    outs = model.generate(texts, sampling_params)
    return [o.outputs[0].text for o in outs]

    
    
def query_llama3(prompt):
    model, tokenizer = get_llama3_model()
    messages = [{"role": "user", "content": prompt}]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    inputs = tokenizer([text], return_tensors="pt").to(model.device)
    generated_ids = model.generate(
        **inputs,
        max_new_tokens=2000,
        do_sample=False
    )
    output_ids = generated_ids[0][inputs.input_ids.shape[1]:]
    return tokenizer.decode(output_ids, skip_special_tokens=True).strip()
    
    
def query_models(prompt, model):
    if model == "gpt-4o-mini":
        response_text = query_gpt(prompt)
    elif model == "gpt-4o":
        response_text = query_gpt(prompt, "gpt-4o")
    elif model == "deepseek":
        response_text = query_deepseek(prompt)
    elif model == "Qwen3-1.7B":
        response_text = query_qwen(prompt, "Qwen3-1.7B")
    elif model == "Qwen3-8B":
        response_text = query_qwen(prompt, "Qwen3-8B")
    elif model == "Qwen3-8B-vllm":
        response_text = query_qwen_vllm(prompt, "Qwen3-8B")
    elif model == "Llama-3.1-8B":
        response_text = query_llama3(prompt)
    # elif model == "gemma3:12b":
    #     response_text = query_ollama(prompt, "gemma3:12b")
    
        
        
    return response_text
    
def query_models_batch(prompts, model):
    if model == "Qwen3-8B-vllm":
        return query_model_vllm_batch(prompts, "Qwen3-8B")
    elif model == "Llama-3.1-8B-vllm":
        return query_model_vllm_batch(prompts, "Llama-3.1-8B")
    else:
        raise ValueError(f"Unknown model: {model}")

def check_model_answer(result):
    if result.isdigit():
        return int(result)
    else:
        return 5


def gpu_analysis(prompts):
    prompt_lengths = []
    print("Counting tokens per prompt...")
    for p in tqdm(prompts, desc="Prompts"):
        prompt_lengths.append(tokenise_vllm_batch(p))

    num_prompts = len(prompt_lengths)
    avg_len = sum(prompt_lengths) / num_prompts
    max_len = max(prompt_lengths)
    print(f"\n=== Per-prompt stats ===")
    print(f"Prompts: {num_prompts}")
    print(f"Average length: {avg_len:.1f} tokens")
    print(f"Max length: {max_len} tokens")

    # ---- Per-batch totals ----
    batch_sizes=[8, 16, 32]

    for bs in batch_sizes:
        batch_totals = []
        for i in range(0, num_prompts, bs):
            batch_totals.append(sum(prompt_lengths[i:i+bs]))
        avg_batch = sum(batch_totals) / len(batch_totals)
        max_batch = max(batch_totals)
        print(f"\n=== Batch size {bs} ===")
        print(f"Number of batches: {len(batch_totals)}")
        print(f"Average batch total: {avg_batch:.1f} tokens")
        print(f"Max batch total: {max_batch} tokens")

    print("prompt_lengths: ", prompt_lengths)