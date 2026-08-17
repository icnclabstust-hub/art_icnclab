#!/usr/bin/env python3
"""
導入Harvard數據到Neo4j
"""

import json
import subprocess

# 讀取數據
with open('harvard_data/harvard_objects_new.json', 'r', encoding='utf-8') as f:
    objects = json.load(f)

with open('harvard_data/harvard_people_new.json', 'r', encoding='utf-8') as f:
    people = json.load(f)

print(f"準備導入 {len(objects)} 件作品和 {len(people)} 位人物...")

# 生成Cypher腳本
cypher_statements = []

# 導入人物
for person in people:
    name = person.get('name', 'Unknown').replace("'", "\\'").replace('"', '\\"')[:200]
    person_id = person.get('id', 0)
    culture = person.get('culture', '').replace("'", "\\'")[:100]

    cypher = f"""MERGE (p:Artist {{id: {person_id}, source: 'Harvard'}}) SET p.name = "{name}", p.culture = "{culture}";"""
    cypher_statements.append(cypher)

print(f"生成了 {len(cypher_statements)} 個人物導入語句")

# 導入作品
for obj in objects:
    title = obj.get('title', 'Untitled').replace("'", "\\'").replace('"', '\\"')[:200]
    obj_id = obj.get('id', 0)
    dated = obj.get('dated', '').replace("'", "\\'")[:50]
    medium = obj.get('medium', '').replace("'", "\\'")[:200]
    classification = obj.get('classification', '').replace("'", "\\'")[:100]

    cypher = f"""MERGE (a:Artwork {{id: {obj_id}, source: 'Harvard'}}) SET a.title = "{title}", a.dated = "{dated}", a.medium = "{medium}", a.classification = "{classification}";"""
    cypher_statements.append(cypher)

    # 創建關係
    if 'people' in obj and obj['people']:
        for person in obj['people']:
            if person.get('role') in ['Artist', 'Creator']:
                person_id = person.get('personid')
                if person_id:
                    rel_cypher = f"""MATCH (a:Artwork {{id: {obj_id}, source: 'Harvard'}}), (p:Artist {{id: {person_id}, source: 'Harvard'}}) MERGE (p)-[:CREATED]->(a);"""
                    cypher_statements.append(rel_cypher)

print(f"總共生成了 {len(cypher_statements)} 個Cypher語句")

# 批量執行
print("開始導入到Neo4j...")

successful = 0
failed = 0

for i, stmt in enumerate(cypher_statements):
    try:
        result = subprocess.run(
            [
                'docker', 'exec', 'art-history-neo4j',
                'cypher-shell', '-u', 'neo4j', '-p', 'CHANGE_ME_NEO4J_PASSWORD',
                stmt
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            successful += 1
        else:
            failed += 1

        if (i + 1) % 10 == 0:
            print(f"  進度: {i+1}/{len(cypher_statements)} (成功:{successful}, 失敗:{failed})")

    except Exception as e:
        failed += 1

print(f"\n✅ 導入完成！")
print(f"  成功: {successful}")
print(f"  失敗: {failed}")
