# Data Directory

This directory contains the raw transcript corpus and ingestion tooling.

## Structure

```
data/
├── transcripts/          # Raw transcript files (.txt, .md, .json)
│   └── .gitkeep
├── scripts/
│   └── ingest.py         # CLI ingestion script
└── README.md
```

## Transcript Format

Each transcript file should follow this naming convention:

```
{episode_id}_{guest_name}_{title_slug}.txt
```

Example: `ep_301_elena_verna_growth_loops.txt`

## Ingestion

```bash
# Ingest all transcripts from a directory
python data/scripts/ingest.py --dir data/transcripts/

# Ingest a single file
python data/scripts/ingest.py --file data/transcripts/ep_301_elena_verna_growth_loops.txt

# Re-index after embedding model change
python data/scripts/ingest.py --reindex
```
