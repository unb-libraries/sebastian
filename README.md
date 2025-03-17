# sebastian
<p align="center">
<img src="assets/image.webp" alt="drawing" width="400"/>
</p>

## Introduction
Sebastian transcribes audio files to text. It leverages the [whisperX](https://github.com/m-bain/whisperX) library, a speech-to-text library that extends Whisper ASR model [originally developed by OpenAI](https://github.com/openai/whisper).

Both time-alignment and diarization (unique speaker identification) are supported.

## Documentation
Some stub documentation is currently available [in the documentation folder](./documentation/README.md "Project Documentation").

## Pre-requisites
- Python 3.8+
- [Poetry](https://python-poetry.org/docs/)
- [Nvidia drivers](https://www.nvidia.com/Download/index.aspx)
- [CUDA](https://developer.nvidia.com/cuda-downloads)

## CLI Commands
### `api:start`

Start the API server:

`poetry run api:start`

## Client Request Format

The client should send a POST request with multipart form data containing an audio file. The form data can contain the following fields:

### Standard Transcriptions

- **file**: The audio file to be transcribed. This is a required field.
- **model**: The whisper model to be used for transcription. Default is 'large-v3-turbo'.
- **device**: The device to be used for computation. Default is 'cuda'.
- **compute_type**: The precision of computation to be used. Default is 'float16'. int8 is also supported but not recommended.
- **batch_size**: The batch size for processing. Default is '16'.
- **language**: The language of the audio file. Default is 'en'.

### Time-Alignment
The transcription can also be time-aligned. The form data can contain the following additional fields:
- **align**: A boolean flag to enable or disable alignment. Default is 'false'.

### Diarization
The transcription can also be diarized to identify unique speakers in the transcription (SPEAKER-1, SPEAKER-2, etc.). The form data can contain the following additional fields:
- **diarize**: A boolean flag to enable or disable diarization. Default is 'false'.
- **min_speakers**: The minimum number of speakers to identify. Default is '1'.
- **max_speakers**: The maximum number of speakers to identify. Default is '4'.

### Debugging
- **debug**: A boolean flag to enable or disable debug mode. Default is 'false'.

The API will return a JSON response with the transcribed text data

## Convenience Commands
Other commands are available for convenience:

### `transcribe`
The input file path should be an absolute path to an audio file you wish to summarize.

`poetry run transcribe test.mp4`

## License
- In line with our 'open' ethos, UNB Libraries makes its applications and workflows freely available to everyone whenever possible.
- As a result, the contents of this repository [unb-libraries/sebastian] are licensed under the [MIT License](http://opensource.org/licenses/mit-license.html). This license explicitly excludes:
   - Any content that remains the exclusive property of its author(s).
   - The UNB logo and any associated visual identity assets remain the exclusive property of the University of New Brunswick.
