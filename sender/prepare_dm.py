#!/usr/bin/env python3
"""Protótipo supervisionado. Uso: python3 sender/prepare_dm.py <handle>. Abre o perfil, abre o chat e digita a mensagem em parágrafos (Shift+Enter). NÃO envia."""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

D = os.path.expanduser(os.environ.get("OUTBOUND_HOME", "~/.outbound-leads"))
os.makedirs(os.path.join(D, "screens"), exist_ok=True)
S = os.environ.get("IG_SESSION", "ig-session")
h = sys.argv[1]
msg = json.load(open(f"{D}/seed_messages.json"))[h]


def ab(*args):
    r = subprocess.run(["agent-browser", "--headed", "--session", S, *args], capture_output=True, text=True, cwd="/tmp")
    return (r.stdout or "") + (r.stderr or "")


def ref(snap, pattern):
    m = re.search(pattern + r'.*?\[ref=(e\d+)\]', snap)
    return m.group(1) if m else None


ab("open", f"https://www.instagram.com/{h}/")
ab("wait", "4500")
snap = ab("snapshot", "-i")
for line in snap.splitlines():
    if re.search(r'heading "|button "(Seguir|Seguindo|Enviar mensagem|Mensagem)"', line):
        print(line.strip())
        if line.strip().startswith("- heading"):
            pass
f = ref(snap, r'button "Seguir"')
if f and not os.environ.get("NOFOLLOW"):
    ab("click", f"@{f}")
    ab("wait", "3000")
    snap = ab("snapshot", "-i")
    print("FOLLOW:", "Seguindo" if re.search(r'button "(Seguindo|Solicitado)"', snap) else "NAO CONFIRMADO")
b = ref(snap, r'button "Enviar mensagem"')
if not b:
    print("NOBTN")
    ab("screenshot", f"{D}/screens/ig_{h}.png")
    sys.exit(0)
tb = None
for attempt in range(2):
    ab("click", f"@{b}")
    ab("wait", "3500")
    snap2 = ab("snapshot", "-i")
    tb = ref(snap2, r'textbox "Mensagem\.\.\."')
    if tb:
        break
    ab("reload")
    ab("wait", "4500")
    snap = ab("snapshot", "-i")
    b = ref(snap, r'button "Enviar mensagem"') or b
if not tb:
    print("NOTEXTBOX")
    ab("screenshot", f"{D}/screens/ig_{h}.png")
    sys.exit(0)
ab("click", f"@{tb}")
paras = msg.split("\n\n")
for i, p in enumerate(paras):
    ab("keyboard", "inserttext", p)
    if i < len(paras) - 1:
        ab("press", "Shift+Enter")
        ab("press", "Shift+Enter")
ab("wait", "800")
ab("screenshot", f"{D}/screens/ig_{h}.png")
print("READY", h)
