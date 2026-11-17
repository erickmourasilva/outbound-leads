"""Local live dashboard (read-mostly). Serves on 127.0.0.1 only. Stdlib only.

Run: python3 -m outbound serve (uses https://outbound-leads.localhost via portless when installed)
"""
import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from zoneinfo import ZoneInfo

from . import db, forecast


def build_state() -> dict:
    with db.connect() as con:
        st = db.get_settings(con)
        tz = ZoneInfo(st["timezone"])
        today = datetime.now(tz).date()
        # "today" in local time -> UTC window
        start_local = datetime(today.year, today.month, today.day, tzinfo=tz)
        start_utc = start_local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        by_status = {r["status"]: r["n"] for r in con.execute("SELECT status, COUNT(*) n FROM leads GROUP BY status")}
        by_kind = {r["kind"]: r["n"] for r in con.execute("SELECT kind, COUNT(*) n FROM leads GROUP BY kind")}
        by_segment = [dict(r) for r in con.execute(
            "SELECT kind, segment, status, COUNT(*) n FROM leads GROUP BY kind, segment, status ORDER BY kind, segment")]
        sent_today = con.execute(
            "SELECT COUNT(*) FROM sends WHERE result='ok' AND sent_at >= ?", (start_utc,)).fetchone()[0]
        sent_total = con.execute("SELECT COUNT(*) FROM sends WHERE result='ok'").fetchone()[0]
        remaining = sum(by_status.get(s, 0) for s in ("approved", "queued"))
        pipeline_pending = sum(by_status.get(s, 0) for s in ("discovered", "qualified"))
        leads = [dict(r) for r in con.execute(
            """SELECT id, kind, segment, name, handle, source_kind, source_ref, signal, score, status, variant,
                      scheduled_at, sent_at FROM leads ORDER BY
                      CASE status WHEN 'queued' THEN 0 WHEN 'approved' THEN 1 WHEN 'qualified' THEN 2
                                  WHEN 'discovered' THEN 3 ELSE 4 END, score DESC, id DESC LIMIT 600""")]
        sends = [dict(r) for r in con.execute(
            """SELECT s.sent_at, s.result, s.variant, l.name, l.handle, l.kind FROM sends s
               JOIN leads l ON l.id = s.lead_id ORDER BY s.sent_at DESC LIMIT 40""")]
        events = [dict(r) for r in con.execute("SELECT at, level, message FROM events ORDER BY id DESC LIMIT 25")]
        fc = forecast.project(remaining, st, sent_today, today)
    return {
        "now": datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S"),
        "paused": st["paused"] == "1",
        "settings": st,
        "counts": {"by_status": by_status, "by_kind": by_kind, "by_segment": by_segment,
                   "sent_today": sent_today, "sent_total": sent_total,
                   "queue": remaining, "pending_qualification": pipeline_pending, "total": sum(by_status.values())},
        "forecast": fc,
        "leads": leads,
        "sends": sends,
        "events": events,
    }


