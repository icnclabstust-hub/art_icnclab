#!/usr/bin/env python3
"""
測試 ChromaDB 查詢功能
"""

import requests
from sentence_transformers import SentenceTransformer

print("🔍 測試 ChromaDB 查詢功能")
print("=" * 60)

# 初始化嵌入模型
print("\n📦 載入嵌入模型...")
try:
    model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
    print("✅ 模型載入成功")
except Exception as e:
    print(f"❌ 模型載入失敗: {e}")
    exit(1)

# ChromaDB 配置
chroma_url = "http://localhost:8001"
collection_name = "art_history_collection"

# 測試查詢
test_queries = ["達文西的畫作", "文藝復興時期", "巴洛克風格", "印象派", "梵谷"]

for query in test_queries:
    print(f"\n{'=' * 60}")
    print(f"🔎 查詢: {query}")
    print(f"{'=' * 60}")

    try:
        # 生成查詢向量
        query_embedding = model.encode(query).tolist()
        print(f"✅ 生成查詢向量 (維度: {len(query_embedding)})")

        # 查詢 ChromaDB
        response = requests.post(
            f"{chroma_url}/api/v2/tenants/default_tenant/databases/default_database/collections/{collection_name}/query",
            json={
                "query_embeddings": [query_embedding],
                "n_results": 3,
                "include": ["metadatas", "documents", "distances"],
            },
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()

            # 顯示結果
            documents = data.get("documents", [[]])[0]
            metadatas = data.get("metadatas", [[]])[0]
            distances = data.get("distances", [[]])[0]

            print(f"\n📊 找到 {len(documents)} 個結果:")

            for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances), 1):
                score = 1 / (1 + distance)  # 轉換為相似度分數

                print(f"\n[結果 {i}] 相似度: {score:.3f}")
                print(f"來源: ChromaDB > {metadata.get('collection', 'unknown')}")

                # 顯示作品資訊
                if "title" in metadata:
                    print(f"標題: {metadata['title']}")
                if "artist" in metadata:
                    print(f"藝術家: {metadata['artist']}")
                if "date" in metadata:
                    print(f"年代: {metadata['date']}")
                if "style" in metadata:
                    print(f"風格: {metadata['style']}")

                # 顯示內容摘要
                print(f"內容: {doc[:150]}...")
        else:
            print(f"❌ 查詢失敗: {response.status_code}")
            print(f"錯誤: {response.text}")

    except Exception as e:
        print(f"❌ 查詢錯誤: {e}")

print("\n" + "=" * 60)
print("✅ 測試完成！")
print("=" * 60)
