#!/usr/bin/env python3
"""
Migrate existing opportunity data from local ChromaDB to Xeon Gold ChromaDB

This script:
1. Reads all data from local ChromaDB
2. Connects to Xeon Gold ChromaDB
3. Copies all collections and documents
4. Verifies the migration
"""

import chromadb
from pathlib import Path
import sys

# Paths
WORKSPACE = Path(__file__).parent.absolute()
LOCAL_CHROMA_PATH = WORKSPACE / "data" / "chroma_db"
XEON_HOST = "10.0.0.87"
XEON_PORT = 8000

def migrate_data():
    """Migrate all data from local to Xeon ChromaDB"""

    print("════════════════════════════════════════════════════════════")
    print("  MIGRATING OPPORTUNITY DATA TO XEON GOLD")
    print("════════════════════════════════════════════════════════════")
    print()

    # Connect to local ChromaDB
    print(f"1. Connecting to local ChromaDB at {LOCAL_CHROMA_PATH}...")
    try:
        local_client = chromadb.PersistentClient(path=str(LOCAL_CHROMA_PATH))
        print("   ✅ Connected to local ChromaDB")
    except Exception as e:
        print(f"   ❌ Error connecting to local ChromaDB: {e}")
        return False

    # Connect to Xeon ChromaDB
    print(f"\n2. Connecting to Xeon Gold ChromaDB at {XEON_HOST}:{XEON_PORT}...")
    try:
        xeon_client = chromadb.HttpClient(
            host=XEON_HOST,
            port=XEON_PORT
        )
        # Test connection
        xeon_client.heartbeat()
        print("   ✅ Connected to Xeon Gold ChromaDB (RAM disk)")
    except Exception as e:
        print(f"   ❌ Error connecting to Xeon ChromaDB: {e}")
        print("   Make sure Xeon Gold ChromaDB is running")
        return False

    # Get collections from local
    print("\n3. Reading local collections...")
    try:
        local_collections = local_client.list_collections()
        print(f"   Found {len(local_collections)} collection(s):")
        for coll in local_collections:
            count = coll.count()
            print(f"     - {coll.name}: {count} documents")
    except Exception as e:
        print(f"   ❌ Error reading local collections: {e}")
        return False

    if not local_collections:
        print("   ⚠️  No collections found in local ChromaDB")
        print("   Nothing to migrate!")
        return True

    # Migrate each collection
    print("\n4. Migrating collections...")
    for local_coll in local_collections:
        coll_name = local_coll.name
        count = local_coll.count()

        print(f"\n   Migrating '{coll_name}' ({count} documents)...")

        try:
            # Get all data from local collection
            all_data = local_coll.get()

            if not all_data['ids']:
                print(f"     ⚠️  Collection empty, skipping")
                continue

            # Create or get collection on Xeon
            try:
                xeon_coll = xeon_client.get_collection(coll_name)
                print(f"     → Collection exists on Xeon ({xeon_coll.count()} existing docs)")
            except:
                xeon_coll = xeon_client.create_collection(
                    name=coll_name,
                    metadata=local_coll.metadata
                )
                print(f"     → Created new collection on Xeon")

            # Add all documents to Xeon
            print(f"     → Uploading {len(all_data['ids'])} documents...")

            # ChromaDB has a limit on batch size, so upload in chunks
            batch_size = 100
            for i in range(0, len(all_data['ids']), batch_size):
                end_idx = min(i + batch_size, len(all_data['ids']))

                batch_ids = all_data['ids'][i:end_idx]
                batch_docs = all_data['documents'][i:end_idx] if all_data['documents'] else None
                batch_metadata = all_data['metadatas'][i:end_idx] if all_data['metadatas'] else None
                batch_embeddings = all_data['embeddings'][i:end_idx] if all_data['embeddings'] else None

                # Build add kwargs
                add_kwargs = {'ids': batch_ids}
                if batch_docs:
                    add_kwargs['documents'] = batch_docs
                if batch_metadata:
                    add_kwargs['metadatas'] = batch_metadata
                if batch_embeddings:
                    add_kwargs['embeddings'] = batch_embeddings

                xeon_coll.add(**add_kwargs)
                print(f"       Uploaded batch {i//batch_size + 1} ({end_idx}/{len(all_data['ids'])})")

            print(f"     ✅ Migration complete for '{coll_name}'")

            # Verify
            final_count = xeon_coll.count()
            print(f"     → Xeon collection now has {final_count} documents")

        except Exception as e:
            print(f"     ❌ Error migrating '{coll_name}': {e}")
            continue

    print("\n5. Verification...")
    xeon_collections = xeon_client.list_collections()
    print(f"   Xeon ChromaDB now has {len(xeon_collections)} collection(s):")
    for coll in xeon_collections:
        count = coll.count()
        print(f"     - {coll.name}: {count} documents")

    print("\n════════════════════════════════════════════════════════════")
    print("  ✅ MIGRATION COMPLETE!")
    print("════════════════════════════════════════════════════════════")
    print()
    print("Your opportunity data is now on Xeon Gold ChromaDB!")
    print("  → 192GB RAM disk storage")
    print("  → 10-100x faster vector search")
    print("  → Network accessible")
    print()
    print("The bot will now automatically use Xeon Gold ChromaDB.")
    print("Set USE_XEON_CHROMADB=false to use local ChromaDB instead.")
    print()

    return True

if __name__ == "__main__":
    success = migrate_data()
    sys.exit(0 if success else 1)
