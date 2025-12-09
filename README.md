<<<<<<< HEAD
# Deepfake Detection App

A Python web application for AI-generated image detection. It uses a primary CLIP-based model and falls back to a secondary model if confidence is low.

## Features

- **Primary Detector**: Uses [ClipBased-SyntheticImageDetection](https://github.com/grip-unina/ClipBased-SyntheticImageDetection) (CLIP + Linear Probe).
- **Fallback Detector**: Uses a custom Keras model (`V3_103.h5`) when primary confidence < 0.8.
- **API**: FastAPI providing a REST endpoint for image detection.
- **UI**: Simple HTML/JS interface for testing.

## Setup & Running Locally

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the App**:
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Open in Browser**:
   Go to [http://localhost:8000](http://localhost:8000).

## Configuration

Environment variables can be set in `.env` or passed to the process:

- `PRIMARY_CONFIDENCE_THRESHOLD`: Threshold for fallback (default 0.8).
- `DEVICE`: `cpu` or `cuda` (default `cpu`).
- `PORT`: Web server port (default 8000).

## Docker

Build and run:
```bash
docker build -t deepfake-detector .
docker run -p 8000:8000 deepfake-detector
```
=======
# deepfake_detection

The DeepFaker application is an AI-driven platform designed to explore both the creation and detection of deepfake content. The project aims to build a complete pipeline that covers data collection and preprocessing, model training, evaluation, and deployment. It will enable the generation of realistic synthetic media while also integrating detection mechanisms to identify manipulated content, supporting research, ethical use, and responsible innovation.

Key goals include:

Collecting and cleaning diverse multimedia datasets.

Developing and training deep learning models for both generation and detection.

Evaluating model accuracy, performance, and error handling.

Deploying the solution with a user-friendly interface and scalable infrastructure.

Ensuring transparency, security, and alignment with ethical AI practices.

This project will serve as a proof-of-concept for building robust deepfake systems while highlighting safeguards against misuse.
>>>>>>> 2c200280ce4b17775169935ddc134485f0dddcb8