PAGE = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Outbound Leads</title>
<style>
:root{--bg:#f6f7f9;--card:#fff;--ink:#14171f;--mut:#667085;--line:#e4e7ec;--ok:#067647;--warn:#b54708;--bad:#b42318;--acc:#3b5bdb}
@media (prefers-color-scheme:dark){:root{--bg:#0e1116;--card:#161b22;--ink:#e6e9ef;--mut:#9aa4b2;--line:#262d38;--ok:#4ade80;--warn:#fbbf24;--bad:#f87171;--acc:#7c93ff}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1180px;margin:0 auto;padding:16px}
header{display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between;margin-bottom:14px}
h1{font-size:18px;margin:0}h2{font-size:14px;margin:0 0 8px}
.pill{display:inline-block;padding:3px 10px;border-radius:999px;font-weight:600;font-size:12px;border:1px solid var(--line)}
.pill.on{color:var(--ok)}.pill.off{color:var(--warn)}
button{font:inherit;border:1px solid var(--line);background:var(--card);color:var(--ink);padding:6px 12px;border-radius:8px;cursor:pointer}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-bottom:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}
.k{color:var(--mut);font-size:12px}.v{font-size:24px;font-weight:700;margin-top:2px}
.two{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px}@media(max-width:820px){.two{grid-template-columns:1fr}}
table{width:100%;border-collapse:collapse}th,td{padding:6px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{color:var(--mut);font-weight:600;font-size:12px}.wrap{overflow:auto;max-height:420px}
.s-sent{color:var(--ok)}.s-failed,.s-do_not_contact{color:var(--bad)}.s-queued,.s-approved{color:var(--acc)}
.bar{height:8px;background:var(--line);border-radius:6px;overflow:hidden}.bar>i{display:block;height:100%;background:var(--acc)}
.row{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}select,input{font:inherit;padding:5px 8px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--ink)}
.mut{color:var(--mut)}
</style></head><body><main>
<header><div><h1>Outbound Leads</h1><div class="mut" id="now"></div></div>
<div><span id="state" class="pill"></span> <button id="toggle">Pausar / retomar</button></div></header>
<div class="grid" id="cards"></div>
<div class="two">
 <div class="card"><h2>Hoje</h2><div id="today"></div><div class="bar"><i id="todaybar" style="width:0"></i></div></div>
 <div class="card"><h2>Previsão</h2><div id="fc"></div></div>
</div>
<div class="two">
 <div class="card"><h2>Próximos dias (limite do aquecimento)</h2><div class="wrap"><table id="plan"></table></div></div>
 <div class="card"><h2>Segmentos</h2><div class="wrap"><table id="seg"></table></div></div>
</div>
<div class="card" style="margin-bottom:14px"><h2>Leads</h2>
 <div class="row"><select id="fk"><option value="">Todos os tipos</option><option value="client">Clientes</option><option value="partner">Parceiros</option><option value="intel">Concorrentes</option></select>
 <select id="fs"><option value="">Todos os status</option></select><input id="fq" placeholder="Buscar nome ou @"></div>
 <div class="wrap"><table id="leads"></table></div></div>
<div class="two">
 <div class="card"><h2>Últimos disparos</h2><div class="wrap"><table id="sends"></table></div></div>
 <div class="card"><h2>Eventos</h2><div class="wrap"><table id="events"></table></div></div>
</div>
</main>
<script>
const KIND={client:"Cliente",partner:"Parceiro",intel:"Concorrente"};
const ST={discovered:"Descoberto",qualified:"Qualificado",approved:"Aprovado",queued:"Na fila",sent:"Enviado",failed:"Falhou",skipped:"Ignorado",do_not_contact:"Não contatar"};
let S=null;
function el(t,txt,cls){const e=document.createElement(t);if(txt!==undefined)e.textContent=txt;if(cls)e.className=cls;return e}
function fmt(iso){if(!iso)return "";const d=new Date(iso);return d.toLocaleString("pt-BR",{day:"2-digit",month:"2-digit",hour:"2-digit",minute:"2-digit"})}
function table(id,head,rows){const t=document.getElementById(id);t.replaceChildren();const h=el("tr");head.forEach(x=>h.append(el("th",x)));t.append(h);
 rows.forEach(r=>{const tr=el("tr");r.forEach(c=>{const td=el("td");if(c&&c.text!==undefined){td.textContent=c.text;if(c.cls)td.className=c.cls}else td.textContent=c;tr.append(td)});t.append(tr)})}
function card(k,v){const c=el("div",undefined,"card");c.append(el("div",k,"k"),el("div",String(v),"v"));return c}
function render(){
 if(!S)return;const c=S.counts,f=S.forecast;
 document.getElementById("now").textContent="Atualizado em "+S.now+" (Brasília)";
 const st=document.getElementById("state");st.textContent=S.paused?"Envio PAUSADO":"Envio ATIVO";st.className="pill "+(S.paused?"off":"on");
 const cards=document.getElementById("cards");cards.replaceChildren(card("Leads",c.total),card("Clientes",c.by_kind.client||0),card("Parceiros",c.by_kind.partner||0),card("Concorrentes",c.by_kind.intel||0),card("Na fila",c.queue),card("Aguardando qualificar",c.pending_qualification),card("Enviados (total)",c.sent_total));
 document.getElementById("today").textContent="Enviados hoje: "+c.sent_today+" de "+f.today_cap+" permitidos";
 document.getElementById("todaybar").style.width=Math.min(100,f.today_cap?100*c.sent_today/f.today_cap:0)+"%";
 document.getElementById("fc").textContent=f.remaining===0?"Fila vazia: nada a enviar.":("Fila de "+f.remaining+" leads. "+(f.finish_date?("Termina em "+f.finish_date.split("-").reverse().join("/")+", em "+f.days+" dias de envio."):"Fora do horizonte de previsão."))+(S.settings.warmup_start?"":" (aquecimento ainda não iniciado: previsão parte de hoje)");
 table("plan",["Data","Limite do dia","Previstos"],f.plan.map(p=>[p.date.split("-").reverse().join("/"),String(p.cap),String(p.planned)]));
 table("seg",["Tipo","Segmento","Status","Qtd"],c.by_segment.map(r=>[KIND[r.kind]||r.kind,r.segment||"-",ST[r.status]||r.status,String(r.n)]));
 const fs=document.getElementById("fs");if(fs.options.length===1)Object.entries(ST).forEach(([k,v])=>fs.append(new Option(v,k)));
 const k=document.getElementById("fk").value,s=document.getElementById("fs").value,q=document.getElementById("fq").value.toLowerCase();
 const rows=S.leads.filter(l=>(!k||l.kind===k)&&(!s||l.status===s)&&(!q||(l.name+" "+l.handle).toLowerCase().includes(q)));
 table("leads",["Tipo","Nome","@","Segmento","Origem","Sinal","Pts","Status","Variante","Quando"],rows.map(l=>[KIND[l.kind]||l.kind,l.name,"@"+l.handle,l.segment,l.source_ref||l.source_kind,l.signal.slice(0,90),String(l.score),{text:ST[l.status]||l.status,cls:"s-"+l.status},l.variant,fmt(l.sent_at||l.scheduled_at)]));
 table("sends",["Quando","Perfil","Tipo","Resultado"],S.sends.map(x=>[fmt(x.sent_at),"@"+x.handle,KIND[x.kind]||x.kind,{text:x.result,cls:x.result==="ok"?"s-sent":"s-failed"}]));
 table("events",["Quando","Nível","Mensagem"],S.events.map(x=>[fmt(x.at),x.level,x.message]));
}
async function load(){try{const r=await fetch("/api/state");S=await r.json();render()}catch(e){document.getElementById("now").textContent="Sem conexão com o servidor local"}}
["fk","fs","fq"].forEach(id=>document.getElementById(id).addEventListener("input",render));
document.getElementById("toggle").addEventListener("click",async()=>{await fetch("/api/toggle-pause",{method:"POST",headers:{"X-Requested-With":"dashboard"}});load()});
load();setInterval(load,5000);
</script></body></html>
"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/state":
            self._send(200, json.dumps(build_state(), ensure_ascii=False).encode(), "application/json; charset=utf-8")
        elif self.path in ("/", "/index.html"):
            self._send(200, PAGE.encode(), "text/html; charset=utf-8")
        else:
            self._send(404, b"not found", "text/plain")

    def do_POST(self):
        if self.path == "/api/toggle-pause" and self.headers.get("X-Requested-With") == "dashboard":
            with db.connect() as con:
                cur = db.get_settings(con)["paused"]
                new = "0" if cur == "1" else "1"
                con.execute("UPDATE settings SET value=? WHERE key='paused'", (new,))
                db.log_event(con, "Envio retomado pelo painel" if new == "0" else "Envio pausado pelo painel",
                             "info" if new == "0" else "pause")
            self._send(200, b"{}", "application/json")
        else:
            self._send(403, b"forbidden", "text/plain")

    def log_message(self, *args):  # quiet
        pass


def serve(port: int | None = None) -> None:
    """Bind to 127.0.0.1 only. portless injects PORT; fall back to 8787."""
    port = port or int(os.environ.get("PORT", "8787"))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    url = os.environ.get("PORTLESS_URL") or f"http://127.0.0.1:{port}"
    print(f"Painel: {url}  (porta {port}, só local). Ctrl+C para parar.", flush=True)
    server.serve_forever()
