"""
ChromaDB Configuration for Opportunity Bot

Switch between local and Xeon Gold ChromaDB easily.
"""

import os
import chromadb
from pathlib import Path

# Configuration
USE_XEON_CHROMADB = os.getenv('USE_XEON_CHROMADB', 'true').lower() == 'true'
XEON_CHROMADB_HOST = os.getenv('XEON_CHROMADB_HOST', '10.0.0.87')
XEON_CHROMADB_PORT = int(os.getenv('XEON_CHROMADB_PORT', '8000'))

# Local fallback
WORKSPACE = Path(__file__).parent.absolute()
LOCAL_CHROMA_PATH = WORKSPACE / "data" / "chroma_db"


def get_chroma_client():
    """
    Get ChromaDB client - automatically uses Xeon if available, falls back to local.

    Returns:
        chromadb.Client: Connected ChromaDB client
    """
    if USE_XEON_CHROMADB:
        try:
            print(f"🚀 Connecting to Xeon Gold ChromaDB at {XEON_CHROMADB_HOST}:{XEON_CHROMADB_PORT}...")
            print("   → Using 192GB RAM disk storage")
            print("   → Expected: 10-100x faster vector search!")

            client = chromadb.HttpClient(
                host=XEON_CHROMADB_HOST,
                port=XEON_CHROMADB_PORT
            )

            # Test connection
            client.heartbeat()
            print("   ✅ Connected to Xeon Gold ChromaDB (RAM disk)")
            return client

        except Exception as e:
            print(f"   ⚠️  Could not connect to Xeon ChromaDB: {e}")
            print(f"   → Falling back to local ChromaDB at {LOCAL_CHROMA_PATH}")
            LOCAL_CHROMA_PATH.mkdir(parents=True, exist_ok=True)
            return chromadb.PersistentClient(path=str(LOCAL_CHROMA_PATH))
    else:
        print(f"📁 Using local ChromaDB at {LOCAL_CHROMA_PATH}")
        LOCAL_CHROMA_PATH.mkdir(parents=True, exist_ok=True)
        return chromadb.PersistentClient(path=str(LOCAL_CHROMA_PATH))


def get_chroma_settings():
    """
    Get ChromaDB configuration settings.

    Returns:
        dict: Configuration settings
    """
    return {
        "use_xeon": USE_XEON_CHROMADB,
        "host": XEON_CHROMADB_HOST if USE_XEON_CHROMADB else "local",
        "port": XEON_CHROMADB_PORT if USE_XEON_CHROMADB else None,
        "path": None if USE_XEON_CHROMADB else str(LOCAL_CHROMA_PATH),
        "storage": "RAM disk (192GB)" if USE_XEON_CHROMADB else "Local SSD"
    }


# Quick usage:
# from config_chromadb import get_chroma_client
# client = get_chroma_client()
# collection = client.get_or_create_collection("opportunities")
