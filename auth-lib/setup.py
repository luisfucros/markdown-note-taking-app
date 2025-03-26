from pathlib import Path
from setuptools import setup, find_packages
import ast

BASE_DIR = Path(__file__).parent

requirements_file = BASE_DIR / "requirements.txt"
if requirements_file.exists():
    with requirements_file.open("r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
else:
    requirements = []

version_file = BASE_DIR / "auth_lib" / "version.py"
with version_file.open("r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            version = ast.literal_eval(line.split("=")[1].strip())
            break
    else:
        raise ValueError("Version information not found in auth_lib/version.py")

setup(
    name="auth_lib",
    version=version,
    packages=find_packages(),
    install_requires=requirements,
)
