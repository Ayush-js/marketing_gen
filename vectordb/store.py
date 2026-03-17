# =============================================
#   vectordb/store.py
#   ChromaDB integration for storing &
#   retrieving past marketing content
# =============================================

import os
import uuid
import chromadb
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class ContentVectorStore:
    """
    Manages ChromaDB storage for generated marketing content.
    Enables semantic similarity search across past generations
    to ensure brand consistency.
    """

    def __init__(self):
        db_path = os.getenv("CHROMA_DB_PATH", "./vectordb/chroma_store")
        os.makedirs(db_path, exist_ok=True)

        self.client = chromadb.PersistentClient(path=db_path)

        # One collection per content type
        self.collections = {
            "Ad Copy":             self._get_or_create("ad_copy"),
            "Social Media Posts":  self._get_or_create("social_media"),
            "Email Campaign":      self._get_or_create("email_campaign"),
            "Product Description": self._get_or_create("product_description"),
        }

    def _get_or_create(self, name: str):
        """Get existing collection or create a new one."""
        return self.client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},
        )

    def save_content(
        self,
        content_type: str,
        topic: str,
        audience: str,
        tone: str,
        platform: str,
        generated_content: str,
    ) -> str:
        """
        Save generated content to the vector store.

        Returns:
            doc_id: The unique ID of the saved document
        """
        collection = self.collections.get(content_type)
        if not collection:
            raise ValueError(f"Unknown content type: {content_type}")

        doc_id    = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Document text used for embedding
        document_text = f"Topic: {topic}\nAudience: {audience}\n\n{generated_content}"

        collection.add(
            ids=[doc_id],
            documents=[document_text],
            metadatas=[{
                "topic":        topic,
                "audience":     audience,
                "tone":         tone,
                "platform":     platform,
                "timestamp":    timestamp,
                "content_type": content_type,
            }],
        )
        return doc_id

    def find_similar(
        self,
        content_type: str,
        topic: str,
        audience: str,
        n_results: int = 2,
    ) -> str:
        """
        Find past content similar to the current request.

        Returns:
            Formatted string of similar past content, or empty string
        """
        collection = self.collections.get(content_type)
        if not collection:
            return ""

        # Need at least 1 doc to query
        if collection.count() == 0:
            return ""

        query_text = f"Topic: {topic}\nAudience: {audience}"

        results = collection.query(
            query_texts=[query_text],
            n_results=min(n_results, collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        if not results["documents"] or not results["documents"][0]:
            return ""

        similar_items = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            similarity = round((1 - dist) * 100, 1)
            if similarity > 30:  # Only include if reasonably similar
                similar_items.append(
                    f"[{meta['content_type']} | Tone: {meta['tone']} | "
                    f"Platform: {meta['platform']} | Similarity: {similarity}%]\n{doc}"
                )

        return "\n\n---\n\n".join(similar_items)

    def get_history(self, content_type: str = None, limit: int = 20) -> list:
        """
        Retrieve content history for the sidebar.

        Returns:
            List of metadata dicts with preview
        """
        history = []

        target_collections = (
            {content_type: self.collections[content_type]}
            if content_type and content_type in self.collections
            else self.collections
        )

        for ctype, collection in target_collections.items():
            if collection.count() == 0:
                continue

            results = collection.get(
                limit=limit,
                include=["documents", "metadatas"],
            )

            for doc, meta in zip(results["documents"], results["metadatas"]):
                history.append({
                    "content_type": ctype,
                    "topic":        meta.get("topic", ""),
                    "tone":         meta.get("tone", ""),
                    "platform":     meta.get("platform", ""),
                    "timestamp":    meta.get("timestamp", ""),
                    "preview":      doc[:120] + "..." if len(doc) > 120 else doc,
                    "full_content": doc,
                })

        # Sort by timestamp descending
        history.sort(key=lambda x: x["timestamp"], reverse=True)
        return history[:limit]

    def delete_all(self, content_type: str = None) -> int:
        """Delete all stored content. Returns count deleted."""
        total = 0
        targets = (
            {content_type: self.collections[content_type]}
            if content_type
            else self.collections
        )
        for name, collection in targets.items():
            count = collection.count()
            if count > 0:
                all_ids = collection.get()["ids"]
                collection.delete(ids=all_ids)
                total += count
        return total