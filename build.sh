#!/bin/bash

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🤖 Downloading Hugging Face model..."
python -c "from transformers import pipeline; pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')"

echo "✅ Build completed successfully."
echo "✅ Hugging Face model downloaded and cached."
