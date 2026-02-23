# Winy

## Install with docker

1. Launch all containers
   ```bash
   cd resto
   docker compose up --build -d
   ```

2. Download mistral model with ollama
   ```bash
   cd resto/tools
   ./download_model.sh llama3.2
   ./download_model.sh mxbai-embed-large
   ```

3. Create vector collection and embeddings
   ```bash
   cd resto/tools
   source adp-rags/bin/activate
   python load_embeddings.py
   ```
