"""
TODO: Add description here
"""
from transformers import AutoImageProcessor
from PIL import Image
import torch
import json


def preprocessing(image_path):
    image = Image.open(image_path)
    processor = AutoImageProcessor.from_pretrained("microsoft/resnet-50")
    input_data = processor(image, return_tensors="pt")['pixel_values']
    return input_data


async def infer(client, input):
    model_output = client.infer(model_name="image_classification", inputs=[input])
    model_output = model_output.as_numpy('output')
    return model_output


def postprocessing(output):
    sm_output = torch.nn.functional.softmax(torch.from_numpy(output[0]), dim=1)
    ind = torch.argmax(sm_output)
    with open("client/apps/image_classification/imagenet_class_index.json") as json_file:
        labels = json.load(json_file)
    predicted_label = labels[str(ind.item())]
    return predicted_label
