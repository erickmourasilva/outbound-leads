#!/usr/bin/env python3
"""Outreach engine - CLI.

  python3 -m outbound init                    create the database
  python3 -m outbound seed [file.json]        import already-contacted leads from a local JSON (data/seed_leads.json)
  python3 -m outbound import leads.csv        add leads from a CSV (dedupes by handle, honours do-not-contact)
  python3 -m outbound export [file.csv]       export every lead to CSV
  python3 -m outbound stats                   counts and forecast
  python3 -m outbound dnc <handle> [reason]   add a handle to the do-not-contact list
  python3 -m outbound serve [port]            live dashboard on 127.0.0.1
"""
import csv
import json
import os
import sys
from datetime import datetime

from . import dashboard, db

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FIELDS = ["kind", "segment", "name", "handle", "source_kind", "source_ref", "source_url", "signal",
              "signal_date", "score", "status", "variant", "message_text", "scheduled_at", "sent_at", "notes"]



def cmd_init():
    db.init()
    print("Banco criado em", db.DB_PATH)


def cmd_seed(path: str | None = None):
    """Import already-contacted leads from a local JSON file (never stored in code)."""
    db.init()
    path = path or os.environ.get("SEED_LEADS", os.path.join(ROOT, "data", "seed_leads.json"))
    if not os.path.exists(path):
        print(f"Arquivo não encontrado: {path}\nVeja docs/examples/seed_leads.example.json para o formato.")
        return
    msg_path = os.environ.get("SEED_MESSAGES", os.path.join(ROOT, "data", "seed_messages.json"))
    texts = json.load(open(msg_path)) if os.path.exists(msg_path) else {}
    added = 0
    with db.connect() as con:
        for item in json.load(open(path)):
            msg = texts.get(item.get("message_key", ""), "")
            fields = {k: item[k] for k in ("kind", "handle", "name", "segment", "source_kind", "source_ref",
                                          "source_url", "signal", "signal_date", "score", "status", "variant",
                                          "sent_at", "notes") if k in item}
            if db.add_lead(con, message_text=msg, **fields):
                added += 1
                if item.get("status") == "sent":
                    lead_id = con.execute("SELECT id FROM leads WHERE handle=?", (db.normalize_handle(item["handle"]),)).fetchone()["id"]
                    con.execute("INSERT INTO sends(lead_id, sent_at, result, variant, message_text) VALUES (?,?,?,?,?)",
                                (lead_id, item.get("sent_at") or db.now_utc(), item.get("send_result", "ok"),
                                 item.get("variant", ""), msg))
        db.log_event(con, f"Importados {added} perfis de {os.path.basename(path)}")
    print(f"{added} perfis importados")


def cmd_import(path: str):
    db.init()
    added = skipped = 0
    with db.connect() as con, open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            row = {k: (v or "").strip() for k, v in row.items() if k in CSV_FIELDS}
            if row.get("kind") not in db.KINDS or not row.get("handle") or not row.get("name"):
                skipped += 1
                continue
            row["score"] = int(row["score"]) if row.get("score", "").isdigit() else 0
            row.setdefault("status", "discovered")
            row["status"] = row["status"] if row["status"] in db.STATUSES else "discovered"
            row.pop("scheduled_at", None)
            row["sent_at"] = row.get("sent_at") or None
            if db.add_lead(con, **row):
                added += 1
            else:
                skipped += 1
        db.log_event(con, f"Importação de {os.path.basename(path)}: {added} novos, {skipped} ignorados")
    print(f"{added} novos, {skipped} ignorados (duplicados, bloqueados ou inválidos)")


def cmd_export(path: str | None):
    db.init()
    path = path or os.path.join(ROOT, "exports", f"leads-{datetime.now():%Y%m%d-%H%M}.csv")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with db.connect() as con, open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(CSV_FIELDS)
        for r in con.execute("SELECT * FROM leads ORDER BY id"):
            w.writerow([r[f] if r[f] is not None else "" for f in CSV_FIELDS])
    print("Exportado:", path)


def cmd_stats():
    db.init()
    state = dashboard.build_state()
    c = state["counts"]
    print(json.dumps({"total": c["total"], "por_status": c["by_status"], "por_tipo": c["by_kind"],
                      "enviados_hoje": c["sent_today"], "fila": c["queue"],
                      "previsao": {k: v for k, v in state["forecast"].items() if k != "plan"}},
                     ensure_ascii=False, indent=2))


def cmd_dnc(handle: str, reason: str = ""):
    db.init()
    h = db.normalize_handle(handle)
    with db.connect() as con:
        con.execute("INSERT OR REPLACE INTO do_not_contact(handle, reason, created_at) VALUES (?,?,?)", (h, reason, db.now_utc()))
        con.execute("UPDATE leads SET status='do_not_contact', updated_at=? WHERE handle=?", (db.now_utc(), h))
        db.log_event(con, f"@{h} adicionado à lista de não contato", "warn")
    print("OK:", h)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    cmd, args = argv[1], argv[2:]
    if cmd == "init":
        cmd_init()
    elif cmd == "seed":
        cmd_seed(args[0] if args else None)
    elif cmd == "import" and args:
        cmd_import(args[0])
    elif cmd == "export":
        cmd_export(args[0] if args else None)
    elif cmd == "stats":
        cmd_stats()
    elif cmd == "dnc" and args:
        cmd_dnc(args[0], " ".join(args[1:]))
    elif cmd == "serve":
        db.init()
        dashboard.serve(int(args[0]) if args else None)
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
