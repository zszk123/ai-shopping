"""Milvus vector search service."""
from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    connections,
    utility,
)

from app.config import settings

VECTOR_DIM = 1024
COLLECTION_NAME = settings.MILVUS_COLLECTION


def _get_collection() -> Collection:
    if not utility.has_collection(COLLECTION_NAME):
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="goods_id", dtype=DataType.INT64),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=VECTOR_DIM),
            FieldSchema(name="brand", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="platform", dtype=DataType.VARCHAR, max_length=32),
        ]
        schema = CollectionSchema(fields, description="goods vector collection")
        collection = Collection(COLLECTION_NAME, schema)
        index_params = {
            "metric_type": "IP",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128},
        }
        collection.create_index("vector", index_params)
    else:
        collection = Collection(COLLECTION_NAME)

    collection.load()
    return collection


async def init_milvus():
    connections.connect(
        alias="default",
        host=settings.MILVUS_HOST,
        port=settings.MILVUS_PORT,
        timeout=5,
    )
    _get_collection()


async def ping_milvus() -> bool:
    try:
        connections.connect(
            alias="default",
            host=settings.MILVUS_HOST,
            port=settings.MILVUS_PORT,
            timeout=5,
        )
        utility.list_collections()
        return True
    except Exception:
        return False


async def insert_vector(goods_id: int, vector: list[float], brand: str = "", platform: str = "") -> bool:
    collection = _get_collection()
    data = [[goods_id], [vector], [brand], [platform]]
    result = collection.insert(data)
    return result.insert_count > 0


async def search_similar_goods(query_vector: list[float], top_k: int = 50) -> list[int]:
    collection = _get_collection()
    search_params = {"metric_type": "IP", "params": {"nprobe": 16}}
    results = collection.search(
        data=[query_vector],
        anns_field="vector",
        param=search_params,
        limit=top_k,
        output_fields=["goods_id"],
    )
    goods_ids = []
    for hits in results:
        for hit in hits:
            goods_ids.append(hit.entity.get("goods_id"))
    return goods_ids


async def delete_vector_by_goods_id(goods_id: int):
    collection = _get_collection()
    collection.delete(f"goods_id == {goods_id}")
