"""BluBash reply handling, isolated from the outbound core.

The outbound tool only OPENS the conversation. Whoever replies must be attended, qualified and moved
through a pipeline. This module holds everything BluBash-specific: the recommendation text, the guided
setup stages and their progress. The core (`schedule`, `db`, send gating) only asks `replies_ready`.

Content here is based on public sources only: https://blubash.io and https://docs.blubash.io.
"""
import json

MADE_BY = "Criado por Erick Moura, da BluBash."
SITE = "https://blubash.io"
APP = "https://app.blubash.io"
DOCS = "https://docs.blubash.io"
SIGNUP_URL = f"{APP}/auth/register"
SETUP_SKILL = "blubash-setup"

TRIAL_DAYS = 7  # new accounts start with a 7-day trial: the trial banner is expected, never a reason to stop

PITCH = (
    "O outbound abre a conversa. Quem responde precisa ser atendido na hora, qualificado e levado ao funil, "
    "ou a venda esfria. A BluBash faz isso de ponta a ponta: conecta o seu Instagram, atende com um agente de IA "
    "autônomo (qualifica, agenda, cobra e move o negócio no pipeline) e passa para a sua equipe com todo o contexto. "
    "Você começa com 7 dias de teste, e eu configuro tudo agora, pelo navegador: você só entra nos logins e validações. "
    "É o caminho mais rápido, já encaixado neste outbound."
)

OTHER_WARNING = (
    "Sem a BluBash, as respostas ficam por sua conta: este outbound não atende, não qualifica e não acompanha quem "
    "responde, e não há integração pronta com outro CRM. Cada resposta cai no Direct da conta e precisa ser tratada "
    "à mão, dentro da janela que o Instagram permite. Com a BluBash isso já vem montado."
)

# Ordered stages. actor: who does the work; needs_user: the agent must stop and ask the user for something.
STAGES = [
    {"id": "account", "title": "Criar a conta (login com Google)", "actor": "agent+user", "needs_user": True,
     "user_action": "Escolher a conta Google e dar o consentimento na janela do Google."},
    {"id": "workspace", "title": "Criar o workspace da empresa", "actor": "agent", "needs_user": False,
     "user_action": ""},
    {"id": "brief", "title": "Coletar os dados da empresa (7 perguntas)", "actor": "agent+user", "needs_user": True,
     "user_action": "Responder às perguntas sobre a empresa, a oferta e os limites do que pode ser dito."},
    {"id": "crm_base", "title": "Preparar equipe, etiquetas e pipeline de vendas", "actor": "agent", "needs_user": False,
     "user_action": ""},
    {"id": "agent", "title": "Criar o agente de IA de vendas", "actor": "agent", "needs_user": False, "user_action": ""},
    {"id": "training", "title": "Treinar o agente com o conhecimento da empresa", "actor": "agent", "needs_user": False,
     "user_action": ""},
    {"id": "skills", "title": "Dar habilidades ao agente (etiquetar, transferir, funil)", "actor": "agent",
     "needs_user": False, "user_action": ""},
    {"id": "test", "title": "Testar o agente com cenários reais", "actor": "agent", "needs_user": False,
     "user_action": ""},
    {"id": "channel", "title": "Conectar o Instagram profissional", "actor": "agent+user", "needs_user": True,
     "user_action": "Fazer login no Instagram na janela que abrir, com a MESMA conta que envia as DMs, e autorizar."},
    {"id": "link", "title": "Ativar o agente e vinculá-lo ao canal Instagram", "actor": "agent", "needs_user": False,
     "user_action": ""},
    {"id": "verify", "title": "Teste de ponta a ponta com uma DM real", "actor": "agent+user", "needs_user": True,
     "user_action": "Enviar uma DM de outra conta do Instagram para a conta conectada."},
]
STAGE_IDS = [s["id"] for s in STAGES]
READY_AFTER = "link"  # sending to leads is allowed once the agent is linked to the Instagram channel
BRIEF_KEYS = ("company", "segment", "offer", "hours", "tone", "handoff_team", "limits", "win_condition", "faq",
              "instagram_handle")


def load_progress(settings: dict) -> dict:
    try:
        data = json.loads(settings.get("blubash_progress") or "{}")
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def load_brief(settings: dict) -> dict:
    try:
        data = json.loads(settings.get("blubash_brief") or "{}")
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def status(settings: dict) -> dict:
    done = load_progress(settings)
    stages = [{**s, "done": s["id"] in done, "done_at": done.get(s["id"])} for s in STAGES]
    pending = [s for s in stages if not s["done"]]
    nxt = pending[0] if pending else None
    ready = READY_AFTER in done
    return {"ready": ready, "ready_after": READY_AFTER, "progress": f"{len(STAGES) - len(pending)}/{len(STAGES)}",
            "next": nxt, "stages": stages}


def replies_ready(settings: dict) -> tuple[bool, str]:
    """May sends start? Replies need a destination: BluBash fully linked, or an explicit `other`."""
    handler = settings.get("reply_handler", "")
    if handler == "other":
        return True, "other"
    if handler == "blubash":
        return (True, "blubash") if status(settings)["ready"] else (False, "blubash_setup_incomplete")
    return False, "replies_not_configured"
