"""
TODO: Add docstring
"""
from transformers import AutoTokenizer
import numpy as np


def preprocessing(question, context):
    model_name = 'distilbert-base-cased-distilled-squad'
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    inputs = tokenizer.encode_plus(question, context, add_special_tokens=True, return_tensors="pt")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    inputs = tokenizer.encode_plus(question, context, add_special_tokens=True, return_tensors="pt")
    return inputs


async def infer(client, inputs):
    output = client.infer(model_name="question_answering", inputs=inputs)
    return output


def postprocessing(output, input_ids):
    model_name = 'distilbert-base-cased-distilled-squad'
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    start_scores = output.as_numpy('start_logits')
    end_scores = output.as_numpy('end_logits')
    start_index = np.argmax(start_scores)
    end_index = np.argmax(end_scores)
    answer_tokens = input_ids[start_index:end_index + 1]
    answer = tokenizer.decode(answer_tokens)
    return answer
