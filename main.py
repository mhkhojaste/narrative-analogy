import os

# os.environ["HF_HOME"] = "/var/scratch/zln016/huggingface"
# os.environ["TRANSFORMERS_CACHE"] = "/var/scratch/zln016/huggingface/transformers"
# os.environ["HF_DATASETS_CACHE"] = "/var/scratch/zln016/huggingface/datasets"
# os.environ["VLLM_CACHE_DIR"] = "/var/scratch/zln016/vllm_cache"

import json
import argparse
import pandas as pd
from datetime import datetime
import pickle
from sklearn import metrics
import sys
import openai
import re
from collections import defaultdict
from tqdm import tqdm
import ast
import random
# random.seed(42)

from utils.Extraction.unit_extraction import run_unit_extraction
from utils.Extraction.abstraction_extraction import run_abstraction_extraction
from utils.Mapping.main_mapping import run_main_mapping


def parse_arguments():
    parser = argparse.ArgumentParser(description="Run the code for: unit extraction, unit abstraction, stage extraction, relation extraction, and mapping.")
    parser.add_argument('--dataset', required=True, help="Name of the dataset to use")
    parser.add_argument('--model', required=True, help="Model name")
    parser.add_argument('--task', required=True, help="Task")
    parser.add_argument('--unit', required=True, help="Story unit")
    
    parser.add_argument('--scoring_method', default="cosine", help="How to calculate the score")
    parser.add_argument('--global_map', default="Greedy", help="Global Mapping")
    parser.add_argument('--config', type=json.loads, default={}, help='Dictionary in JSON format' )

    return parser.parse_args()

def run_task(args):
    if args.task == "unit_extraction":
        print("\n Start extracting units\n ------------")
        run_unit_extraction(args)
    elif args.task == "mapping":
        print("\n Start mapping\n ------------")
        run_main_mapping(args)
    else:
        print(f"\n Start extracting abstractions for {args.task}\n ------------")
        run_abstraction_extraction(args)
        
    
def main():
    args = parse_arguments()
    
    run_task(args)
    
    
if __name__ == "__main__":
    main()