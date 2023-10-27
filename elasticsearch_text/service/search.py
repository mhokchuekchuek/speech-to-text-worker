from typing import Dict, List, Union

from elasticsearch import Elasticsearch


class SearchService:
    def __init__(
        self,
        client: Elasticsearch,
        sentence_query_name: str = "text",
        vector_query_name: str = "text_vector",
        vector_dim: int = 384,
        similarity_metric: str = "cosine",
    ):
        self.client = client
        self.sentence_query_name = sentence_query_name
        self.text_vector_query_name = vector_query_name
        self.vector_dim = vector_dim
        self.similarity_metric = similarity_metric
        self.mappings = self._create_mappings()

    def _create_mappings(self) -> Dict:
        return {
            "properties": {
                self.text_vector_query_name: {
                    "type": "dense_vector",
                    "dims": self.vector_dim,
                    "index": "true",
                    "similarity": self.similarity_metric,
                }
            }
        }

    def create_index(self, index_name: str):
        if not self._is_existed_index(index_name=index_name):
            self.client.indices.create(index=index_name, mappings=self.mappings)

    def _is_existed_index(self, index_name: str) -> bool:
        if self.client.indices.exists(index=index_name):
            return True
        return False

    def delete_index(self, index_name: str) -> bool:
        if self.is_existed_index(index_name):
            self.client.indices.delete(index=index_name)

    def _create_bulk_format(
        self, index_name: str, sentence_query: str, vector_query: List[int]
    ) -> List[Dict[str, List[int]]]:
        index_dict = {"index": {"_index": index_name}}
        query_dict = {
            self.sentence_query_name: sentence_query,
            self.text_vector_query_name: vector_query,
        }
        return [index_dict, query_dict]

    def bulk(self, index_name: str, sentence_query: str, vector_query: List[int]):
        bulk_input = self._create_bulk_format(index_name, sentence_query, vector_query)
        self.client.bulk(index=index_name, operations=bulk_input)

    def _search_from_vector_field(
        self,
        index_name: str,
        vector_query: List[int],
    ):
        return self.client.search(
            index=index_name,
            knn={
                "field": self.text_vector_query_name,
                "query_vector": vector_query,
                "k": 10,
                "num_candidates": 100,
            },
        )

    def _search_from_text_field(
        self,
        index_name: str,
        sentence_query: str,
    ):
        return self.client.search(
            index=index_name,
            body={
                "query": {"match_phrase": {self.sentence_query_name: sentence_query}}
            },
        )

    def get_response_from_text_field(
        self, index_name: str, sentence_query: str
    ) -> Union[None, str]:
        response = self._search_from_text_field(index_name, sentence_query)

        if len(response["hits"]["hits"]) == 0:
            return None

        else:
            response_item = []
            for hit in response["hits"]["hits"]:
                score = hit["_score"]
                text = hit["_source"][self.sentence_query_name]
                response_item.append({"text": text, "score": score})
            return response_item

    def get_response_from_vector_field(
        self, index_name: str, vector_query: List[int]
    ) -> List[tuple[str, float]]:
        response = self._search_from_vector_field(
            index_name=index_name, vector_query=vector_query
        )

        if len(response["hits"]["hits"]) == 0:
            return None

        else:
            response_item = []
            for hit in response["hits"]["hits"]:
                score = hit["_score"]
                text = hit["_source"][self.sentence_query_name]
                response_item.append({"text": text, "score": score})
            return response_item
