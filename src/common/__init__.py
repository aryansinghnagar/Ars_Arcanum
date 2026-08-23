"""Ars Arcanum Common Foundation Package"""
from .config import (
    DEFAULT_WORLDS_DIR,
    DEFAULT_CONFIG_DIR,
    AVAILABLE_THEMES,
    get_active_world_name,
    get_active_world_path,
    set_active_world_name,
    list_worlds,
    get_active_theme,
    set_active_theme,
)
from .lore_parser import (
    parse_frontmatter,
    format_frontmatter,
    EntityRecord,
    extract_world_entities,
    audit_manuscript_consistency,
)
from .git_ops import init_world_git, create_snapshot, get_commit_history
from .logger import log_writing_session, calculate_world_word_count
from .ui_helpers import show_notification, show_info_dialog, show_error_dialog, ask_text_input, ask_confirmation

__all__ = [
    "DEFAULT_WORLDS_DIR",
    "DEFAULT_CONFIG_DIR",
    "AVAILABLE_THEMES",
    "get_active_world_name",
    "get_active_world_path",
    "set_active_world_name",
    "list_worlds",
    "get_active_theme",
    "set_active_theme",
    "parse_frontmatter",
    "format_frontmatter",
    "EntityRecord",
    "extract_world_entities",
    "audit_manuscript_consistency",
    "init_world_git",
    "create_snapshot",
    "get_commit_history",
    "log_writing_session",
    "calculate_world_word_count",
    "show_notification",
    "show_info_dialog",
    "show_error_dialog",
    "ask_text_input",
    "ask_confirmation",
]
