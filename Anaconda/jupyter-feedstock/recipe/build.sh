export PYTHONDONTWRITEBYTECODE=1
pip install --no-deps .
# Conflicts with jupyter_core which is a transitive dep.
cd $SP_DIR
rm jupyter.py
rm -f jupyter.pyc
if [[ -d __pycache__ ]]; then
   rm -rf __pycache__
fi
