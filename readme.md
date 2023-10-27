# text sementic search from Elasticsearch
An Elasticsearch for text semantic task

## Usage
### Service
`create_index`: create elasticsearch index\
`delete_index`: delete elasticsearch index\
`bulk`: add sentence query and vector query to elasticsearch\
`get_response_from_text_field`: get similar text response from text field and bm25 score\
`get_response_from_vector_field`:get similar text response from vector field and cosine similarity score

## Example
```python
# init elasticsearch client
from elasticsearch import Elasticsearch
from worker.service.search import SearchService
client = Elasticsearch('http://localhost:9200')

# add elasticsearch client to Searchservice
es_client = SearchService(client=client)

# create index
es_client.create_index(index_name = "text_vector")

# text
text = "Hello world"
text_embedding = [...] # list of vector

#add text to elastic search
es_client.bulk(index_name="text_vector", sentence_query=speech, vector_query=vector_query)

# get response from vector field
es_client.get_response_from_vector_field(index_name="text_vector", vector_query=vector_query)

#example output
[{'text': "Hello World",
  'score': 1.0}]

# get response from text field
es_client.get_response_from_text_field(index_name="text_vector", sentence_query=speechs[0])

#example output
[{'text': "Hello World",
  'score': 2.2}]
```