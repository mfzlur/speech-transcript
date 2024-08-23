# Speech-to-Text Flask App

## Overview

This is a simple Flask application that converts speech to text. The app supports multiple languages and is deployed using Docker on Google Cloud.

## Features

- **Speech-to-Text Conversion**: Converts audio files to text.
- **Language Detection**: Detects Language of audio and converts its transcripts into english.
- **Supported Languages**: A variety of languages are supported for transcription.
- **Dockerized Deployment**: Deployed using Docker for easy management and scalability.
- **Google Cloud Deployment**: Hosted on Google Cloud Platform (GCP) for reliable and scalable access.

## Supported Languages

The app supports the following languages:

- **Bulgarian**: `bg`
- **Catalan**: `ca`
- **Chinese (Mandarin, Simplified)**: `zh`, `zh-CN`, `zh-Hans`
- **Chinese (Mandarin, Traditional)**: `zh-TW`, `zh-Hant`
- **Czech**: `cs`
- **Danish**: `da`, `da-DK`
- **Dutch**: `nl`
- **English**: `en`, `en-US`, `en-AU`, `en-GB`, `en-NZ`, `en-IN`
- **Estonian**: `et`
- **Finnish**: `fi`
- **Flemish**: `nl-BE`
- **French**: `fr`, `fr-CA`
- **German**: `de`
- **German (Switzerland)**: `de-CH`
- **Greek**: `el`
- **Hindi**: `hi`
- **Hungarian**: `hu`
- **Indonesian**: `id`
- **Italian**: `it`
- **Japanese**: `ja`
- **Korean**: `ko`, `ko-KR`
- **Latvian**: `lv`
- **Lithuanian**: `lt`
- **Malay**: `ms`
- **Multilingual (Spanish + English)**: `multi`
- **Norwegian**: `no`
- **Polish**: `pl`
- **Portuguese**: `pt`, `pt-BR`
- **Romanian**: `ro`
- **Russian**: `ru`
- **Slovak**: `sk`
- **Spanish**: `es`, `es-419`
- **Swedish**: `sv`, `sv-SE`
- **Thai**: `th`, `th-TH`
- **Turkish**: `tr`
- **Ukrainian**: `uk`
- **Vietnamese**: `vi`


## Tools / APIs Used

- **Deepgram**: For speech-to-text conversion.
- **Google Translate**: For text translation.
- **pydub**: For handling audio and video files.
- **Google OAuth2**: For authentication.
