# Hugging Face Docker Space (free CPU basic: 2 vCPU, 16 GB RAM). Built by Hugging Face from this folder.
FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg libsndfile1 && rm -rf /var/lib/apt/lists/*

# Spaces run the container as user 1000
RUN useradd -m -u 1000 user
ENV HOME=/home/user HF_HOME=/home/user/.cache/huggingface PYTHONUNBUFFERED=1 OMP_NUM_THREADS=2
WORKDIR /home/user/app

COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir torch==2.6.0+cpu torchaudio==2.6.0+cpu --index-url https://download.pytorch.org/whl/cpu \
 && pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

COPY --chown=user . .
USER user
# bake the public ECAPA model into the image (the gated pyannote VAD model is fetched at start-up with HF_TOKEN)
RUN python -c "from speechbrain.inference.speaker import EncoderClassifier as E; E.from_hparams(source='speechbrain/spkrec-ecapa-voxceleb', savedir='checkpoints/ecapa')"

EXPOSE 7860
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
