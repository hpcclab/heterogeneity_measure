"""
TODO: Add docstring
"""
import tritonclient.grpc as grpcclient
from transformers import Wav2Vec2Processor
import soundfile as sf
import torch


def preprocessing(audio_path):
    """
    TODO: Add docstring
    """
    audio_input, sample_rate = sf.read(audio_path)
    processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
    input_data = processor(audio_input, sampling_rate=sample_rate, return_tensors="pt")
    input_data = input_data.input_values

    return input_data


async def infer(client, input):
    """
    TODO: Add docstring
    """
    model_output = client.infer(model_name="speech_recognition", inputs=[input])
    return model_output.as_numpy('output')


def postprocessing(model_output):
    processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
    model_output = torch.from_numpy(model_output)
    predictions = torch.argmax(model_output, dim=-1)
    transcription = processor.decode(predictions[0])
    return transcription


if __name__ == '__main__':
    IP = "3.138.137.51"
    PORT = "8000"
    client = httpclient.InferenceServerClient(url=f"{IP}:{PORT}")
    input_data = preprocessing('./client/sample_audio.wav')
    model_output = infer(client, input_data)
    transcription = postprocessing(model_output)
