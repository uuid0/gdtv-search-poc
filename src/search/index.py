from datetime import UTC, datetime

from elasticsearch import Elasticsearch

from search.docs import ConceptDocument


class ElasticsearchConceptIndex:
    _client: Elasticsearch
    _index_name: str

    def __init__(
            self,
            hosts: list[str],
            username: str,
            password: str,
            index_name: str = "concepts",
    ):
        self._client: Elasticsearch = Elasticsearch(
            hosts=hosts,
            basic_auth=(username, password),
        )
        self._index_name = index_name

    def doc_id(
            self,
            course_id: str,
            video_id: str,
            concept_name: str,
    ) -> str:
        return f"{course_id}::{video_id}::{concept_name}"

    def setup(self, drop_index: bool = False):
        mappings = {
            "properties": {
                "concept_name": {"type": "text"},
                "description": {"type": "text"},
                "keywords": {"type": "text"}, # not using keyword to be more relaxed
                "share": {"type": "float"},
                "duration_ms": {"type": "integer"},
                "course_id": {"type": "keyword"},
                "video_id": {"type": "keyword"},
                "updated_at": {"type": "date"},
                "newly_introduced": {"type": "boolean"},
                "further_discussed": {"type": "boolean"},
                "just_mentioned": {"type": "boolean"},
            }
        }
        if drop_index:
            self._client.indices.delete(index=self._index_name)
        self._client.indices.create(
            index=self._index_name,
            mappings=mappings,
        )

    def search(
            self,
            keywords: list[str] | None = None,
            course_ids: list[str] | None = None,
    ) -> list[ConceptDocument]:
        must = []
        if keywords:
            must.append({"match": {"keywords": " ".join(keywords)}})
        if course_ids:
            must.append({"terms": {"course_id": course_ids}})
        if not must:
            query = {"match_all": {}}
        else:
            query = {"bool": {
                "must": must,
            }}
        return self._client.search(
            index=self._index_name,
            query=query,
        )["hits"]["hits"]  # yolo

    def get_all_keywords(
            self,
            course_ids: list[str] | None = None,
    ) -> list[tuple[str, int]]:
        if course_ids is None:
            query = {"match_all": {}}
        else:
            query = {"terms": {"course_id": course_ids}}
        docs = self._client.search(
            index=self._index_name,
            query=query,
        )["hits"]["hits"]
        keywords = {}
        for doc in docs:
            for kw in doc["_source"]["keywords"]:
                if kw not in keywords:
                    keywords[kw] = 0
                keywords[kw] += 1
        return list(keywords.items())

    def index(
            self,
            course_id: str,
            video_id: str,
            concept_name: str,
            description: str,
            keywords: list[str],
            share: float,
            duration_ms: int,
            newly_introduced: bool,
            further_discussed: bool,
            just_mentioned: bool,
    ):
        doc_id = self.doc_id(course_id, video_id, concept_name)
        doc = ConceptDocument(
            id=doc_id,
            concept_name=concept_name,
            description=description,
            keywords=keywords,
            share=share,
            duration_ms=duration_ms,
            course_id=course_id,
            video_id=video_id,
            updated_at=datetime.now(UTC),
            newly_introduced=newly_introduced,
            further_discussed=further_discussed,
            just_mentioned=just_mentioned,
        )
        self._client.index(
            id=doc_id,
            index=self._index_name,
            document=doc,
        )
