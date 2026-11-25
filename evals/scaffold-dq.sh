#!/usr/bin/env bash
# Gedeeld door de scaffold-scripts van de evals die dq echt laten draaien (geen case: hier staat geen case.yaml).
# Zet de Python-omgeving van dq klaar in de werkmap van de run, buiten de sandbox (die mag niet installeren en niet
# in de datamap van de plugin schrijven). De case wijst dq ernaartoe met EVAL_DQ_DATA: .dq-data.
# Gebruik in een case: source "$(dirname "$0")/../scaffold-dq.sh"; daarna staat dq klaar als functie `dq`.
set -euo pipefail
ROOT="${DQ_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
export EVAL_DQ_DATA="$PWD/.dq-data"

# De sandbox mag de thuismap niet lezen. Een Python van uv of pyenv staat daar, dus de venv komt op een
# systeem-Python (Homebrew, /usr/local, /usr) van versie 3.10 of nieuwer.
PY=""
for map in /opt/homebrew/bin /usr/local/bin /usr/bin; do
  for kandidaat in "$map"/python3.1[0-9] "$map"/python3; do
    [ -x "$kandidaat" ] || continue
    if "$kandidaat" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
      PY="$kandidaat"; break 2
    fi
  done
done
if [ -z "$PY" ]; then
  echo "Geen systeem-Python 3.10+ buiten de thuismap gevonden (Homebrew, /usr/local of /usr)." >&2
  exit 1
fi
"$PY" -m venv "$EVAL_DQ_DATA/venv"
dq() { "$ROOT/scripts/dq" "$@"; }
echo "Een korte tekst om de omgeving klaar te zetten." | dq tells >/dev/null
test -x "$EVAL_DQ_DATA/venv/bin/python"
