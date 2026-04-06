from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from home_view import render_home
from ui import setup_page, top_nav


setup_page("Cloudburst Risk Intelligence | Home")
top_nav("Home")
render_home()
