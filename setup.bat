@echo off
echo === Installing tracker-core ===
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
echo Done. Run: python -m src
