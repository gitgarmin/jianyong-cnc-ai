"""B08 RAG 检索服务测试 — TDD RED 阶段

覆盖 PRD §4.1.2 五个知识库领域（材料/故障/工艺/报警码/切削参数）。
测试场景：空库检索、文档分块、相似度阈值。

所有 ChromaDB 调用通过 mock 隔离，不依赖运行中的向量数据库实例。
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from app.services.rag_service import (
    RAGChunk,
    RAGResult,
    RAGService,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_chroma_collection():
    """返回一个 mock 的 ChromaDB Collection 对象。

    - query() 默认返回空结果（模拟空库）
    - add() 可追踪调用参数
    - count() 默认返回 0
    """
    collection = MagicMock()
    collection.query.return_value = {
        "ids": [[]],
        "documents": [[]],
        "metadatas": [[]],
        "distances": [[]],
    }
    collection.count.return_value = 0
    collection.add.return_value = None
    collection.name = "test_knowledge"
    return collection


@pytest.fixture()
def rag_service(mock_chroma_collection: MagicMock) -> RAGService:
    """返回使用 mock collection 的 RAGService 实例。"""
    with patch("chromadb.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_chroma_collection
        mock_client_cls.return_value = mock_client

        service = RAGService(
            collection_name="test_knowledge",
            chunk_size=200,
            chunk_overlap=50,
        )
        # 保留 mock 引用以便测试中访问
        service._collection = mock_chroma_collection
        yield service


@pytest.fixture()
def sample_document() -> str:
    """模拟一份材料库文档（PRD §4.1.2 材料库）。"""
    return (
        "45#钢（优质碳素结构钢）\n\n"
        "硬度：HRC 20-25（调质态）\n"
        "推荐切削速度：80-120 m/min（硬质合金刀具）\n"
        "进给量：0.15-0.30 mm/r（粗车）\n"
        "切削深度：1.5-4.0 mm（单刀）\n"
        "冷却建议：5%-8% 乳化液，流量 ≥ 20 L/min\n\n"
        "加工注意事项：\n"
        "1. 粗车时优先保证断屑，进给量不宜过小\n"
        "2. 精车时切削速度取上限，进给量 0.08-0.12 mm/r\n"
        "3. 钻孔时建议使用内冷却钻头，排屑顺畅\n"
        "4. 攻丝时使用含硫切削液，降低丝锥磨损\n"
        "5. 热处理后工件硬度升高，需降低切削速度 20%-30%\n"
    )


@pytest.fixture()
def knowledge_documents() -> list[dict[str, Any]]:
    """模拟多个知识库文档，覆盖 PRD §4.1.2 五个领域。"""
    return [
        {
            "id": "mat_001",
            "text": "45#钢切削参数：切削速度80-120m/min，进给0.15-0.30mm/r",
            "metadata": {"source": "材料库", "category": "碳钢"},
        },
        {
            "id": "fault_001",
            "text": "振纹故障诊断：刀杆悬伸过长导致工件表面出现规则波纹",
            "metadata": {"source": "故障库", "category": "振纹"},
        },
        {
            "id": "process_001",
            "text": "外圆粗车工艺：推荐使用CNMG120408刀片，切深2-4mm",
            "metadata": {"source": "工艺库", "category": "车削"},
        },
        {
            "id": "alarm_001",
            "text": "FANUC PS0001报警：程序格式错误，检查G代码语法",
            "metadata": {"source": "报警码库", "category": "FANUC"},
        },
        {
            "id": "param_001",
            "text": "304不锈钢切削参数：切削速度60-90m/min，进给0.10-0.25mm/r",
            "metadata": {"source": "切削参数", "category": "不锈钢"},
        },
    ]


# ===========================================================================
# TestRAGIngestion — 文档摄入
# ===========================================================================


class TestRAGIngestion:
    """文档摄入测试（TDD 驱动 RAGService.ingest_document 实现）。"""

    def test_ingest_single_document(
        self,
        rag_service: RAGService,
        mock_chroma_collection: MagicMock,
        sample_document: str,
    ):
        """单文档摄入后 collection.add 被调用，且文档内容被正确传递。"""
        rag_service.ingest_document(
            doc_id="mat_45steel",
            text=sample_document,
            metadata={"source": "材料库", "category": "碳钢"},
        )

        mock_chroma_collection.add.assert_called_once()
        call_kwargs = mock_chroma_collection.add.call_args
        # ids 参数是列表
        assert len(call_kwargs.kwargs["ids"]) >= 1
        # documents 参数包含文档文本
        assert len(call_kwargs.kwargs["documents"]) >= 1

    def test_ingest_multiple_documents(
        self,
        rag_service: RAGService,
        mock_chroma_collection: MagicMock,
        knowledge_documents: list[dict[str, Any]],
    ):
        """批量摄入多个文档，每个文档对应独立的 chunk。"""
        for doc in knowledge_documents:
            rag_service.ingest_document(
                doc_id=doc["id"],
                text=doc["text"],
                metadata=doc["metadata"],
            )

        assert mock_chroma_collection.add.call_count == len(knowledge_documents)

    def test_document_chunking(
        self,
        rag_service: RAGService,
        mock_chroma_collection: MagicMock,
        sample_document: str,
    ):
        """长文档按 chunk_size 正确分块，生成多个 chunk。"""
        # sample_document 约 300+ 字符，chunk_size=200，应产生至少 2 个 chunk
        rag_service.ingest_document(
            doc_id="mat_45steel",
            text=sample_document,
            metadata={"source": "材料库"},
        )

        call_kwargs = mock_chroma_collection.add.call_args
        chunks = call_kwargs.kwargs["documents"]
        chunk_ids = call_kwargs.kwargs["ids"]

        # 应产生多个 chunk（文档长度 > chunk_size）
        assert len(chunks) >= 2, (
            f"Expected >= 2 chunks for {len(sample_document)} chars "
            f"with chunk_size=200, got {len(chunks)}"
        )
        # chunk 数量与 id 数量一致
        assert len(chunks) == len(chunk_ids)
        # 每个 chunk 的长度不超过 chunk_size + 容差（sentence boundary 可能略超）
        for chunk in chunks:
            assert len(chunk) <= rag_service.chunk_size + 50

    def test_chunk_overlap(
        self,
        rag_service: RAGService,
        mock_chroma_collection: MagicMock,
    ):
        """分块时相邻 chunk 之间存在 overlap 文本。"""
        # 构造足够长的文本以产生至少 3 个 chunk
        long_text = "这是一段关于数控加工的测试文本。" * 50  # ~650 字符

        rag_service.ingest_document(
            doc_id="test_overlap",
            text=long_text,
            metadata={"source": "测试"},
        )

        call_kwargs = mock_chroma_collection.add.call_args
        chunks = call_kwargs.kwargs["documents"]

        if len(chunks) >= 2:
            # 验证第一个 chunk 的尾部出现在第二个 chunk 中（overlap 存在）
            # 取第一个 chunk 最后 overlap 个字符的子串
            overlap_size = rag_service.chunk_overlap
            first_tail = chunks[0][-overlap_size:]
            assert first_tail in chunks[1], (
                f"Expected overlap of {overlap_size} chars between chunks, "
                "but first chunk tail not found in second chunk"
            )

    def test_ingest_with_metadata(
        self,
        rag_service: RAGService,
        mock_chroma_collection: MagicMock,
    ):
        """摄入时携带的 metadata 被正确传递到每个 chunk。"""
        metadata = {"source": "故障库", "category": "烧刀", "machine": "FANUC 0i-TF"}

        rag_service.ingest_document(
            doc_id="fault_burn",
            text="烧刀故障：切削速度过高或冷却不足导致刀尖温度超限",
            metadata=metadata,
        )

        call_kwargs = mock_chroma_collection.add.call_args
        metadatas = call_kwargs.kwargs["metadatas"]

        # 每个 chunk 都携带了元数据
        assert len(metadatas) >= 1
        for meta in metadatas:
            assert meta["source"] == "故障库"
            assert meta["category"] == "烧刀"
            assert meta["machine"] == "FANUC 0i-TF"
            # 元数据中应包含原始文档 id
            assert "parent_doc_id" in meta

    def test_ingest_empty_document_rejected(
        self,
        rag_service: RAGService,
        mock_chroma_collection: MagicMock,
    ):
        """空文档或纯空白文档被拒绝，不调用 collection.add。"""
        rag_service.ingest_document(
            doc_id="empty_doc",
            text="",
            metadata={"source": "测试"},
        )

        mock_chroma_collection.add.assert_not_called()

        # 纯空白也应被拒绝
        rag_service.ingest_document(
            doc_id="whitespace_doc",
            text="   \n\t  ",
            metadata={"source": "测试"},
        )

        mock_chroma_collection.add.assert_not_called()


# ===========================================================================
# TestRAGRetrieval — 相似度检索
# ===========================================================================


class TestRAGRetrieval:
    """相似度检索测试（TDD 驱动 RAGService.search 实现）。"""

    def test_search_empty_collection_returns_empty(
        self,
        rag_service: RAGService,
        mock_chroma_collection: MagicMock,
    ):
        """核心场景：空库检索返回空列表，不抛异常。"""
        mock_chroma_collection.query.return_value = {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

        results = rag_service.search(query="45#钢切削参数", top_k=5)

        assert results == []
        mock_chroma_collection.query.assert_called_once()

    def test_search_returns_relevant_results(
        self,
        rag_service: RAGService,
        mock_chroma_collection: MagicMock,
    ):
        """摄入后检索返回相关结果，结果结构符合 RAGResult。"""
        mock_chroma_collection.query.return_value = {
            "ids": [["mat_001_chunk_0"]],
            "documents": [["45#钢切削参数：切削速度80-120m/min"]],
            "metadatas": [[{"source": "材料库", "category": "碳钢"}]],
            "distances": [[0.25]],
        }

        results = rag_service.search(query="45#钢切削参数", top_k=5)

        assert len(results) == 1
        result = results[0]
        assert isinstance(result, RAGResult)
        assert "45#钢" in result.text
        assert result.doc_id == "mat_001_chunk_0"
        assert result.metadata["source"] == "材料库"
        assert result.distance == 0.25

    def test_similarity_threshold_filter(
        self,
        rag_service: RAGService,
        mock_chroma_collection: MagicMock,
    ):
        """核心场景：低于阈值的结果被过滤，只返回高相关度结果。"""
        # ChromaDB 返回 3 个结果，距离越小越相似
        # distance 0.1 = 高相似度，0.5 = 中等，0.9 = 低相似度
        mock_chroma_collection.query.return_value = {
            "ids": [["chunk_high", "chunk_mid", "chunk_low"]],
            "documents": [
                [
                    "45#钢切削速度80-120m/min",
                    "铝合金6061加工参数",
                    "这是一段不相关的内容",
                ]
            ],
            "metadatas": [
                [
                    {"source": "材料库"},
                    {"source": "材料库"},
                    {"source": "其他"},
                ]
            ],
            "distances": [[0.1, 0.5, 0.9]],
        }

        # 使用阈值 0.4（距离 < 0.4 的保留）
        results = rag_service.search(
            query="45#钢切削参数",
            top_k=5,
            distance_threshold=0.4,
        )

        # 只有第一个结果（distance=0.1）通过阈值
        assert len(results) == 1
        assert results[0].doc_id == "chunk_high"
        assert results[0].distance == 0.1

    def test_search_with_top_k(
        self,
        rag_service: RAGService,
        mock_chroma_collection: MagicMock,
    ):
        """返回结果数量受 top_k 约束，传递给 ChromaDB 的 n_results 正确。"""
        mock_chroma_collection.query.return_value = {
            "ids": [["c1", "c2", "c3"]],
            "documents": [["doc1", "doc2", "doc3"]],
            "metadatas": [[{"source": "s"}, {"source": "s"}, {"source": "s"}]],
            "distances": [[0.1, 0.2, 0.3]],
        }

        rag_service.search(query="测试查询", top_k=3)

        # 验证传递给 ChromaDB 的 n_results 参数
        call_kwargs = mock_chroma_collection.query.call_args
        assert call_kwargs.kwargs.get("n_results") == 3 or (
            call_kwargs.args and call_kwargs.args[1] == 3
        )

    def test_search_returns_source_metadata(
        self,
        rag_service: RAGService,
        mock_chroma_collection: MagicMock,
    ):
        """结果包含完整的 source/category 元数据。"""
        mock_chroma_collection.query.return_value = {
            "ids": [["alarm_fanuc_001"]],
            "documents": [["FANUC PS0001 报警：程序格式错误"]],
            "metadatas": [
                [{"source": "报警码库", "category": "FANUC", "parent_doc_id": "alarm_001"}]
            ],
            "distances": [[0.15]],
        }

        results = rag_service.search(query="FANUC 报警 PS0001", top_k=5)

        assert len(results) == 1
        meta = results[0].metadata
        assert meta["source"] == "报警码库"
        assert meta["category"] == "FANUC"
        assert meta["parent_doc_id"] == "alarm_001"

    def test_search_no_match_above_threshold(
        self,
        rag_service: RAGService,
        mock_chroma_collection: MagicMock,
    ):
        """所有结果低于阈值时返回空列表。"""
        mock_chroma_collection.query.return_value = {
            "ids": [["c1", "c2"]],
            "documents": [["doc1", "doc2"]],
            "metadatas": [[{"source": "s"}, {"source": "s"}]],
            "distances": [[0.7, 0.85]],
        }

        results = rag_service.search(
            query="完全不相关的查询",
            top_k=5,
            distance_threshold=0.3,
        )

        assert results == []


# ===========================================================================
# TestRAGService — 服务层集成
# ===========================================================================


class TestRAGService:
    """RAGService 初始化与集成测试。"""

    def test_initialize_creates_collection(
        self,
        mock_chroma_collection: MagicMock,
    ):
        """初始化时通过 ChromaDB Client 创建/获取集合。"""
        with patch("chromadb.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.get_or_create_collection.return_value = mock_chroma_collection
            mock_client_cls.return_value = mock_client

            service = RAGService(collection_name="cnc_knowledge")

            mock_client.get_or_create_collection.assert_called_once_with(
                name="cnc_knowledge",
            )
            assert service._collection is mock_chroma_collection

    def test_ingest_knowledge_base(
        self,
        rag_service: RAGService,
        mock_chroma_collection: MagicMock,
        knowledge_documents: list[dict[str, Any]],
    ):
        """批量导入知识库文档，覆盖 PRD §4.1.2 五个领域。"""
        rag_service.ingest_knowledge_base(knowledge_documents)

        # 所有文档都被摄入
        assert mock_chroma_collection.add.call_count == len(knowledge_documents)

        # 验证每个领域的文档都被包含
        all_calls = mock_chroma_collection.add.call_args_list
        ingested_sources: set[str] = set()
        for call in all_calls:
            metadatas = call.kwargs.get("metadatas", [])
            for meta in metadatas:
                if "source" in meta:
                    ingested_sources.add(meta["source"])

        expected_sources = {"材料库", "故障库", "工艺库", "报警码库", "切削参数"}
        assert expected_sources.issubset(ingested_sources), (
            f"Missing sources: {expected_sources - ingested_sources}"
        )

    def test_search_with_relevance_scores(
        self,
        rag_service: RAGService,
        mock_chroma_collection: MagicMock,
    ):
        """返回带相似度分数的结果，分数排序从高到低。"""
        mock_chroma_collection.query.return_value = {
            "ids": [["c1", "c2", "c3"]],
            "documents": [
                [
                    "45#钢切削速度80-120m/min",
                    "45#钢硬度HRC20-25",
                    "304不锈钢切削参数",
                ]
            ],
            "metadatas": [
                [
                    {"source": "切削参数", "category": "碳钢"},
                    {"source": "材料库", "category": "碳钢"},
                    {"source": "切削参数", "category": "不锈钢"},
                ]
            ],
            "distances": [[0.1, 0.2, 0.6]],
        }

        results = rag_service.search(query="45#钢", top_k=5)

        assert len(results) == 3
        # 结果按距离升序排列（距离越小越相关）
        assert results[0].distance <= results[1].distance <= results[2].distance
        # 每个结果都有 distance 字段
        for r in results:
            assert hasattr(r, "distance")
            assert isinstance(r.distance, float)
