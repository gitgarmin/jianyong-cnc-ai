"""B08 RAG 检索服务 — 基于 ChromaDB + sentence-transformers 的知识库检索。

覆盖 PRD §4.1.2 五个知识库领域：材料库、故障库、工艺库、报警码库、切削参数。
支持文档分块摄入（带 overlap）和相似度检索（带阈值过滤）。
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

import chromadb


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RAGChunk:
    """单个文档分块，用于摄入到 ChromaDB。"""

    id: str
    text: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class RAGResult:
    """检索结果条目，包含相似度距离。"""

    doc_id: str
    text: str
    metadata: dict[str, Any]
    distance: float


# ---------------------------------------------------------------------------
# RAG Service
# ---------------------------------------------------------------------------


class RAGService:
    """基于 ChromaDB 的 RAG 检索服务。

    参数：
        collection_name: ChromaDB 集合名称。
        chunk_size: 文本分块目标长度（字符数）。
        chunk_overlap: 相邻分块的重叠字符数。
    """

    def __init__(
        self,
        collection_name: str = "cnc_knowledge",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ) -> None:
        self.chunk_size: int = chunk_size
        self.chunk_overlap: int = chunk_overlap

        client = chromadb.Client()
        self._collection: Any = client.get_or_create_collection(
            name=collection_name,
        )

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    def ingest_document(
        self,
        doc_id: str,
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """摄入单个文档：分块后写入 ChromaDB。

        空白文档被静默忽略。
        """
        if not text or not text.strip():
            return

        metadata = metadata or {}
        chunks = self._chunk_text(text)

        chunk_ids: list[str] = []
        chunk_documents: list[str] = []
        chunk_metadatas: list[dict[str, Any]] = []

        for i, chunk_text in enumerate(chunks):
            chunk_ids.append(f"{doc_id}_chunk_{i}")
            chunk_documents.append(chunk_text)
            chunk_meta = {
                **metadata,
                "parent_doc_id": doc_id,
                "chunk_index": i,
            }
            chunk_metadatas.append(chunk_meta)

        self._collection.add(
            ids=chunk_ids,
            documents=chunk_documents,
            metadatas=chunk_metadatas,
        )

    def ingest_knowledge_base(self, documents: list[dict[str, Any]]) -> None:
        """批量摄入知识库文档列表。

        每个 dict 需包含 id、text、metadata 字段。
        """
        for doc in documents:
            self.ingest_document(
                doc_id=doc["id"],
                text=doc["text"],
                metadata=doc.get("metadata", {}),
            )

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 5,
        distance_threshold: float | None = None,
    ) -> list[RAGResult]:
        """相似度检索，返回按距离升序排列的结果列表。

        参数：
            query: 查询文本。
            top_k: 最大返回条数。
            distance_threshold: 距离阈值，仅返回 distance < threshold 的结果。
        """
        result = self._collection.query(
            query_texts=[query],
            n_results=top_k,
        )

        # ChromaDB 返回的字段都是嵌套列表（外层按 query，内层按结果）
        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        results: list[RAGResult] = []
        for i in range(len(ids)):
            distance = distances[i]

            if distance_threshold is not None and distance >= distance_threshold:
                continue

            results.append(
                RAGResult(
                    doc_id=ids[i],
                    text=documents[i],
                    metadata=metadatas[i],
                    distance=distance,
                )
            )

        # 按距离升序排列（距离越小越相关）
        results.sort(key=lambda r: r.distance)

        return results

    # ------------------------------------------------------------------
    # Text chunking
    # ------------------------------------------------------------------

    def _chunk_text(self, text: str) -> list[str]:
        """将文本拆分为带 overlap 的分块。

        优先在句子边界（中文句号、换行等）处断开。
        """
        if len(text) <= self.chunk_size:
            return [text]

        sentences = self._split_sentences(text)
        chunks: list[str] = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                    # 从当前 chunk 尾部取 overlap 文本作为下一个 chunk 的开头
                    overlap_text = current_chunk[-self.chunk_overlap:]
                    current_chunk = overlap_text + sentence
                else:
                    # 单个句子超过 chunk_size，硬切
                    current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def _split_sentences(self, text: str) -> list[str]:
        """按句子边界拆分文本。

        分隔符包括中文标点和换行符。
        """
        import re

        # 在中文句号、问号、叹号、分号、换行后拆分
        parts = re.split(r"((?:。|！|？|；|\n))", text)
        sentences: list[str] = []

        i = 0
        while i < len(parts):
            sentence = parts[i]
            # 将标点符号合并到前一个片段
            if i + 1 < len(parts) and parts[i + 1] in ("。", "！", "？", "；", "\n"):
                sentence += parts[i + 1]
                i += 2
            else:
                i += 1
            if sentence:
                sentences.append(sentence)

        return sentences
