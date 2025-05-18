# utils/parsers.py

import re
from typing import List, Dict, Any

# ─────────────────────────────────────────────────────────────
#  Modèles d’extraction par outil / « source » (clé source)
# ─────────────────────────────────────────────────────────────
_USER_PATTERNS = {
    "rid_brute":   re.compile(r"\\([\w.$-]+).*SidTypeUser"),
    "enum4linux":  re.compile(r"\+\s+([A-Za-z0-9_.-]+)\s+\(id:"),
}

_CRED_PATTERNS = {
    "spray":    re.compile(r"\[\+\]\s+\S+\\([\w.$-]+):(\S+)")
}

# ─────────────────────────────────────────────────────────────
#  Parseur “users”
# ─────────────────────────────────────────────────────────────
def parse_users(stdout: str, source: str) -> List[str]:
    """
    Retourne la liste unique et triée des logins AD trouvés
    dans la sortie d’un outil identifié par `source`.
    """
    pat = _USER_PATTERNS.get(source)
    if not pat:
        return []
    return sorted(set(pat.findall(stdout)))

# ─────────────────────────────────────────────────────────────
#  Parseur “creds”
# ─────────────────────────────────────────────────────────────

def parse_creds(stdout: str, source: str):
    pat = _CRED_PATTERNS.get(source)
    if not pat:
        return []
    return [(u,p) for u, p in pat.findall(stdout)]



# ─────────────────────────────────────────────────────────────
#  Registry global des parseurs
# ─────────────────────────────────────────────────────────────
PARSERS: Dict[str, Any] = {
    "users": parse_users,
    "creds": parse_creds,
}


