# 資料庫備份

| 檔案 | 內容 |
|------|------|
| `neo4j_data.tar.gz` | Neo4j 圖資料庫（部署機 bolt 7688 那座）|
| `chromadb_data.tar.gz` | ChromaDB 向量庫（部署機 8001）|
| `openwebui_data.tar.gz` | OpenWebUI 的 `vector_db/` 與 `uploads/` |

三者皆以 Git LFS 追蹤（見 `.gitattributes`）。

## openwebui_data.tar.gz 的排除項目

2026-08-18 重新打包，從 133 MB 縮為 275 KB。移除下列內容，**還原時需另行處理**：

- **`webui.db` / `-wal` / `-shm`** — 含使用者帳號、bcrypt 密碼雜湊、對話紀錄。
  本 repo 有公開 GitHub remote，依 CODING_STYLE.md S-18／S-19 不應納入版控
  （S-18 亦明文點名 `-wal`／`-shm`）。還原時請從部署機或離線備份取得。
- **`cache/whisper/`** — `faster-whisper-base` 模型，佔原始壓縮檔 99%
  （`blobs/` 與 `snapshots/` 各存一份共 290 MB）。OpenWebUI 首次使用語音功能時
  會自動從 HuggingFace 重新下載，不需納入版控。
- **`cache/audio/transcriptions/`** — 一段真人語音錄音（webm）。人聲屬可識別資料。

## 還原

```bash
tar -xzf openwebui_data.tar.gz -C <OpenWebUI 資料目錄的上層>
```

解開後只會有 `vector_db/` 與 `uploads/`；`webui.db` 缺席時 OpenWebUI 會建立全新的
空資料庫（等同重新初始化，需重設管理員帳號）。若要保留原帳號與對話，必須另外
取得 `webui.db` 再放回同一目錄。
