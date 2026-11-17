"""Fictional demo data for screenshots, docs and trying the dashboard. Never touches real leads."""
import random
from datetime import datetime, timedelta, timezone

from . import db

SEGMENTS = {
    "client": ["Clínica odontológica", "Clínica de estética", "Policlínica", "Escola de idiomas", "Imobiliária", "Contabilidade"],
    "partner": ["Agência de marketing", "Consultoria de CRM", "Integrador", "Agência de performance"],
    "intel": ["Concorrente: CRM de WhatsApp", "Concorrente: plataforma de atendimento"],
}
PREFIX = {"client": ["Aurora", "Horizonte", "Vitale", "Nova Era", "Prisma", "Atlântica", "Sereno", "Pioneira", "Lumen", "Boreal", "Alvorada", "Cedro"],
          "partner": ["Impulso", "Vértice", "Órbita", "Conecta", "Norte Digital", "Tração", "Sinapse", "Rota 360"],
          "intel": ["Exemplo Chat", "Demo Desk"]}
SIGNALS = {
    "client": ["Abriu nova unidade em outubro", "Vaga aberta de atendente de WhatsApp", "Matrículas abertas para o próximo ano",
               "Avaliações públicas citam demora no atendimento", "Anunciou expansão para uma segunda cidade"],
    "partner": ["Listada no diretório de parceiros de um CRM", "Implementa CRM e automação para PMEs", "Case publicado em página oficial"],
    "intel": ["Página pública de cases de clientes"],
}


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def populate(seed: int = 7) -> dict:
    rng = random.Random(seed)
    now = datetime.now(timezone.utc)
    plan = [("client", 26), ("partner", 20), ("intel", 2)]
    statuses = (["sent"] * 14 + ["queued"] * 9 + ["approved"] * 7 + ["qualified"] * 9 + ["discovered"] * 7 +
                ["skipped"] * 1 + ["failed"] * 1)
    rng.shuffle(statuses)
    created = 0
    with db.connect() as con:
        for kind, count in plan:
            for i in range(count):
                name = f"{rng.choice(PREFIX[kind])} {rng.choice(['Saúde', 'Studio', 'Group', 'Co.', 'Lab', 'Hub'])} (exemplo {kind[:1]}{i + 1})"
                handle = f"demo_{kind[:3]}_{i + 1:02d}"
                status = statuses.pop() if statuses else "discovered"
                sent_at = None
                if status == "sent":
                    sent_at = _iso(now - timedelta(hours=rng.choice([1, 2, 3, 5, 26, 28, 30, 50, 52, 75])))
                db.add_lead(con, kind=kind, name=name, handle=handle, segment=rng.choice(SEGMENTS[kind]),
                            source_kind=rng.choice(["competitor_directory", "news", "job", "maps"]),
                            source_ref=rng.choice(["Diretório A", "Diretório B", "Notícia regional", "Vaga pública"]),
                            source_url="https://example.com/fonte", signal=rng.choice(SIGNALS[kind]),
                            score=rng.randint(45, 92), status=status, variant=rng.choice(["v1", "v2"]),
                            message_text="Mensagem de exemplo", sent_at=sent_at)
                if status == "sent":
                    lead_id = con.execute("SELECT id FROM leads WHERE handle=?", (handle,)).fetchone()["id"]
                    con.execute("INSERT INTO sends(lead_id, sent_at, result, variant, message_text) VALUES (?,?,?,?,?)",
                                (lead_id, sent_at, "ok", "v1", "Mensagem de exemplo"))
                created += 1
        start = (now - timedelta(days=3)).date().isoformat()
        con.execute("UPDATE settings SET value=? WHERE key='warmup_start'", (start,))
        con.execute("UPDATE settings SET value='0' WHERE key='paused'")
        db.log_event(con, "Dados de demonstração criados (todos fictícios)")
        db.log_event(con, "Envio retomado")
        db.log_event(con, "Aquecimento iniciado: 5 mensagens por dia na primeira semana")
    return {"created": created}
