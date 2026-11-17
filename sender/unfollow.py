#!/usr/bin/env python3
"""Protótipo supervisionado. Uso: python3 sender/unfollow.py <handle>. Deixa de seguir o perfil e confirma que o botão voltou para 'Seguir'."""
import os, re, subprocess, sys

S = os.environ.get("IG_SESSION", "ig-session")
h = sys.argv[1]


def ab(*args):
    r = subprocess.run(["agent-browser", "--headed", "--session", S, *args], capture_output=True, text=True)
    return (r.stdout or "") + (r.stderr or "")


def ref(snap, pattern):
    m = re.search(pattern + r'.*?\[ref=(e\d+)\]', snap)
    return m.group(1) if m else None


ab("open", f"https://www.instagram.com/{h}/")
ab("wait", "4500")
snap = ab("snapshot", "-i")
b = ref(snap, r'button "Seguindo')
if not b:
    state = "JA_NAO_SEGUE" if re.search(r'button "Seguir"', snap) else "SEM_BOTAO"
    print(h, state)
    sys.exit(0)
ab("click", f"@{b}")
ab("wait", "2000")
snap2 = ab("snapshot", "-i")
u = ref(snap2, r'(button|menuitem|generic|link) "Deixar de seguir"') or ref(snap2, r'"Deixar de seguir"')
if not u:
    print(h, "SEM_MENU_DEIXAR_DE_SEGUIR")
    sys.exit(0)
ab("click", f"@{u}")
ab("wait", "2500")
snap3 = ab("snapshot", "-i")
# Alguns perfis pedem confirmação em um diálogo
c = ref(snap3, r'button "Deixar de seguir"')
if c:
    ab("click", f"@{c}")
    ab("wait", "2500")
    snap3 = ab("snapshot", "-i")
print(h, "UNFOLLOWED" if re.search(r'button "Seguir"', snap3) and not re.search(r'button "Seguindo', snap3) else "VERIFICAR")
