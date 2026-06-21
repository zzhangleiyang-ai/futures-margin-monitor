import json
import sys
from datetime import datetime
from pathlib import Path


def fail(message):
    print(f"DATA CHECK FAILED: {message}")
    raise SystemExit(1)


def parse_iso(value):
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception as exc:
        fail(f"invalid updatedAt: {value!r} ({exc})")


def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/data.json")
    if not target.exists():
        fail(f"file not found: {target}")

    payload = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        fail("payload must be a JSON object")

    items = payload.get("items")
    if not isinstance(items, list):
        fail("items must be a list")

    if payload.get("status") != "ok":
        fail(f"status is {payload.get('status')!r}, message={payload.get('message')!r}")

    if len(items) < 60:
        fail(f"expected at least 60 items, got {len(items)}")

    parse_iso(str(payload.get("updatedAt", "")))

    priced = 0
    margined = 0
    contracts = 0
    bad_rows = []

    for item in items:
        code = item.get("code") or "?"
        exchange = item.get("exchange")
        multiplier = item.get("contractMultiplier")
        rate = item.get("marginRate")
        margin = item.get("marginPerLot")
        price = item.get("price")
        contract = item.get("contract")

        if not exchange:
            bad_rows.append(f"{code}: missing exchange")
        if not multiplier:
            bad_rows.append(f"{code}: missing contractMultiplier")
        if price is not None:
            try:
                if float(price) > 0:
                    priced += 1
            except Exception:
                bad_rows.append(f"{code}: invalid price {price!r}")
        if rate is not None:
            try:
                rate_num = float(rate)
                if 0 < rate_num < 1:
                    margined += 1
                else:
                    bad_rows.append(f"{code}: invalid marginRate {rate!r}")
            except Exception:
                bad_rows.append(f"{code}: invalid marginRate {rate!r}")
        if margin is not None:
            try:
                if float(margin) <= 0:
                    bad_rows.append(f"{code}: invalid marginPerLot {margin!r}")
            except Exception:
                bad_rows.append(f"{code}: invalid marginPerLot {margin!r}")
        if contract:
            contracts += 1

    if bad_rows:
        fail("; ".join(bad_rows[:8]))

    required_coverage = max(60, int(len(items) * 0.85))
    if priced < required_coverage:
        fail(f"priced items too low: {priced}/{len(items)}")
    if margined < required_coverage:
        fail(f"margin items too low: {margined}/{len(items)}")
    if contracts < required_coverage:
        fail(f"contract coverage too low: {contracts}/{len(items)}")

    print(
        f"DATA CHECK OK: items={len(items)} priced={priced} "
        f"margins={margined} contracts={contracts} updatedAt={payload['updatedAt']}"
    )


if __name__ == "__main__":
    main()
