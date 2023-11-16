"""
TODO: Add docstring
"""
import torchvision.transforms as T
from PIL import Image


def preprocessing(image_path):
    image = Image.open(image_path).convert('RGB')
    transform = T.Compose([T.Resize((256, 256)),
                           T.ToTensor(),
                           T.Normalize(mean=[0.485, 0.456, 0.406],
                                       std=[0.229, 0.224, 0.225])
                           ])
    image = transform(image)
    image = image.unsqueeze(0)
    return image


async def infer(client, input):
    model_output = client.infer(model_name="object_detection", inputs=[input])
    return model_output.as_numpy('output0')
