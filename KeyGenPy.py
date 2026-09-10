#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KeyGenPy - Professioneller Passwort-Generator
Dark Mode GUI mit Logo und App-Icon
"""

import csv
import ipaddress
import json
import math
import os
import random
import re
import string
import sys
import textwrap

from datetime import datetime
from urllib.parse import urlparse

from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QScrollArea,  # neu
    QSpinBox,
    QGroupBox,
    QTextEdit,
    QMessageBox,
    QSizePolicy,
    QFrame,
    QSplitter,
    QFileDialog,
    QInputDialog,
    QMenu,
    QComboBox,
)
from PyQt6.QtCore import Qt, QTimer, QSize, QSettings, QRect, pyqtSignal
from PyQt6.QtGui import (
    QFont,
    QIcon,
    QPixmap,
    QClipboard,
    QColor,
    QPalette,
    QKeySequence,
    QAction,
    QPainter,
    QContextMenuEvent,
)

# ===================================================
# KONFIGURATION
# =======================================================

script_dir = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(script_dir, "BinhDiez.png")
APP_ICON_PATH = os.path.join(script_dir, "KeyGenPy.png")

DEFAULT_PASSWORD_LENGTH = 20
MAX_PASSWORD_LENGTH = 2048
MIN_PASSWORD_LENGTH = 4
DEFAULT_PASSWORD_COUNT = 1
MAX_PASSWORD_COUNT = 20
DEFAULT_GROUP_SIZE = 5
DEFAULT_SEPARATOR = "-"

# Sonderzeichen-Modi (für die Combobox)
SPECIAL_MODES = {
    "many": "viele (Standard)",
    "few": "wenige",
    "single": "einzelne",
    "one_per_group": "eins pro Gruppe",
    "only_one": "nur eins",
}

COLORS = {
    "primary": "#1a1a2e",
    "secondary": "#162447",
    "accent": "#0f3460",
    "highlight": "#0D47A1",
    "success": "#00C853",
    "warning": "#FFC107",
    "danger": "#FF2D2D",
    "text": "#ffffff",
    "text_secondary": "#B0B8C1",
    "border": "#1f4068",
    "background": "#1e1e2e",
    "strong10": "#FF1744",
    "strong20": "#FF3D00",
    "strong30": "#FF6D00",
    "strong40": "#FFAB00",
    "strong50": "#FFD600",
    "strong60": "#D4E157",
    "strong70": "#9CCC65",
    "strong80": "#66BB6A",
    "strong90": "#26A69A",
    "strong100": "#2E7D32",
}

# ======================================================
# CUSTOM WIDGETS
# ======================================================


class PasswordLineEdit(QLineEdit):
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.clicked.emit()

    def show_context_menu(self, pos):
        menu = QMenu(self)
        window = self.window()
        if isinstance(window, KeyGenPyWindow):
            copy_action = QAction("In Zwischenablage kopieren", self)
            copy_action.triggered.connect(window.copy_password)
            menu.addAction(copy_action)
            save_action = QAction("In Verlauf übernehmen", self)
            save_action.triggered.connect(window.save_to_history)
            menu.addAction(save_action)
            if sys.platform == "darwin":
                icloud_action = QAction("In Schlüsselbund speichern", self)
                icloud_action.triggered.connect(window.save_to_icloud)
                menu.addAction(icloud_action)
        menu.exec(self.mapToGlobal(pos))


class PasswordStrengthIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(8)
        self.strength = 0

    def set_strength(self, strength):
        self.strength = max(0, min(100, strength))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg_color = QColor(60, 60, 60)
        painter.fillRect(self.rect(), bg_color)
        width = int(self.width() * self.strength / 100)
        if self.strength < 20:
            color = QColor(COLORS["strong10"])
        elif self.strength < 30:
            color = QColor(COLORS["strong20"])
        elif self.strength < 40:
            color = QColor(COLORS["strong30"])
        elif self.strength < 50:
            color = QColor(COLORS["strong40"])
        elif self.strength < 60:
            color = QColor(COLORS["strong50"])
        elif self.strength < 70:
            color = QColor(COLORS["strong60"])
        elif self.strength < 80:
            color = QColor(COLORS["strong70"])
        elif self.strength < 90:
            color = QColor(COLORS["strong80"])
        else:
            color = QColor(COLORS["strong100"])
        strength_rect = QRect(0, 0, width, self.height())
        painter.fillRect(strength_rect, color)
        painter.setPen(QColor(100, 100, 100))
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)


# =======================================================
# HAUPTFENSTER
# =======================================================


class KeyGenPyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.generated_passwords = []
        self.raw_password = ""
        self.formatted_password = ""
        self.settings = QSettings("BinhDiez", "KeyGen")
        self.current_charset = ""
        self.password_added_to_history = False
        self._original_copy_text = "In Zwischenablage"
        self.copy_timer = None

        self.setup_ui()
        self.load_settings()

        # nach setup_ui
        # Bildschirmgröße ermitteln
        screen = QApplication.primaryScreen().availableGeometry()
        screen_width = screen.width()
        screen_height = screen.height()

        # Mindestgröße anpassen (darf nicht größer als der Bildschirm sein)
        min_w = min(600, screen_width)
        min_h = min(400, screen_height)
        self.setMinimumSize(min_w, min_h)

        # Fenstergröße auf 90 % der Bildschirmgröße setzen (aber nicht kleiner als die Mindestgröße)
        new_width = max(min_w, int(screen_width * 0.65))
        new_height = max(min_h, int(screen_height * 0.9))
        self.resize(new_width, new_height)

    def setup_ui(self):
        self.setWindowTitle("KeyGenPy - Professioneller Passwort-Generator")

        if os.path.exists(APP_ICON_PATH):
            self.setWindowIcon(QIcon(APP_ICON_PATH))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.create_header(main_layout)
        self.create_content_area(main_layout)
        self.apply_dark_theme()
        self.setup_shortcuts()

        QTimer.singleShot(100, self.generate_password)

    def setup_shortcuts(self):
        gen_shortcut = QAction("Generate", self)
        gen_shortcut.setShortcut(QKeySequence("Ctrl+G"))
        gen_shortcut.triggered.connect(self.generate_password)
        self.addAction(gen_shortcut)
        copy_shortcut = QAction("Copy", self)
        copy_shortcut.setShortcut(QKeySequence("Ctrl+Shift+C"))
        copy_shortcut.triggered.connect(self.copy_password)
        self.addAction(copy_shortcut)

    def create_header(self, parent_layout):
        header_frame = QFrame()
        header_frame.setFixedHeight(100)
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS["primary"]};
                border-bottom: 2px solid {COLORS["accent"]};
            }}
        """)
        header_layout = QGridLayout(header_frame)
        header_layout.setContentsMargins(20, 10, 20, 10)

        if os.path.exists(LOGO_PATH):
            logo_label = QLabel()
            logo_pixmap = QPixmap(LOGO_PATH)
            logo_pixmap = logo_pixmap.scaled(
                100,
                100,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo_label.setPixmap(logo_pixmap)
            logo_label.setAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            header_layout.addWidget(logo_label, 0, 0)

        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        main_title = QLabel("KeyGenPy")
        main_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_title.setStyleSheet(f"""
            QLabel {{
                color: {COLORS["text"]};
                font-size: 32px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                letter-spacing: 3px;
                margin: 5px;
            }}
        """)
        subtitle = QLabel("Professioneller Passwort-Generator")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"""
            QLabel {{
                color: {COLORS["text"]};
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                letter-spacing: 1.5px;
            }}
        """)
        title_layout.addWidget(main_title)
        title_layout.addWidget(subtitle)
        header_layout.addWidget(title_container, 0, 1)

        if os.path.exists(APP_ICON_PATH):
            icon_label = QLabel()
            icon_pixmap = QPixmap(APP_ICON_PATH)
            icon_pixmap = icon_pixmap.scaled(
                80,
                80,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            icon_label.setPixmap(icon_pixmap)
            icon_label.setAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
            header_layout.addWidget(icon_label, 0, 2)

        header_layout.setColumnStretch(0, 1)
        header_layout.setColumnStretch(1, 2)
        header_layout.setColumnStretch(2, 1)
        parent_layout.addWidget(header_frame)

    def create_content_area(self, parent_layout):
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #2d3746;
                width: 2px;
            }
            QSplitter::handle:hover {
                background-color: #e94560;
            }
        """)

        # # --- Linkes Panel (Control) in ScrollArea ---
        control_panel = self.create_control_panel()
        scroll = QScrollArea()

        # nur vertical scrollen
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        scroll.setWidgetResizable(False)  # Feste Breite

        scroll.setWidget(control_panel)

        # Die natürliche Höhe des Panels als Mindesthöhe setzen, damit es bei kleinerem Viewport nicht gestaucht wird.
        # Ein Timer stellt sicher, dass das Layout bereits berechnet ist.
        QTimer.singleShot(
            0, lambda: control_panel.setMinimumHeight(control_panel.sizeHint().height())
        )
        splitter.addWidget(scroll)

        # --- Rechtes Panel (History) unverändert ---
        right_panel = self.create_history_panel()
        splitter.addWidget(right_panel)

        splitter.setSizes([600, 400])
        parent_layout.addWidget(splitter)

    def create_control_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # ----- Generiertes Passwort -----
        password_group = QGroupBox("Generiertes Passwort")
        password_group.setStyleSheet(self.get_groupbox_style(COLORS["accent"]))
        password_layout = QVBoxLayout(password_group)

        self.password_display = PasswordLineEdit()
        self.password_display.setReadOnly(False)
        self.password_display.setAlignment(Qt.AlignmentFlag.AlignLeft)
        font_family = "Monaco" if sys.platform == "darwin" else "Consolas"
        self.password_display.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS["secondary"]};
                color: {COLORS["text"]};
                border: 2px solid {COLORS["border"]};
                border-radius: 8px;
                padding: 15px;
                font-family: '{font_family}', 'monospace';
                font-size: 18px;
                font-weight: bold;
                selection-background-color: {COLORS["highlight"]};
            }}
        """)
        self.password_display.clicked.connect(self.copy_password)
        self.password_display.editingFinished.connect(self.on_password_edited)
        self.password_display.textChanged.connect(self.on_text_changed)
        self.password_display.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.password_display.setMinimumHeight(50)
        password_layout.addWidget(self.password_display)

        # Stärke
        strength_layout = QHBoxLayout()
        strength_layout.addWidget(QLabel("Stärke:"))
        self.strength_indicator = PasswordStrengthIndicator()
        self.strength_indicator.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        strength_layout.addWidget(self.strength_indicator)
        self.strength_label = QLabel("")
        self.strength_label.setStyleSheet(
            f"color: {COLORS['success']}; font-weight: bold;"
        )
        strength_layout.addWidget(self.strength_label)
        strength_layout.addSpacing(20)
        strength_layout.addWidget(QLabel("Entropie:"))
        self.entropy_label = QLabel("0 Bit")
        self.entropy_label.setStyleSheet(
            f"color: {COLORS['text_secondary']}; font-weight: normal;"
        )
        strength_layout.addWidget(self.entropy_label)
        password_layout.addLayout(strength_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.generate_btn = self.create_button(
            "Neu generieren", COLORS["highlight"], self.generate_password
        )
        self.copy_btn = self.create_button(
            "In Zwischenablage", COLORS["border"], self.copy_password
        )
        button_layout.addWidget(self.generate_btn)
        button_layout.addWidget(self.copy_btn)
        if sys.platform == "darwin":
            self.icloud_btn = self.create_button(
                "In Schlüsselbund", "#007AFF", self.save_to_icloud
            )
            button_layout.addWidget(self.icloud_btn)
        password_layout.addLayout(button_layout)
        layout.addWidget(password_group)

        # ----- Einstellungen -----
        settings_group = QGroupBox("Passwort-Einstellungen")
        settings_group.setStyleSheet(self.get_groupbox_style(COLORS["primary"]))
        settings_layout = QGridLayout(settings_group)
        settings_layout.setVerticalSpacing(10)

        # Länge
        settings_layout.addWidget(QLabel("Länge:"), 0, 0)
        self.length_spin = QSpinBox()
        self.length_spin.setRange(MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH)
        self.length_spin.setValue(DEFAULT_PASSWORD_LENGTH)
        self.length_spin.setStyleSheet(f"""
            QSpinBox {{
                background-color: {COLORS["secondary"]};
                color: {COLORS["text"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 4px;
                padding: 5px;
            }}
        """)
        settings_layout.addWidget(self.length_spin, 0, 1)

        # Gruppierung
        settings_layout.addWidget(QLabel("Gruppierung:"), 0, 2)
        self.group_size_spin = QSpinBox()
        self.group_size_spin.setRange(0, 10)
        self.group_size_spin.setValue(DEFAULT_GROUP_SIZE)
        self.group_size_spin.setSpecialValueText("Keine")
        self.group_size_spin.setStyleSheet(self.length_spin.styleSheet())
        self.group_size_spin.valueChanged.connect(self.format_password)
        self.group_size_spin.valueChanged.connect(self._update_special_mode_combo)
        settings_layout.addWidget(self.group_size_spin, 0, 3)

        # Trennzeichen
        settings_layout.addWidget(QLabel("Trennzeichen:"), 0, 4)
        self.separator_input = QLineEdit()
        self.separator_input.setMaxLength(1)
        self.separator_input.setText(DEFAULT_SEPARATOR)
        self.separator_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS["secondary"]};
                color: {COLORS["text"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 4px;
                padding: 5px;
                max-width: 40px;
            }}
        """)
        self.separator_input.textChanged.connect(self.format_password)
        settings_layout.addWidget(self.separator_input, 0, 5)

        # Info-Label
        self.length_info_label = QLabel("")
        self.length_info_label.setStyleSheet(
            f"color: {COLORS['text_secondary']}; font-size: 11px;"
        )
        settings_layout.addWidget(self.length_info_label, 1, 0, 1, 6)
        self.length_spin.valueChanged.connect(self.update_length_info)

        # Zeichentypen
        row = 2
        self.uppercase_check = QCheckBox("Großbuchstaben (A-Z)")
        self.uppercase_check.setChecked(True)
        settings_layout.addWidget(self.uppercase_check, row, 0, 1, 2)

        self.lowercase_check = QCheckBox("Kleinbuchstaben (a-z)")
        self.lowercase_check.setChecked(True)
        settings_layout.addWidget(self.lowercase_check, row + 1, 0, 1, 2)

        self.digits_check = QCheckBox("Zahlen (0-9)")
        self.digits_check.setChecked(True)
        settings_layout.addWidget(self.digits_check, row + 2, 0, 1, 2)

        self.uppercase_check.toggled.connect(self._rebuild_special_mode_combo)
        self.lowercase_check.toggled.connect(self._rebuild_special_mode_combo)
        self.digits_check.toggled.connect(self._rebuild_special_mode_combo)

        # Sonderzeichen – Checkbox in Spalte 0-1, Combobox in Spalte 3-4
        self.symbols_check = QCheckBox("Sonderzeichen (!@#$%^&*)          -->")
        self.symbols_check = QCheckBox("Sonderzeichen (!@#$%^&*)        ⟶")  #
        self.symbols_check.setChecked(True)
        self.symbols_check.toggled.connect(self.generate_password)
        self.symbols_check.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        settings_layout.addWidget(self.symbols_check, row + 3, 0, 1, 3)

        self.special_mode_combo = QComboBox()
        self.special_mode_combo.addItem("viele (Standard)", "many")
        self.special_mode_combo.addItem("wenige", "few")
        self.special_mode_combo.addItem("einzelne", "single")
        self.special_mode_combo.addItem("eins pro Gruppe", "one_per_group")
        self.special_mode_combo.addItem("nur eins", "only_one")
        self.special_mode_combo.setCurrentIndex(0)
        self.special_mode_combo.currentIndexChanged.connect(self.generate_password)
        self.special_mode_combo.setToolTip(
            "Häufigkeit der Sonderzeichen im Passwort.\n"
            "Bei 'eins pro Gruppe' wird die Gruppierung benötigt."
        )
        # Combobox nimmt den verfügbaren Platz in ihrer Spalte ein
        self.special_mode_combo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        settings_layout.addWidget(self.special_mode_combo, row + 3, 3, 1, 3)

        # Verbinde Checkboxen mit sofortiger Generierung
        self.uppercase_check.toggled.connect(self.generate_password)
        self.lowercase_check.toggled.connect(self.generate_password)
        self.digits_check.toggled.connect(self.generate_password)

        # Erweiterte Optionen
        advanced_group = QGroupBox("Erweiterte Optionen")
        advanced_group.setStyleSheet(self.get_groupbox_style(COLORS["secondary"]))
        advanced_layout = QVBoxLayout(advanced_group)

        # Ausgeschlossene Zeichen
        exclude_layout = QHBoxLayout()
        exclude_layout.addWidget(QLabel("Ausgeschlossene Zeichen:"))
        self.exclude_input = QLineEdit()
        self.exclude_input.setPlaceholderText("z.B. 0O1lI")
        self.exclude_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS["secondary"]};
                color: {COLORS["text"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 4px;
                padding: 5px;
            }}
        """)
        self.exclude_input.textChanged.connect(self.generate_password)
        exclude_layout.addWidget(self.exclude_input, 1)
        advanced_layout.addLayout(exclude_layout)

        # Mehrere Passwörter
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("Mehrere generieren:"))
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, MAX_PASSWORD_COUNT)
        self.count_spin.setValue(DEFAULT_PASSWORD_COUNT)
        self.count_spin.setStyleSheet(self.length_spin.styleSheet())
        count_layout.addWidget(self.count_spin)
        advanced_layout.addLayout(count_layout)

        # Automatisch kopieren
        auto_copy_layout = QHBoxLayout()
        self.auto_copy_check = QCheckBox(
            "Bei Generierung in Zwischenablage kopieren und im Verlauf anzeigen  "
        )
        self.auto_copy_check.setChecked(False)
        auto_copy_layout.addWidget(self.auto_copy_check)
        advanced_layout.addLayout(auto_copy_layout)

        settings_layout.addWidget(advanced_group, row + 4, 0, 2, 6)
        settings_layout.setRowStretch(row + 6, 1)

        layout.addWidget(settings_group)

        self._rebuild_special_mode_combo()
        return panel

    def create_history_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        header_layout = QHBoxLayout()
        header_label = QLabel("Passwort-Verlauf")
        header_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS["text"]};
                font-size: 18px;
                font-weight: bold;
            }}
        """)
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        # Info-Button – dezent
        info_btn = QPushButton("ⓘ")
        info_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666;
                border: none;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #aaa;
            }
        """)
        info_btn.setFixedSize(40, 40)
        info_btn.clicked.connect(self.show_about_dialog)
        header_layout.addWidget(info_btn)

        layout.addLayout(header_layout)

        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS["secondary"]};
                color: {COLORS["text"]};
                border: 2px solid {COLORS["border"]};
                border-radius: 8px;
                padding: 10px;
                font-family: 'Monaco', 'Consolas', monospace;
                font-size: 12px;
            }}
        """)
        layout.addWidget(self.history_text)

        export_layout = QHBoxLayout()
        export_btn = QPushButton("Exportieren")
        export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["accent"]};
                color: {COLORS["text"]};
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 12px;
                min-height: 15px;
            }}
            QPushButton:hover {{
                background-color: {self.adjust_color(COLORS["accent"], 20)};
            }}
            QPushButton::menu-indicator {{
                image: none;
            }}
        """)
        menu = QMenu()
        menu.addAction("JSON", self.export_json)
        menu.addAction("TXT", self.export_txt)
        menu.addAction("CSV", self.export_csv)
        export_btn.setMenu(menu)
        export_layout.addWidget(export_btn)

        self.clear_btn = self.create_button(
            "Verlauf löschen", COLORS["danger"], self.clear_history
        )
        self.clear_btn.setFixedWidth(120)
        export_layout.addWidget(self.clear_btn)
        export_layout.addStretch()
        layout.addLayout(export_layout)

        return panel

    def create_button(self, text, color, callback):
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: {COLORS["text"]};
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 12px;
                min-height: 15px;
            }}
            QPushButton:hover {{
                background-color: {self.adjust_color(color, 20)};
            }}
            QPushButton:pressed {{
                background-color: {self.adjust_color(color, -20)};
                padding: 11px 14px 9px 16px;
            }}
        """)
        btn.clicked.connect(callback)
        return btn

    def adjust_color(self, hex_color, amount):
        hex_color = hex_color.lstrip("#")
        r, g, b = (
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16),
        )
        r = max(0, min(255, r + amount))
        g = max(0, min(255, g + amount))
        b = max(0, min(255, b + amount))
        return f"#{r:02x}{g:02x}{b:02x}"

    def get_groupbox_style(self, color):
        return f"""
            QGroupBox {{
                color: {COLORS["text"]};
                border: 2px solid {color};
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
                font-size: 14px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: {COLORS["text"]};
            }}
        """

    def apply_dark_theme(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 46))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 38))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(35, 35, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(40, 40, 60))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(40, 40, 60))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(80, 130, 255))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(233, 69, 96))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        dark_palette.setColor(
            QPalette.ColorGroup.Disabled,
            QPalette.ColorRole.WindowText,
            QColor(127, 127, 127),
        )
        dark_palette.setColor(
            QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(127, 127, 127)
        )
        dark_palette.setColor(
            QPalette.ColorGroup.Disabled,
            QPalette.ColorRole.ButtonText,
            QColor(127, 127, 127),
        )
        self.setPalette(dark_palette)

        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {COLORS["background"]}; }}
            QCheckBox {{
                color: {COLORS["text"]};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {COLORS["border"]};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS["highlight"]};
                border-color: {COLORS["highlight"]};
            }}
            QCheckBox::indicator:unchecked {{
                background-color: {COLORS["secondary"]};
            }}
            QLabel {{ color: {COLORS["text"]}; }}
            QSpinBox, QLineEdit {{
                background-color: {COLORS["secondary"]};
                color: {COLORS["text"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 4px;
                padding: 5px;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background-color: {COLORS["border"]};
                border: none;
                border-radius: 2px;
                width: 16px;
            }}
            QSpinBox::up-arrow, QSpinBox::down-arrow {{
                width: 8px;
                height: 8px;
            }}
            QGroupBox {{
                color: {COLORS["text"]};
                font-weight: bold;
            }}
            QComboBox {{
                background-color: {COLORS["secondary"]};
                color: {COLORS["text"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 4px;
                padding: 5px;
            }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox::down-arrow {{ image: none; }}
        """)

    # deutsch + englisch
    def show_about_dialog(self):

        dialog = QDialog(self)
        dialog.setWindowTitle("Über KeyGenPy")
        dialog.setMinimumWidth(600)
        dialog.setMinimumHeight(400)

        layout = QVBoxLayout(dialog)

        # Header mit Logo und Titel
        self.create_header(layout)

        # 2. und 3. Kopfzeile
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)

        version_label = QLabel("Version 1.0.1")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS["text"]};
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                letter-spacing: 1.5px;
            }}
        """)
        copyright_label = QLabel("Copyright (c) 2026 BinhDiez")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS["text"]};
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                letter-spacing: 1.5px;
            }}
        """)

        website_label = QLabel("https://github.com/BinhDiez")
        website_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        website_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS["strong70"]};
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                letter-spacing: 1.5px;
            }}
        """)
        title_layout.addWidget(version_label)
        title_layout.addWidget(copyright_label)
        title_layout.addWidget(website_label)
        layout.addWidget(title_container)

        # Text – zuerst Deutsch, dann Englisch
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(textwrap.dedent("""
            === Deutsche Version ===

            MIT-Lizenz

            Copyright (c) 2026 BinhDiez

            Hiermit wird jeder Person, die eine Kopie dieser Software und der zugehörigen
            Dokumentationsdateien (die "Software") erhält, unentgeltlich die Erlaubnis erteilt, die Software
            ohne Einschränkung zu nutzen, einschließlich und ohne Einschränkung der Rechte zur Nutzung, Kopie, Änderung, Zusammenführung, Veröffentlichung, Verteilung, Unterlizenzierung und/oder zum Verkauf von Kopien der Software, und Personen, denen die Software zur Verfügung gestellt wird, dies unter den folgenden Bedingungen zu gestatten:
            Der obige Urheberrechtshinweis und dieser Erlaubnishinweis müssen in allen Kopien oder wesentlichen Teilen der Software enthalten sein.

            DIE SOFTWARE WIRD OHNE JEGLICHE AUSDRÜCKLICHE ODER STILLSCHWEIGENDE GARANTIE BEREITGESTELLT, EINSCHLIESSLICH, ABER NICHT BESCHRÄNKT AUF DIE GARANTIEN DER MARKTGÄNGIGKEIT, DER EIGNUNG FÜR EINEN BESTIMMTEN ZWECK UND DER NICHTVERLETZUNG VON RECHTEN. IN KEINEM FALL SIND DIE AUTOREN ODER RECHTSINHABER FÜR JEGLICHE ANSPRÜCHE, SCHÄDEN ODER ANDEREN HAFTUNGEN VERANTWORTLICH, OB IN EINER VERTRAGS- ODER DELIKTSHAFTUNG ODER ANDERWEITIG, DIE AUS DER ODER IN VERBINDUNG MIT DER SOFTWARE ODER DER NUTZUNG ODER ANDEREN HANDLUNGEN MIT DER SOFTWARE ENTSTEHEN.

            ---

            Diese Software verwendet PyQt6, das urheberrechtlich (c) Riverbank Computing Limited geschützt ist.
            PyQt6 ist freie Software: Sie können es unter den Bedingungen der GNU General Public License, wie von der Free Software Foundation veröffentlicht, entweder Version 3 der Lizenz oder (nach Ihrer Wahl) jeder späteren Version, weiterverteilen und/oder modifizieren.
            PyQt6 wird in der Hoffnung verteilt, dass es nützlich sein wird, aber OHNE JEGLICHE GARANTIE; sogar ohne die stillschweigende Garantie der MARKTGÄNGIGKEIT oder der EIGNUNG FÜR EINEN BESTIMMTEN ZWECK. Weitere Einzelheiten finden Sie in der GNU General Public License.
            Sie sollten eine Kopie der GNU General Public License zusammen mit PyQt6 erhalten haben. Falls nicht, siehe <http://www.gnu.org/licenses/>.

            === English Version ===

            MIT License

            Copyright (c) 2026 BinhDiez

            Permission is hereby granted, free of charge, to any person obtaining a copy
            of this software and associated documentation files (the "Software"), to deal
            in the Software without restriction, including without limitation the rights
            to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
            copies of the Software, and to permit persons to whom the Software is
            furnished to do so, subject to the following conditions:
            The above copyright notice and this permission notice shall be included in all
            copies or substantial portions of the Software.

            THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
            IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
            FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
            THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
            LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
            OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
            SOFTWARE.

            ---

            This software uses PyQt6, which is Copyright (c) Riverbank Computing Limited.
            PyQt6 is free software: you can redistribute it and/or modify it under the
            terms of the GNU General Public License as published by the Free Software
            Foundation, either version 3 of the License, or (at your option) any later
            version.
            PyQt6 is distributed in the hope that it will be useful, but WITHOUT ANY
            WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
            FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
            You should have received a copy of the GNU General Public License along with
            PyQt6. If not, see <http://www.gnu.org/licenses/>.
            """))

        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b3a;
                color: #ffffff;
                border: none;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }
        """)
        layout.addWidget(text_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)

        dialog.exec()

    # ====================
    # Passwort-Generierung
    # ====================

    def _get_charset(self):
        chars = ""
        if self.uppercase_check.isChecked():
            chars += string.ascii_uppercase
        if self.lowercase_check.isChecked():
            chars += string.ascii_lowercase
        if self.digits_check.isChecked():
            chars += string.digits
        if self.symbols_check.isChecked():
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        exclude = self.exclude_input.text()
        if exclude:
            chars = "".join(c for c in chars if c not in exclude)
        return chars

    def generate_password(self):
        self.password_added_to_history = False
        chars_all = self._get_charset()
        if not chars_all:
            self.password_display.setText("Bitte mindestens einen Zeichentyp auswählen")
            return

        self.current_charset = chars_all
        length = self.length_spin.value()
        count = self.count_spin.value()
        mode = self.special_mode_combo.currentData()

        specials = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not self.symbols_check.isChecked():
            specials = ""
        nonspecial = "".join(c for c in chars_all if c not in specials)
        if not specials:
            mode = "many"
        if not nonspecial:
            nonspecial = specials  # Fallback

        if count == 1:
            password = self._generate_single_password(
                length, mode, specials, nonspecial
            )
            self.raw_password = password
            self.format_password()
            if self.auto_copy_check.isChecked():
                self.copy_password()
        else:
            passwords = []
            for i in range(count):
                pw = self._generate_single_password(length, mode, specials, nonspecial)
                passwords.append(pw)
                if i == 0:
                    self.raw_password = pw
                    self.format_password()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for pw in passwords:
                formatted = self.apply_formatting(pw)
                self.add_to_history(formatted, timestamp)
            self.password_added_to_history = True
            if self.auto_copy_check.isChecked():
                self.copy_password()

    def _generate_single_password(self, length, mode, specials, nonspecial):
        if not specials:
            return "".join(random.choice(nonspecial) for _ in range(length))
        if not nonspecial:
            return "".join(random.choice(specials) for _ in range(length))

        if mode == "many":
            pool = specials + nonspecial
            return "".join(random.choice(pool) for _ in range(length))
        elif mode == "few":
            return self._generate_with_probability(length, 0.1, specials, nonspecial)
        elif mode == "single":
            return self._generate_with_probability(length, 0.05, specials, nonspecial)
        elif mode == "only_one":
            return self._generate_exactly_one(length, specials, nonspecial)
        elif mode == "one_per_group":
            group_size = self.group_size_spin.value()
            if group_size <= 0:
                return self._generate_exactly_one(length, specials, nonspecial)
            return self._generate_one_per_group(
                length, group_size, specials, nonspecial
            )
        else:
            pool = specials + nonspecial
            return "".join(random.choice(pool) for _ in range(length))

    def _generate_with_probability(self, length, p, specials, nonspecial):
        result = []
        for _ in range(length):
            if random.random() < p:
                result.append(random.choice(specials))
            else:
                result.append(random.choice(nonspecial))
        return "".join(result)

    def _generate_exactly_one(self, length, specials, nonspecial):
        pos = random.randint(0, length - 1)
        chars = [random.choice(nonspecial) for _ in range(length)]
        chars[pos] = random.choice(specials)
        return "".join(chars)

    def _generate_one_per_group(self, length, group_size, specials, nonspecial):
        result = []
        for start in range(0, length, group_size):
            end = min(start + group_size, length)
            g_len = end - start
            pos_in_group = random.randint(0, g_len - 1)
            group_chars = [random.choice(nonspecial) for _ in range(g_len)]
            group_chars[pos_in_group] = random.choice(specials)
            result.extend(group_chars)
        return "".join(result)

    def _update_special_mode_combo(self):
        """Wird bei Änderung der Gruppierungsgröße aufgerufen."""
        self._rebuild_special_mode_combo()
        # Optional: sofort neu generieren, wenn sich die Optionen ändern
        self.generate_password()

    def _rebuild_special_mode_combo(self):
        """
        Baut die Combobox neu auf:
        - „eins pro Gruppe“ nur wenn Gruppierung > 0
        - Deaktiviert die Combobox, wenn nur Sonderzeichen aktiv sind
        """
        # Aktuellen ausgewählten Modus merken (falls vorhanden)
        current_mode = (
            self.special_mode_combo.currentData()
            if self.special_mode_combo.count() > 0
            else "many"
        )

        # Alle Einträge löschen
        self.special_mode_combo.clear()

        # Grundlegende Modi – immer verfügbar
        items = [
            ("viele (Standard)", "many"),
            ("wenige", "few"),
            ("einzelne", "single"),
            ("nur eins", "only_one"),
        ]

        # „eins pro Gruppe“ nur, wenn Gruppierung > 0
        if self.group_size_spin.value() > 0:
            items.append(("eins pro Gruppe", "one_per_group"))

        # Einträge neu einfügen
        for label, data in items:
            self.special_mode_combo.addItem(label, data)

        # Vorherigen Modus wiederherstellen, falls noch vorhanden
        index = self.special_mode_combo.findData(current_mode)
        if index >= 0:
            self.special_mode_combo.setCurrentIndex(index)
        else:
            self.special_mode_combo.setCurrentIndex(0)  # Fallback auf "many"

        # Combobox deaktivieren, wenn keine anderen Zeichentypen außer Sonderzeichen aktiv sind
        other_types = (
            self.uppercase_check.isChecked()
            or self.lowercase_check.isChecked()
            or self.digits_check.isChecked()
        )
        self.special_mode_combo.setEnabled(other_types)

    def format_password(self):
        if not self.raw_password:
            return
        self.formatted_password = self.apply_formatting(self.raw_password)
        self.password_display.setText(self.formatted_password)
        self.update_strength_display()
        self.password_display.setCursorPosition(len(self.formatted_password))

    def apply_formatting(self, password):
        group_size = self.group_size_spin.value()
        separator = self.separator_input.text()
        if group_size > 0 and separator:
            groups = []
            for i in range(0, len(password), group_size):
                groups.append(password[i : i + group_size])
            return separator.join(groups)
        else:
            return password

    def on_text_changed(self, text):
        separator = self.separator_input.text()
        raw = text.replace(separator, "")
        self.raw_password = raw
        self.formatted_password = text
        self.password_added_to_history = (
            False  # <-- Neu: Bei manueller Änderung Verlauf neu anlegen
        )
        self.update_strength_display()

    def on_password_edited(self):
        self.format_password()
        self.password_added_to_history = False  # <-- Neu: auch bei Enter/Fokusverlust

    # ====================
    # Stärke & Entropie
    # ====================

    LENGTH_INFO = {
        4: {
            "strength": "Sehr schwach",
            "short": "PIN-Niveau",
            "usage": "Keine Passwörter; allenfalls temporärer Code",
        },
        6: {
            "strength": "Sehr schwach",
            "short": "Kurzcode",
            "usage": "Keine wichtigen Konten; ggf. temporärer Zugangscode",
        },
        8: {
            "strength": "Schwach",
            "short": "Basisschutz",
            "usage": "Unkritische Test-/Demo-Konten",
        },
        10: {
            "strength": "Schwach–mittel",
            "short": "Einfachschutz",
            "usage": "Unkritische Dienste, wenn keine bessere Option besteht",
        },
        12: {
            "strength": "Mittel",
            "short": "Standard",
            "usage": "Normale Konten; besser mit MFA",
        },
        16: {
            "strength": "Stark",
            "short": "Kontoschutz",
            "usage": "E-Mail, Benutzerkonten, Cloud-Dienste",
        },
        20: {
            "strength": "Stark",
            "short": "besserer Kontoschutz",
            "usage": "Wichtigere Konten, Admin-Zugänge",
        },
        24: {
            "strength": "Stark",
            "short": "Sicherheitsreserve",
            "usage": "Besonders wichtige Konten und Systeme",
        },
        32: {
            "strength": "Sehr stark",
            "short": "Hochsicherheit",
            "usage": "Passwortmanager, Admin-/Serverzugänge",
        },
        64: {
            "strength": "Besonders stark",
            "short": "Maximalschutz",
            "usage": "Hochsicherheitskonten, Schlüsselmaterial-ähnliche Geheimnisse",
        },
        128: {
            "strength": "Ausgezeichnet",
            "short": "Sicherheitsreserve",
            "usage": "Technische Secrets, API-/Systemzugänge",
        },
        256: {
            "strength": "Sehr exzellent",
            "short": "Sehr hoher Schutz",
            "usage": "Maschinengeheimnisse, kryptografienahe Anwendungen",
        },
        512: {
            "strength": "Extrem",
            "short": "Überdimensioniert",
            "usage": "Spezielle technische Anwendungen",
        },
        1024: {
            "strength": "Absolut extrem",
            "short": "Massive Reserve",
            "usage": "Praktisch nie als normales Benutzerpasswort erforderlich",
        },
        2048: {
            "strength": "Extrem paranoid",
            "short": "Praktisch überdimensioniert",
            "usage": "Spezialfälle; für normale Konten ohne zusätzlichen Nutzen",
        },
    }

    STRENGTH_CATEGORIES = [
        {
            "min": 0,
            "max": 40,
            "label": "Sehr schwach",
            "symbol": "🔴",
            "color": COLORS["strong10"],
            "value": 5,
        },
        {
            "min": 40,
            "max": 60,
            "label": "Schwach",
            "symbol": "🟠",
            "color": COLORS["strong10"],
            "value": 10,
        },
        {
            "min": 60,
            "max": 80,
            "label": "Mittel",
            "symbol": "🟡",
            "color": COLORS["strong20"],
            "value": 20,
        },
        {
            "min": 80,
            "max": 120,
            "label": "Stark",
            "symbol": "🟢",
            "color": COLORS["strong30"],
            "value": 30,
        },
        {
            "min": 120,
            "max": 200,
            "label": "Sehr stark",
            "symbol": "🟢",
            "color": COLORS["strong40"],
            "value": 40,
        },
        {
            "min": 200,
            "max": 420,
            "label": "Sehr stark",
            "symbol": "🟢",
            "color": COLORS["strong50"],
            "value": 50,
        },
        {
            "min": 420,
            "max": 600,
            "label": "Besonders stark",
            "symbol": "🟢",
            "color": COLORS["strong60"],
            "value": 60,
        },
        {
            "min": 600,
            "max": 860,
            "label": "Ausgezeichnet",
            "symbol": "🟢",
            "color": COLORS["strong70"],
            "value": 70,
        },
        {
            "min": 860,
            "max": 1300,
            "label": "Exzellent",
            "symbol": "🟢",
            "color": COLORS["strong70"],
            "value": 70,
        },
        {
            "min": 1300,
            "max": 1700,
            "label": "Sehr exzellent",
            "symbol": "🟢",
            "color": COLORS["strong80"],
            "value": 80,
        },
        {
            "min": 1700,
            "max": 3400,
            "label": "Extrem",
            "symbol": "🟢",
            "color": COLORS["strong90"],
            "value": 90,
        },
        {
            "min": 3400,
            "max": 6100,
            "label": "Hochgradig extrem",
            "symbol": "🟢",
            "color": COLORS["strong100"],
            "value": 95,
        },
        {
            "min": 6100,
            "max": 6800,
            "label": "Absolut extrem",
            "symbol": "🟢",
            "color": "#2E7D32",
            "value": 100,
        },
        {
            "min": 6800,
            "max": 12200,
            "label": "Paranoid",
            "symbol": "🟢",
            "color": "#2E7D32",
            "value": 100,
        },
        {
            "min": 12200,
            "max": float("inf"),
            "label": "Extrem paranoid",
            "symbol": "🟢",
            "color": "#2E7D32",
            "value": 100,
        },
    ]

    def update_length_info(self):
        length = self.length_spin.value()
        if length in self.LENGTH_INFO:
            info = self.LENGTH_INFO[length]
            text = f"{info['strength']} – {info['short']}: {info['usage']} (bei voller Zeichenauswahl)"
        else:
            charset_size = len(self.current_charset) if self.current_charset else 0
            if charset_size == 0:
                category = "Keine Zeichen ausgewählt"
            else:
                entropy = length * math.log2(charset_size)
                category = self._get_category_from_entropy(entropy)
            text = f"Individuelle Länge – {category} (bei voller Zeichenauswahl)"
        self.length_info_label.setText(text)

    def _get_category_from_entropy(self, entropy):
        for cat in self.STRENGTH_CATEGORIES:
            if cat["min"] <= entropy < cat["max"]:
                return cat["label"]
        return "Extrem"

    def _get_category_details(self, entropy):
        for cat in self.STRENGTH_CATEGORIES:
            if cat["min"] <= entropy < cat["max"]:
                return cat["label"], cat["value"], cat["color"], cat["symbol"]
        return "Extrem", 100, "#0D47A1", "��"

    def calculate_entropy(self, length, mode, specials, nonspecial):
        if not specials or not nonspecial:
            pool = specials + nonspecial
            if not pool:
                return 0
            return length * math.log2(len(pool))
        if mode == "many":
            pool = specials + nonspecial
            return length * math.log2(len(pool))
        elif mode == "few":
            p = 0.1
        elif mode == "single":
            p = 0.05
        elif mode == "only_one":
            L = length
            return (
                math.log2(L)
                + math.log2(len(specials))
                + (L - 1) * math.log2(len(nonspecial))
            )
        elif mode == "one_per_group":
            group_size = self.group_size_spin.value()
            if group_size <= 0:
                L = length
                return (
                    math.log2(L)
                    + math.log2(len(specials))
                    + (L - 1) * math.log2(len(nonspecial))
                )
            entropy = 0.0
            for start in range(0, length, group_size):
                g_len = min(group_size, length - start)
                entropy += (
                    math.log2(g_len)
                    + math.log2(len(specials))
                    + (g_len - 1) * math.log2(len(nonspecial))
                )
            return entropy
        else:
            pool = specials + nonspecial
            return length * math.log2(len(pool))
        # für p-basierte Modi
        h = -p * math.log2(p / len(specials)) - (1 - p) * math.log2(
            (1 - p) / len(nonspecial)
        )
        return length * h

    def update_strength_display(self):
        if not self.raw_password:
            return
        length = len(self.raw_password)
        chars_all = self._get_charset()
        specials = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not self.symbols_check.isChecked():
            specials = ""
        nonspecial = "".join(c for c in chars_all if c not in specials)
        mode = self.special_mode_combo.currentData()
        if not specials:
            mode = "many"
        if not nonspecial:
            nonspecial = specials

        entropy = self.calculate_entropy(length, mode, specials, nonspecial)
        self.entropy_label.setText(f"{entropy:.1f} Bit")
        category, strength_value, color, symbol = self._get_category_details(entropy)
        self.strength_indicator.set_strength(strength_value)
        self.strength_label.setText(f"{symbol} {category}")
        self.strength_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    # =========================
    # Zwischenablage & Verlauf
    # =========================

    def copy_password(self):
        if not self.formatted_password:
            return

        if not self.password_added_to_history:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.add_to_history(self.formatted_password, timestamp)
            self.password_added_to_history = True

        clipboard = QApplication.clipboard()
        clipboard.setText(self.formatted_password)

        # Original-Text speichern (wenn nicht bereits gespeichert)
        if not hasattr(self, "_original_copy_text") or not self._original_copy_text:
            self._original_copy_text = "In Zwischenablage"

        # Button-Text und Stil ändern
        self.copy_btn.setText("✓ Kopiert!")
        self.copy_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["success"]};
                color: {COLORS["text"]};
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 12px;
                min-height: 30px;
            }}
        """)

        # Alten Timer stoppen
        if self.copy_timer is not None:
            self.copy_timer.stop()
            self.copy_timer = None

        # Neuen Timer starten
        self.copy_timer = QTimer()
        self.copy_timer.setSingleShot(True)
        self.copy_timer.timeout.connect(self._reset_copy_button)
        self.copy_timer.start(1500)

    def _reset_copy_button(self):
        """Setzt den Button nach dem Kopieren zurück."""
        self.copy_btn.setText(self._original_copy_text)
        self.copy_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["border"]};
                color: {COLORS["text"]};
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 12px;
                min-height: 30px;
            }}
            QPushButton:hover {{
                background-color: {self.adjust_color(COLORS["border"], 20)};
            }}
        """)
        self.copy_timer = None

    def save_to_history(self):
        current_text = self.password_display.text()
        if not current_text:
            QMessageBox.warning(
                self, "Kein Passwort", "Es ist kein Passwort vorhanden."
            )
            return
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.add_to_history(current_text, timestamp)
        self.password_added_to_history = True
        QMessageBox.information(
            self, "Erfolg", "Passwort wurde zum Verlauf hinzugefügt."
        )

    def add_to_history(self, password, timestamp):
        entry = f"\n[{timestamp}]\n{password}\n"
        self.generated_passwords.append((timestamp, password))
        current_text = self.history_text.toPlainText()
        self.history_text.setText(entry + current_text)

    def clear_history(self):
        reply = QMessageBox.question(
            self,
            "Verlauf löschen",
            "Sind Sie sicher, dass Sie den Passwort-Verlauf löschen möchten?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.history_text.clear()
            self.generated_passwords.clear()

    # ====================
    # Export
    # ====================

    def export_json(self):
        if not self.generated_passwords:
            QMessageBox.warning(
                self, "Export fehlgeschlagen", "Keine Passwörter im Verlauf."
            )
            return
        data = {
            "export_date": datetime.now().isoformat(),
            "export_settings": {
                "group_size": self.group_size_spin.value(),
                "separator": self.separator_input.text(),
            },
            "passwords": [
                {"timestamp": ts, "password": pw} for ts, pw in self.generated_passwords
            ],
        }
        filename, _ = QFileDialog.getSaveFileName(
            self, "Als JSON exportieren", "KeyGenPy-Export", "JSON Dateien (*.json)"
        )
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                QMessageBox.information(
                    self, "Export erfolgreich", f"Passwörter exportiert nach {filename}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Export fehlgeschlagen", f"Fehler: {str(e)}")

    def export_txt(self):
        if not self.generated_passwords:
            QMessageBox.warning(
                self, "Export fehlgeschlagen", "Keine Passwörter im Verlauf."
            )
            return
        text = "=== KeyGenPy Passwort Export ===\n"
        text += f"Exportiert: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        text += f"Gruppierung: {self.group_size_spin.value()}\n"
        text += f"Trennzeichen: '{self.separator_input.text()}'\n"
        text += "=" * 30 + "\n\n"
        for ts, pw in self.generated_passwords:
            text += f"[{ts}] {pw}\n"
        filename, _ = QFileDialog.getSaveFileName(
            self, "Als Text exportieren", "KeyGenPy-Export", "Textdateien (*.txt)"
        )
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(text)
                QMessageBox.information(
                    self, "Export erfolgreich", f"Passwörter exportiert nach {filename}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Export fehlgeschlagen", f"Fehler: {str(e)}")

    def export_csv(self):
        if not self.generated_passwords:
            QMessageBox.warning(
                self, "Export fehlgeschlagen", "Keine Passwörter im Verlauf."
            )
            return
        filename, _ = QFileDialog.getSaveFileName(
            self, "Als CSV exportieren", "KeyGenPy-Export", "CSV-Dateien (*.csv)"
        )
        if not filename:
            return
        try:
            with open(filename, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(
                    f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
                )
                writer.writerow(["Timestamp", "Password"])
                for ts, pw in self.generated_passwords:
                    writer.writerow([ts, pw])
            QMessageBox.information(
                self, "Export erfolgreich", f"Passwörter exportiert nach {filename}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Export fehlgeschlagen", f"Fehler: {str(e)}")

    # ===============================
    # iCloud-Schlüsselbund (macOS)
    # ===============================

    def save_to_icloud(self):
        if not self.raw_password:
            QMessageBox.warning(
                self, "Kein Passwort", "Generieren Sie zuerst ein Passwort."
            )
            return
        if sys.platform != "darwin":
            QMessageBox.information(
                self, "Nicht verfügbar", "Diese Funktion ist nur unter macOS verfügbar."
            )
            return
        entry_types = ["Website oder IP-Adresse", "App", "WLAN"]
        entry_type, ok = QInputDialog.getItem(
            self,
            "Für Apple Passwörter exportieren",
            "Art des Zugangsdaten-Eintrags:",
            entry_types,
            0,
            False,
        )
        if not ok:
            return
        if entry_type == "Website oder IP-Adresse":
            self._save_icloud_website()
        elif entry_type == "App":
            self._save_icloud_app()
        elif entry_type == "WLAN":
            self._save_icloud_wifi()

    def _save_icloud_website(self):
        service, ok = QInputDialog.getText(
            self,
            "Website zu Apple Passwörter",
            "Website / Host:\n\nBeispiele:\nexample.com\nwww.example.com\nhttps://example.com\n192.168.1.1",
        )
        if not ok or not service.strip():
            return
        service = service.strip()
        website, error = self._normalize_icloud_url(service)
        if error:
            QMessageBox.warning(self, "Ungültige Website", error)
            return
        last_username = self.settings.value("icloud_website_username", "", type=str)
        account, ok = QInputDialog.getText(
            self, "Website zu Apple Passwörter", "Benutzername:", text=last_username
        )
        if not ok or not account.strip():
            return
        account = account.strip()
        self.settings.setValue("icloud_website_username", account)
        parsed = urlparse(website)
        domain = parsed.hostname or website
        title = f"{domain} ({account})"
        self._write_icloud_csv(
            title, website, account, self.formatted_password, "Website"
        )

    def _save_icloud_app(self):
        app_name, ok = QInputDialog.getText(
            self, "App zu Apple Passwörter", "Name der App:"
        )
        if not ok or not app_name.strip():
            return
        app_name = app_name.strip()
        last_username = self.settings.value("icloud_app_username", "", type=str)
        account, ok = QInputDialog.getText(
            self,
            "App zu Apple Passwörter",
            "Benutzername / Account:",
            text=last_username,
        )
        if not ok or not account.strip():
            return
        account = account.strip()
        self.settings.setValue("icloud_app_username", account)
        website, ok = QInputDialog.getText(
            self,
            "App zu Apple Passwörter",
            "Website der App (optional):\nz. B. https://example.com",
        )
        if not ok:
            return
        website = website.strip()
        if website:
            normalized_url, error = self._normalize_icloud_url(website)
            if error:
                QMessageBox.warning(self, "Ungültige App-Website", error)
                return
            website = normalized_url
        title = f"{app_name} ({account})"
        self._write_icloud_csv(title, website, account, self.formatted_password, "App")

    def _save_icloud_wifi(self):
        QMessageBox.information(
            self,
            "WLAN-Passwörter",
            "WLAN-Passwörter werden von Apple in der App „Passwörter“ als eigener Datentyp verwaltet.\n\n"
            "Der von Apple dokumentierte CSV-Import unterstützt Website- und App-Passwörter, aber keinen Import von "
            "WLAN-Passwörtern als WLAN-Eintrag.\n\nDaher kann für WLAN über diese Exportfunktion keine Apple-kompatible "
            "CSV erzeugt werden.",
        )

    def _normalize_icloud_url(self, value):
        value = value.strip()
        if not value:
            return None, "Die Eingabe darf nicht leer sein."
        if any(char.isspace() for char in value):
            return None, "Die Adresse darf keine Leerzeichen enthalten."
        if "://" in value:
            parsed = urlparse(value)
            if parsed.scheme.lower() not in ("http", "https"):
                return None, "Nur http:// und https:// werden unterstützt."
            if not parsed.netloc:
                return None, "Die URL enthält keinen gültigen Host."
            if parsed.username is not None:
                return None, "Der Benutzername darf nicht Bestandteil der URL sein."
            if parsed.password is not None:
                return None, "Das Passwort darf nicht Bestandteil der URL sein."
            return value, None
        try:
            ipaddress.IPv4Address(value)
            return f"https://{value}", None
        except ValueError:
            pass
        try:
            ipaddress.IPv6Address(value)
            return f"https://[{value}]", None
        except ValueError:
            pass
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1]
            try:
                ipaddress.IPv6Address(inner)
                return f"https://[{inner}]", None
            except ValueError:
                return None, "Die IPv6-Adresse ist ungültig."
        hostname = value
        port_suffix = ""
        if ":" in hostname:
            if hostname.count(":") == 1:
                host_part, port_part = hostname.rsplit(":", 1)
                if not port_part.isdigit():
                    return None, "Die Portnummer ist ungültig."
                port = int(port_part)
                if not 1 <= port <= 65535:
                    return None, "Der Port muss zwischen 1 und 65535 liegen."
                hostname = host_part
                port_suffix = f":{port}"
            else:
                return None, "Die IPv6-Adresse ist ungültig."
        labels = hostname.split(".")
        if len(labels) < 2:
            return None, (
                "Bitte geben Sie einen vollständigen Hostnamen ein.\n\n"
                "Beispiele:\nexample.com\nrouter.local\n192.168.1.1"
            )
        label_pattern = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$")
        for label in labels:
            if not label:
                return None, "Die Domain enthält einen leeren Abschnitt."
            if not label_pattern.fullmatch(label):
                return None, f"Der Domain-Abschnitt „{label}“ ist ungültig."
        return f"https://{hostname}{port_suffix}", None

    def _write_icloud_csv(self, title, website, username, password, entry_description):
        desktop = os.path.expanduser("~/Desktop")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"passwords_import_{timestamp}.csv"
        csv_path = os.path.join(desktop, csv_filename)
        try:
            with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(
                    f,
                    delimiter=",",
                    quotechar='"',
                    quoting=csv.QUOTE_MINIMAL,
                    lineterminator="\n",
                )
                writer.writerow(
                    ["Title", "URL", "Username", "Password", "Notes", "OTPAuth"]
                )
                writer.writerow(
                    [title, website, username, password, "CSV-Import (KeyGenPy)", ""]
                )
            QMessageBox.information(
                self,
                f"{entry_description} für Apple Passwörter erstellt",
                f"CSV erstellt:\n\n{csv_path}\n\nImport in der App „Passwörter“:\n"
                f"Ablage → „Passwörter aus einer Datei importieren“\n\n"
                f"Der Export enthält das Passwort im Klartext.\n"
                f"Löschen Sie die CSV-Datei nach dem Import und leeren Sie anschließend den Papierkorb.",
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Fehler", f"CSV konnte nicht erstellt werden:\n\n{str(e)}"
            )

    # ====================
    # Einstellungen speichern/laden
    # ====================

    def load_settings(self):
        geometry = self.settings.value("window_geometry")
        if geometry:
            self.restoreGeometry(geometry)
        self.length_spin.setValue(
            int(self.settings.value("length", DEFAULT_PASSWORD_LENGTH))
        )
        self.uppercase_check.setChecked(
            self.settings.value("uppercase", True, type=bool)
        )
        self.lowercase_check.setChecked(
            self.settings.value("lowercase", True, type=bool)
        )
        self.digits_check.setChecked(self.settings.value("digits", True, type=bool))
        self.symbols_check.setChecked(self.settings.value("symbols", True, type=bool))
        self.exclude_input.setText(self.settings.value("exclude", ""))
        self.group_size_spin.setValue(
            int(self.settings.value("group_size", DEFAULT_GROUP_SIZE))
        )
        self.separator_input.setText(
            self.settings.value("separator", DEFAULT_SEPARATOR)
        )
        self.auto_copy_check.setChecked(
            self.settings.value("auto_copy", False, type=bool)
        )
        mode = self.settings.value("special_mode", "many", type=str)
        index = self.special_mode_combo.findData(mode)
        if index >= 0:
            self.special_mode_combo.setCurrentIndex(index)
        else:
            self.special_mode_combo.setCurrentIndex(0)

    def save_settings(self):
        self.settings.setValue("window_geometry", self.saveGeometry())
        self.settings.setValue("length", self.length_spin.value())
        self.settings.setValue("uppercase", self.uppercase_check.isChecked())
        self.settings.setValue("lowercase", self.lowercase_check.isChecked())
        self.settings.setValue("digits", self.digits_check.isChecked())
        self.settings.setValue("symbols", self.symbols_check.isChecked())
        self.settings.setValue("exclude", self.exclude_input.text())
        self.settings.setValue("group_size", self.group_size_spin.value())
        self.settings.setValue("separator", self.separator_input.text())
        self.settings.setValue("auto_copy", self.auto_copy_check.isChecked())
        self.settings.setValue("special_mode", self.special_mode_combo.currentData())

    def closeEvent(self, event):
        self.save_settings()
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)


# =======================================================
# HAUPTFUNKTION
# =======================================================


def main():
    if hasattr(Qt, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("KeyGenPy")
    app.setOrganizationName("BinhDiez")
    if os.path.exists(APP_ICON_PATH):
        app.setWindowIcon(QIcon(APP_ICON_PATH))

    window = KeyGenPyWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
