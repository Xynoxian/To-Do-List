"""
styles.py — Color palette, fonts, and style constants.
"""

COLORS = {
    "bg_dark": "#0d1117",
    "bg_card": "#161b22",
    "bg_secondary": "#21262d",
    "bg_tertiary": "#30363d",
    "accent": "#58a6ff",
    "accent_hover": "#79c0ff",
    "success": "#3fb950",
    "warning": "#d29922",
    "danger": "#f85149",
    "text_primary": "#f0f6fc",
    "text_secondary": "#8b949e",
    "border": "#30363d",
    # Priority colors
    "priority_low": "#3fb950",
    "priority_medium": "#58a6ff",
    "priority_high": "#d29922",
    "priority_urgent": "#f85149",
    # Status colors
    "status_pending": "#d29922",
    "status_in_progress": "#58a6ff",
    "status_done": "#3fb950",
    "status_late": "#f85149",
}

PRIORITY_COLORS = {
    "Low": COLORS["priority_low"],
    "Medium": COLORS["priority_medium"],
    "High": COLORS["priority_high"],
    "Urgent": COLORS["priority_urgent"],
}

STATUS_COLORS = {
    "Pending": COLORS["status_pending"],
    "In Progress": COLORS["status_in_progress"],
    "Done": COLORS["status_done"],
    "Late": COLORS["status_late"],
}

FONTS = {
    "heading": ("Segoe UI", 24, "bold"),
    "subheading": ("Segoe UI", 18, "bold"),
    "body": ("Segoe UI", 14),
    "body_bold": ("Segoe UI", 14, "bold"),
    "small": ("Segoe UI", 12),
    "tiny": ("Segoe UI", 10),
    "button": ("Segoe UI", 13, "bold"),
}

PRIORITY_EMOJI = {"Low": "🟢", "Medium": "🔵", "High": "🟡", "Urgent": "🔴"}
STATUS_EMOJI = {"Pending": "⏳", "In Progress": "🔄", "Done": "✅", "Late": "⏰"}
