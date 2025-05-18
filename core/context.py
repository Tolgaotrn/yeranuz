# core/context.py
from collections import defaultdict
from typing import Set, List, Dict, Any


class Context:
    """
    Stocke durablement tout ce que le framework découvre
    (users, IPs, creds, domains, vulns) + un buffer _pending pour
    valider les trouvailles à la fin des actions.
    """

    # ──────────────────────────────────────
    #  INIT
    # ──────────────────────────────────────
    def __init__(self) -> None:
        # artefacts validés
        self.users:   Set[str]            = set()
        self.ips:     Set[str]            = set()
        self.domains: Set[str]            = set()
        self.creds:   List[Dict[str, str]] = []   # {"user": "...", "password": "..."}
        self.vulns:   List[Dict[str, Any]] = []   # {"host": "...", "cve": "...", "cvss": "9.8"}

        # artefacts actifs
        self.active_user: str | None             = None
        self.active_ip:   str | None             = None
        self.active_cred: Dict[str, str] | None  = None

        # buffer temporaire (catégorie → set de valeurs)
        self._pending: defaultdict[str, set] = defaultdict(set)

    # ──────────────────────────────────────
    #  PENDING
    # ──────────────────────────────────────
    def stash(self, category: str, value: Any) -> None:
        """Appelé par run_tool pour empiler sans bloquer l’exécution."""
        self._pending[category].add(value)

    def _merge_items(self, cat: str, items: list[Any]) -> None:
        """Ajoute proprement des items à self.<cat> (set ou list)."""
        target = getattr(self, cat)
        if isinstance(target, set):
            target.update(items)
        elif isinstance(target, list):
            for itm in items:
                if itm not in target:
                    target.append(itm)
        else:
            print(f"[!] Catégorie {cat} non supportée")

    def commit_pending(self):
        for cat, vals in self._pending.items():
            if not vals:
                continue

            items = sorted(vals)

            # ↳ affichage dédié pour creds
            if cat == "creds":
                display = [f"{u}:{p}" for u, p in items]
            else:
                display = items

            print(f"\n[?] {cat.title()} trouvés :")
            for i, d in enumerate(display, 1):
                print(f"  {i:2}. {d}")

            choice = input("   ➜ Sélection (ex: 1,3-5,all,none) [all] : ").strip().lower() or "all"

            def _ids(sel): ...
            # --- après calcul de selected_items ---
            if choice in {"a", "all"}:
                selected = items
            elif choice in {"n", "none"}:
                selected = []
            else:
                try:
                    selected = [items[i-1] for i in _ids(choice)]
                except (ValueError, IndexError):
                    print("   ✗ Saisie invalide ; aucun ajout.")
                    selected = []

            # fusion
            if cat == "creds":
                for u, p in selected:
                    entry = {"user": u, "password": p}
                    if entry not in self.creds:
                        self.creds.append(entry)
            else:
                getattr(self, cat).update(selected)

        self._pending.clear()

    # ──────────────────────────────────────
    #  PICKERS
    # ──────────────────────────────────────
    def _pick(self, seq, label: str) -> Any | None:
        if not seq:
            print(f"Aucun {label} enregistré.")
            return None
        items = sorted(seq)
        for i, itm in enumerate(items, 1):
            print(f"{i}. {itm}")
        try:
            idx = int(input(f"Choix du {label} : ")) - 1
            chosen = items[idx]
            print(f"[+] {label.capitalize()} actif : {chosen}")
            return chosen
        except (ValueError, IndexError):
            print("Saisie invalide.")
            return None

    def select_user(self):
        self.active_user = self._pick(self.users, "user")

    def select_ip(self):
        self.active_ip = self._pick(self.ips, "IP")

    def select_cred(self):
        if not self.creds:
            print("Aucun credential enregistré.")
            return
        for i, cred in enumerate(self.creds, 1):
            print(f"{i}. {cred['user']}:{cred['password']}")
        try:
            idx = int(input("Choix du credential : ")) - 1
            self.active_cred = self.creds[idx]
            print(f"[+] Credential actif : {self.active_cred['user']}:{self.active_cred['password']}")
        except (ValueError, IndexError):
            print("Saisie invalide.")

    # ──────────────────────────────────────
    #  DEBUG / AFFICHAGE
    # ──────────────────────────────────────
    def show(self):
        print("\n--- Context ---")
        print("Users   :", ", ".join(sorted(self.users)) or "∅")
        print("IPs     :", ", ".join(sorted(self.ips)) or "∅")
        print("Domains :", ", ".join(sorted(self.domains)) or "∅")
        if self.creds:
            print("Creds   :", ", ".join(f"{c['user']}:{c['password']}" for c in self.creds))
        if self.vulns:
            print(f"Vulns   : {len(self.vulns)} enregistrées")
        print("----------------\n")
