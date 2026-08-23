"""
Ars Arcanum — Test Suite Configuration & Pytest Fixtures
"""

import sys
import shutil
import tempfile
import uuid
from pathlib import Path
import pytest

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import common.config as cfg
from gui.ars_wizard.scaffold import scaffold_world_project


@pytest.fixture
def temp_world_env(monkeypatch):
    """Fixture providing an isolated temporary world directory environment."""
    temp_dir = Path(tempfile.mkdtemp(prefix="ars_test_"))
    temp_worlds = temp_dir / "Worlds"
    temp_config = temp_dir / ".config" / "ars-arcanum"
    temp_worlds.mkdir(parents=True)
    temp_config.mkdir(parents=True)

    monkeypatch.setattr(cfg, "DEFAULT_WORLDS_DIR", temp_worlds)
    monkeypatch.setattr(cfg, "DEFAULT_CONFIG_DIR", temp_config)

    yield temp_worlds, temp_config

    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_world_dir(temp_world_env):
    """Fixture creating a unique isolated test world project per test."""
    temp_worlds, _ = temp_world_env
    unique_name = f"TestWorld_{uuid.uuid4().hex[:6]}"
    world_dir = scaffold_world_project(unique_name, "Fantasy", ["sandersonian_magic"])
    return world_dir
