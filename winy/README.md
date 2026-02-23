# Winy

## Install with docker

1. Launch all containers
   ```bash
   cd winy
   docker compose up --build -d
   ```

2. Download mistral model with ollama
   ```bash
   cd winy/tools
   ./download_model.sh mistral
   ```

3. Create vector collection and embeddings
   ```bash
   cd winy/tools
   source adp-rags/bin/activate
   python create_embeddings.py
   ```

4. Create pg database for wine links
   ```bash
   cd winy/tools
   source adp-rags/bin/activate
   python create_db.py
   ```
