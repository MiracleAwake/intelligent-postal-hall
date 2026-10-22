"""管理员的模型、分支局提示词、知识库。不写密钥，不启动向量库。"""

from app.capabilities.memory import FOUNDATION
from app.provider.profiles import default_profile, load_profiles

ORGS = (
    {"id": 7, "name": "东风路支局"},
    {"id": 8, "name": "西城路支局"},
)
ROLES = ("P1", "P2", "P3", "P4", "P5")


class Studio:
    def __init__(self) -> None:
        self.profiles = {
            item.id: {
                "id": item.id,
                "display_name": item.display_name,
                "protocol": item.protocol,
                "base_url": item.base_url,
                "model": item.model,
            }
            for item in load_profiles().values()
        }
        self.active = default_profile().id
        self.prompts: dict[tuple[int, str], str] = {}
        self.docs: list[dict] = []
        self._n = 0

    def models(self) -> dict:
        return {
            "active": self.active,
            "items": list(self.profiles.values()),
        }

    def add_model(self, payload: dict) -> dict:
        name = str(payload.get("id") or "").strip()
        if not name or name in self.profiles:
            return {"status": "rejected"}
        row = {
            "id": name,
            "display_name": str(payload.get("display_name") or name),
            "protocol": str(payload.get("protocol") or "openai"),
            "base_url": str(payload.get("base_url") or "").rstrip("/"),
            "model": str(payload.get("model") or name),
        }
        self.profiles[name] = row
        return {"status": "added", "item": row}

    def switch(self, profile_id: str) -> dict:
        if profile_id not in self.profiles:
            return {"status": "missing", "active": self.active}
        self.active = profile_id
        return {"status": "switched", "active": self.active}

    def prompt(self, org_id: int, role_code: str) -> dict:
        key = (org_id, role_code)
        if key not in self.prompts:
            base = FOUNDATION.get(role_code, "")
            if org_id != 7 and base:
                base = base + "\n本支局另守一句：授权口吻按本支局现行参数。"
            self.prompts[key] = base
        org = next((item["name"] for item in ORGS if item["id"] == org_id), str(org_id))
        return {"org_id": org_id, "org_name": org, "role_code": role_code, "body": self.prompts[key]}

    def save_prompt(self, org_id: int, role_code: str, body: str) -> dict:
        self.prompts[(org_id, role_code)] = body.strip()
        return self.prompt(org_id, role_code)

    def add_doc(self, title: str, body: str, *, source: str) -> dict:
        text = body.strip()
        if not title.strip() or not text:
            return {"status": "rejected"}
        self._n += 1
        row = {"id": self._n, "title": title.strip(), "body": text, "source": source}
        self.docs.append(row)
        return {"status": "added", "doc": row}

    def find(self, query: str) -> dict:
        needle = query.strip()
        if not needle:
            return {"items": list(self.docs)}
        items = [
            row for row in self.docs if needle in row["title"] or needle in row["body"]
        ]
        return {"items": items}

    def update_doc(self, doc_id: int, title: str, body: str) -> dict:
        for row in self.docs:
            if row["id"] == doc_id:
                if title.strip():
                    row["title"] = title.strip()
                if body.strip():
                    row["body"] = body.strip()
                return {"status": "updated", "doc": row}
        return {"status": "missing"}
