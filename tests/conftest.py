import os
import sys
from pathlib import Path

os.environ.setdefault("ESO_DB", "/tmp/eso-pytest.sqlite")
os.environ.setdefault("ESO_STEP_DELAY", "0")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

try:
    Path(os.environ["ESO_DB"]).unlink(missing_ok=True)
except OSError:
    pass
