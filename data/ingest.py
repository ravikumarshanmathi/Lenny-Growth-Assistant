import os
import glob
from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://lenny:lenny_dev_password@localhost:5432/lenny_growth_assistant")
# Use synchronous psycopg2 driver for this standalone ingestion script
SYNC_DB_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

engine = create_engine(SYNC_DB_URL)
SessionLocal = sessionmaker(bind=engine)

def chunk_text(text_content, max_words=400, overlap=50):
    """Implements semantic chunking with a sliding window of words."""
    words = text_content.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i:i + max_words]
        chunks.append(" ".join(chunk_words))
        i += max_words - overlap
    return chunks

def ingest_transcripts():
    logger.info("Initializing embedding model (all-MiniLM-L6-v2)...")
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
    except Exception as e:
        logger.error(f"Failed to load embedding model: {e}")
        return

    logger.info("Connecting to the database...")
    with SessionLocal() as session:
        try:
            # Ensure pgvector extension is enabled
            session.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            session.commit()
            logger.info("Checked/created pgvector extension.")

            # Ensure tables exist
            import sys
            backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
            sys.path.append(backend_path)
            
            from app.db.models import Base, TranscriptChunk
            Base.metadata.create_all(bind=engine)
            logger.info("Verified database schema.")

            # Setup data directories to scan: agent_transcripts, data/transcripts, data/raw_transcripts
            root_dir = os.path.dirname(os.path.dirname(__file__))
            candidate_dirs = [
                os.path.join(root_dir, 'agent_transcripts'),
                os.path.join(root_dir, 'data', 'transcripts'),
                os.path.join(root_dir, 'data', 'raw_transcripts'),
            ]
            
            seen_files = set()
            files_to_process = []
            for d in candidate_dirs:
                if os.path.exists(d):
                    for ext in ('*.txt', '*.md'):
                        for f in glob.glob(os.path.join(d, ext)):
                            bname = os.path.basename(f)
                            if bname not in seen_files:
                                seen_files.add(bname)
                                files_to_process.append(f)

            if not files_to_process:
                logger.warning(f"No transcript files found in candidate directories: {candidate_dirs}.")
                return

            for filepath in files_to_process:
                logger.info(f"Processing file: {filepath}")
                filename = os.path.basename(filepath)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract Episode and Guest headers if present
                episode_title = os.path.splitext(filename)[0].replace('_', ' ').title()
                guest_name = None

                for line in content.splitlines():
                    if line.startswith("Episode:"):
                        episode_title = line.replace("Episode:", "").strip()
                    elif line.startswith("Guest:"):
                        guest_name = line.replace("Guest:", "").strip()

                if not guest_name:
                    if "elena_verna" in filename.lower() or "elena verna" in content.lower():
                        guest_name = "Elena Verna"
                    elif "brian_balfour" in filename.lower() or "brian balfour" in content.lower() or "balfour" in filename.lower():
                        guest_name = "Brian Balfour"
                    elif "lenny" in filename.lower():
                        guest_name = "Lenny Rachitsky"
                
                # Check if chunks for this episode or file already exist in DB
                existing_count = session.execute(
                    text("SELECT count(*) FROM transcript_chunks WHERE metadata_json->>'file_name' = :fname"),
                    {"fname": filename}
                ).scalar()
                
                if existing_count and existing_count > 0:
                    logger.info(f"File {filename} is already indexed ({existing_count} chunks exist). Skipping duplicate ingestion.")
                    continue

                chunks = chunk_text(content, max_words=400, overlap=50)
                logger.info(f"Generated {len(chunks)} chunks for {filename} (Guest: {guest_name}, Title: {episode_title}).")
                
                # Compute embeddings in batch
                embeddings = model.encode(chunks, show_progress_bar=False)
                
                db_chunks = []
                for idx, (chunk_text_data, emb) in enumerate(zip(chunks, embeddings)):
                    chunk = TranscriptChunk(
                        episode_title=episode_title,
                        guest_name=guest_name,
                        source_url=None,
                        chunk_content=chunk_text_data,
                        chunk_index=str(idx),
                        embedding=emb.tolist(),
                        metadata_json={"file_name": filename, "chunk_order": idx, "guest": guest_name, "episode_metadata": {}}
                    )
                    db_chunks.append(chunk)
                
                session.add_all(db_chunks)
                session.commit()
                logger.info(f"Successfully inserted {len(db_chunks)} chunks for {filename} into the database.")
        
        except Exception as e:
            logger.error(f"Database error during ingestion: {e}")
            session.rollback()

if __name__ == "__main__":
    ingest_transcripts()
