from __future__ import annotations

import sys

if __name__ == "__main__" and "--personalos-upgrade" in sys.argv:
    sys.argv = [sys.argv[0], *[arg for arg in sys.argv[1:] if arg != "--personalos-upgrade"]]
    from scripts.personalos_mvp_upgrade import main as personalos_upgrade_main
    raise SystemExit(personalos_upgrade_main())

print("PersonalOS installer placeholder.")
print("Use: python Install.py --personalos-upgrade --enroll")
