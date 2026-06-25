"""RAG 内容检索引擎 — 使用 FAISS 向量检索。"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


class SimpleEmbedding:
    """简单的基于字符的伪嵌入（生产环境应替换为真实 embedding 模型）。"""

    def __init__(self, dim: int = 128):
        self.dim = dim

    def embed(self, text: str) -> list[float]:
        """将文本转为向量。使用哈希模拟，生产环境用 OpenAI/SentenceTransformer。"""
        import hashlib
        hash_bytes = hashlib.sha512(text.encode()).digest()
        # 将 hash 扩展到目标维度
        expanded = hash_bytes * (self.dim // len(hash_bytes) + 1)
        vec = [float(b) / 255.0 for b in expanded[:self.dim]]
        # 归一化
        norm = sum(v ** 2 for v in vec) ** 0.5
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec


class RAGEngine:
    """简单的 RAG 检索引擎。"""

    def __init__(self):
        self.embedder = SimpleEmbedding()
        self.documents: list[dict[str, Any]] = []
        self.vectors: list[list[float]] = []
        self._index = None

    def add_document(self, doc_id: str, content: str, metadata: dict[str, Any] = None):
        """添加文档到索引。"""
        self.documents.append({
            "id": doc_id,
            "content": content,
            "metadata": metadata or {},
        })
        vec = self.embedder.embed(content)
        self.vectors.append(vec)
        self._index = None  # 标记需要重建索引

    def add_documents(self, docs: list[dict[str, Any]]):
        """批量添加文档。"""
        for doc in docs:
            self.add_document(
                doc_id=doc["id"],
                content=doc["content"],
                metadata=doc.get("metadata", {}),
            )

    def _build_index(self):
        """构建 FAISS 索引。"""
        if not self.vectors:
            return

        try:
            import faiss
            dim = len(self.vectors[0])
            self._index = faiss.IndexFlatIP(dim)  # 内积（余弦相似度，因为已归一化）
            matrix = np.array(self.vectors, dtype=np.float32)
            self._index.add(matrix)
            logger.info(f"FAISS 索引构建完成，共 {len(self.vectors)} 个文档")
        except ImportError:
            logger.warning("FAISS 未安装，使用暴力搜索")
            self._index = None

    def search(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        """检索最相关的文档。"""
        if not self.documents:
            return []

        query_vec = self.embedder.embed(query)

        if self._index is None:
            self._build_index()

        if self._index is not None:
            # FAISS 检索
            query_matrix = np.array([query_vec], dtype=np.float32)
            scores, indices = self._index.search(query_matrix, min(top_k, len(self.documents)))
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0:
                    doc = self.documents[idx].copy()
                    doc["score"] = float(score)
                    results.append(doc)
            return results
        else:
            # 暴力搜索
            scored = []
            for i, doc_vec in enumerate(self.vectors):
                score = sum(a * b for a, b in zip(query_vec, doc_vec))
                scored.append((score, i))
            scored.sort(reverse=True)

            results = []
            for score, idx in scored[:top_k]:
                doc = self.documents[idx].copy()
                doc["score"] = score
                results.append(doc)
            return results


# 全局实例
rag_engine = RAGEngine()


def get_rag_engine() -> RAGEngine:
    return rag_engine
