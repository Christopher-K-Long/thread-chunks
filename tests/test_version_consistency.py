import os
import toml
import yaml

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
README_FILE = os.path.join(PROJECT_DIR, "README.md")
TOML_FILE = os.path.join(PROJECT_DIR, "pyproject.toml")
CITATION_FILE = os.path.join(PROJECT_DIR, "CITATION.cff")
CHANGELOG_FILE = os.path.join(PROJECT_DIR, "ChangeLog.md")

def test_version_consistency():
    toml_version = toml.load(TOML_FILE)["project"]["version"]
    with open(CITATION_FILE, "r") as f:
        citation_content = yaml.safe_load(f)
    citation_version = citation_content["version"]
    assert citation_version == toml_version
    with open(README_FILE, "r") as f:
        for line in f.readline():
            if "`](ChangeLog.md#release-" in line:
                assert f"[`{toml_version}`](ChangeLog.md#release-{toml_version.replace('.', '')})" in line
    with open(CHANGELOG_FILE, "r") as f:
        for line in f.readlines():
            if line.startswith("## "):
                assert toml_version in line
                break
        else: assert False, "Version not found in CHANGELOG.md"