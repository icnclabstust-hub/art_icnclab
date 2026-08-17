"""
title: Obsidian 筆記庫
author: Art History Database Team
version: 1.1.0
description: 個人筆記知識庫。使用者查到資料想保存時用 save_reading_note（存進「01 閱讀筆記」），
記錄靈感/草稿時用 save_idea（存進「02 想法草稿」）；一般讀寫用 read_note/write_note/append_note，
全文搜尋用 search_notes，列出筆記用 list_notes。
"""

import requests
import urllib3
from datetime import date
from pydantic import BaseModel, Field

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Tools:
    class Valves(BaseModel):
        API_URL: str = Field(
            default="https://172.20.160.1:27124",
            description="Obsidian Local REST API 位址（Open WebUI 跑在 WSL 裡，Obsidian 在 Windows 端，"
            "127.0.0.1 在兩邊是不同網段，必須用 WSL 看到的 Windows 主機 IP；"
            "此 IP 可能在系統重開機後改變，可用 WSL 裡執行 `ip route show | grep default` 確認目前值）",
        )
        API_KEY: str = Field(
            default="",
            description="Obsidian Local REST API 外掛設定頁裡的 API Key",
        )
        TIMEOUT: int = Field(default=15, description="請求逾時秒數")

    def __init__(self):
        self.valves = self.Valves()

    def _headers(self):
        return {"Authorization": f"Bearer {self.valves.API_KEY}"}

    def list_notes(self, folder: str = "") -> str:
        """列出 Obsidian 筆記庫裡某個資料夾（預設為根目錄）底下的所有筆記檔案。

        :param folder: 資料夾路徑，留空代表根目錄
        """
        try:
            path = f"/vault/{folder}/" if folder else "/vault/"
            resp = requests.get(
                f"{self.valves.API_URL}{path}",
                headers=self._headers(),
                verify=False,
                timeout=self.valves.TIMEOUT,
            )
            resp.raise_for_status()
            files = resp.json().get("files", [])
            return "\n".join(files) if files else "（這個資料夾是空的）"
        except Exception as e:
            return f"❌ 列出筆記失敗: {e}"

    def read_note(self, filename: str) -> str:
        """讀取指定筆記的完整內容。

        :param filename: 筆記檔名，含路徑與副檔名，例如 "藝術史筆記/文藝復興.md"
        """
        try:
            resp = requests.get(
                f"{self.valves.API_URL}/vault/{filename}",
                headers=self._headers(),
                verify=False,
                timeout=self.valves.TIMEOUT,
            )
            if resp.status_code == 404:
                return f"❌ 找不到筆記: {filename}"
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            return f"❌ 讀取筆記失敗: {e}"

    def write_note(self, filename: str, content: str) -> str:
        """建立新筆記或覆寫既有筆記的完整內容。

        :param filename: 筆記檔名，含路徑與副檔名，例如 "藝術史筆記/文藝復興.md"
        :param content: 要寫入的完整 Markdown 內容
        """
        try:
            resp = requests.put(
                f"{self.valves.API_URL}/vault/{filename}",
                headers={**self._headers(), "Content-Type": "text/markdown"},
                data=content.encode("utf-8"),
                verify=False,
                timeout=self.valves.TIMEOUT,
            )
            resp.raise_for_status()
            return f"✅ 已寫入筆記: {filename}"
        except Exception as e:
            return f"❌ 寫入筆記失敗: {e}"

    def append_note(self, filename: str, content: str) -> str:
        """在既有筆記的結尾附加內容，不覆蓋原本的內容；若筆記不存在則會新建。

        :param filename: 筆記檔名，含路徑與副檔名
        :param content: 要附加的 Markdown 內容
        """
        try:
            resp = requests.post(
                f"{self.valves.API_URL}/vault/{filename}",
                headers={**self._headers(), "Content-Type": "text/markdown"},
                data=content.encode("utf-8"),
                verify=False,
                timeout=self.valves.TIMEOUT,
            )
            resp.raise_for_status()
            return f"✅ 已附加內容到筆記: {filename}"
        except Exception as e:
            return f"❌ 附加內容失敗: {e}"

    def save_reading_note(self, title: str, content: str, source: str = "") -> str:
        """把使用者查到、想保存的資料整理成一篇閱讀筆記，存進「01 閱讀筆記」資料夾，自動加上日期與來源欄位。
        適合用在使用者說「幫我記下來」「幫我存這篇資料」「幫我整理成筆記」的時候。

        :param title: 筆記標題（不含副檔名與日期）
        :param content: 筆記內容，例如重點整理、摘要
        :param source: 資料來源，例如網址、書名、查詢主題，可留空
        """
        today = date.today().isoformat()
        filename = f"01 閱讀筆記/{today} {title}.md"
        front_matter = f"---\ntype: 閱讀筆記\ndate: {today}\n來源: {source}\n---\n\n"
        return self.write_note(filename, f"{front_matter}# {title}\n\n{content}")

    def save_idea(self, title: str, content: str) -> str:
        """把使用者的想法、靈感存成一篇草稿，存進「02 想法草稿」資料夾，自動加上日期與狀態欄位。
        適合用在使用者說「幫我記一個想法」「幫我存這個點子」的時候。

        :param title: 想法標題（不含副檔名與日期）
        :param content: 想法內容
        """
        today = date.today().isoformat()
        filename = f"02 想法草稿/{today} {title}.md"
        front_matter = f"---\ntype: 想法草稿\ndate: {today}\n狀態: 草稿\n---\n\n"
        return self.write_note(filename, f"{front_matter}# {title}\n\n{content}")

    def search_notes(self, query: str) -> str:
        """在整個筆記庫裡做全文搜尋，回傳符合的筆記檔名與匹配片段。

        :param query: 搜尋關鍵字
        """
        try:
            resp = requests.post(
                f"{self.valves.API_URL}/search/simple/",
                headers=self._headers(),
                params={"query": query},
                verify=False,
                timeout=self.valves.TIMEOUT,
            )
            resp.raise_for_status()
            results = resp.json()
            if not results:
                return f"沒有找到符合「{query}」的筆記"

            lines = []
            for r in results[:10]:
                filename = r.get("filename", "未知")
                matches = r.get("matches", [])
                snippet = matches[0].get("context", "") if matches else ""
                lines.append(f"📄 {filename}\n{snippet}")
            return "\n\n".join(lines)
        except Exception as e:
            return f"❌ 搜尋筆記失敗: {e}"
