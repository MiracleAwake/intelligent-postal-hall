"""对照柜台口语用例。不进单元测试，避免每次都打到云端。"""

import json
from pathlib import Path

from app.capabilities.skills import understand_request
from app.provider.client import ModelCallError, Provider
from app.threshold import DEFAULT_THRESHOLD
from decimal import Decimal


def score(actual: dict, expect: dict) -> list[str]:
    misses = []
    for key, wanted in expect.items():
        got = actual.get(key)
        if key == "intents":
            if set(got or []) != set(wanted):
                misses.append(f"intents {got} != {wanted}")
            continue
        if key == "missing":
            if set(got or []) != set(wanted):
                misses.append(f"missing {got} != {wanted}")
            continue
        if got != wanted:
            misses.append(f"{key} {got} != {wanted}")
    return misses


def auth_for(actual: dict) -> bool:
    amounts = [actual.get("base_amount"), actual.get("add_amount")]
    for amount in amounts:
        if amount and Decimal(amount) >= Decimal(DEFAULT_THRESHOLD):
            return True
    return False


def main() -> None:
    path = Path(__file__).with_name("counter_utterances.json")
    spec = json.loads(path.read_text(encoding="utf-8"))
    provider = Provider()
    rows = []
    for case in spec["cases"]:
        actual = None
        error = ""
        for _ in range(2):
            try:
                actual = understand_request(provider, case["text"], profile_id=spec["profile_id"])
                error = ""
                break
            except ModelCallError as exc:
                error = str(exc)[:200]
                provider.breakers[spec["profile_id"]].failures = 0
                provider.breakers[spec["profile_id"]].open = False
        if actual is None:
            rows.append({"id": case["id"], "text": case["text"], "ok": False, "misses": [error], "actual": None})
            print(case["id"], error)
            continue
        misses = score(actual, case["expect"])
        rows.append(
            {
                "id": case["id"],
                "text": case["text"],
                "ok": not misses,
                "misses": misses,
                "auth_likely": auth_for(actual),
                "actual": {
                    "intents": actual.get("intents"),
                    "interest": actual.get("interest"),
                    "new_term": actual.get("new_term"),
                    "base_amount": actual.get("base_amount"),
                    "add_amount": actual.get("add_amount"),
                    "print_new_certificate": actual.get("print_new_certificate"),
                    "party": actual.get("party"),
                    "missing": actual.get("missing"),
                    "summary": actual.get("summary"),
                },
            }
        )
        print(case["id"], "OK" if not misses else misses)
    out = path.with_name("counter_utterances_last.json")
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    failed = [row["id"] for row in rows if not row["ok"]]
    print(f"{len(rows) - len(failed)}/{len(rows)}  profile={spec['profile_id']}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
