from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QSpinBox, QComboBox, QTextEdit, QGroupBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import sys

# Dados (conforme a tua especificação / imagem)
REQ_BODY = {"Ferro": 100, "Cobre": 100, "Aluminio": 100, "Plastico": 150}
REQ_OTHER = {"Ferro": 10, "Cobre": 10, "Aluminio": 10, "Plastico": 15}
PIECES = ["Body", "Gun Barrel", "Gun Butt", "Gun Handle", "Gun Spring"]
MATERIALS = ["Ferro", "Cobre", "Aluminio", "Plastico"]

# Presets conforme a tabela da imagem. Mantive Body = 1 (como antes).
PRESETS = {
    "Five Seven":       [1, 2,  2,  3,  3],
    "0.5":              [1, 6,  6,  6,  6],
    "Tec-9":            [1, 5,  5,  5,  5],
    "PDW":              [1, 10, 10, 10, 10],
    "P90":              [1, 13, 13, 12, 12],
    "Uzi":              [1, 8,  8,  7,  7],
    "MK2":              [1, 8,  9,  9,  9],
    "Compact-Rifle":    [1, 4,  4,  4,  3],
    "QBZ":              [1, 18, 17, 18, 17],
    "Ak-47":            [1, 18, 17, 18, 17],
    "G3":               [1, 23, 21, 23, 21],
    "Shotgun Tactica":  [1, 33, 31, 33, 31]
}

# Mapeamento do tipo de Body (Pistol / SMG / Rifle / Shotgun)
BODY_TYPES = {
    "Five Seven": "Pistol",
    "0.5": "Pistol",
    "Tec-9": "SMG",
    "PDW": "SMG",
    "P90": "SMG",
    "Uzi": "SMG",
    "MK2": "SMG",
    "Compact-Rifle": "Rifle",
    "QBZ": "Rifle",
    "Ak-47": "Rifle",
    "G3": "Rifle",
    "Shotgun Tactica": "Shotgun"
}

# Cores para cada tipo (badge visual)
BODY_TYPE_COLORS = {
    "Pistol": "#FF8A65",
    "SMG": "#4FC3F7",
    "Rifle": "#81C784",
    "Shotgun": "#BA68C8",
    "": "#888888"
}

def calcular(quantidades_materiais, counts):
    """
    Calcula:
      - neces_por_arma: materiais necessários para 1 arma com base em counts (peças por arma)
      - limites: quantas armas são possíveis por cada material individual
      - max_armas: máximo de armas possível (mínimo dos limites)
      - sobra: materiais sobrando após fabricar max_armas armas
    """
    if len(counts) != len(PIECES):
        raise ValueError("counts deve conter um valor por peça: " + ", ".join(PIECES))

    # Calcula materiais por 1 arma
    neces_por_arma = {m: 0 for m in MATERIALS}
    # Body (índice 0) usa REQ_BODY
    for m in MATERIALS:
        neces_por_arma[m] += counts[0] * REQ_BODY.get(m, 0)
    # Outras peças usam REQ_OTHER
    for i in range(1, len(PIECES)):
        for m in MATERIALS:
            neces_por_arma[m] += counts[i] * REQ_OTHER.get(m, 0)

    # Limites por material (evita divisão por zero)
    limites = {}
    for m in MATERIALS:
        req = neces_por_arma.get(m, 0)
        qty = quantidades_materiais.get(m, 0)
        if req > 0:
            limites[m] = qty // req
        else:
            limites[m] = float('inf')

    # Calcula máximo de armas com base no menor limite
    min_lim = min(limites.values())
    if min_lim == float('inf'):
        max_armas = 0
    else:
        max_armas = int(min_lim)

    # Calcula sobra após fabricar max_armas armas
    sobra = {m: quantidades_materiais.get(m, 0) - max_armas * neces_por_arma.get(m, 0) for m in MATERIALS}
    return max_armas, limites, sobra, neces_por_arma

class Calculadora(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora de Armas")
        self.setGeometry(100, 100, 980, 720)
        self.setStyleSheet("background-color:#0f1720; color: #E6EEF3;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        # Cabeçalho
        header = QLabel("💥 Calculadora de Armas 💥")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_font = QFont("Segoe UI", 20, QFont.Weight.Bold)
        header.setFont(header_font)
        header.setStyleSheet("""
            color: white;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #2b5876, stop:1 #4e4376);
            padding: 12px;
            border-radius: 10px;
        """)
        layout.addWidget(header)

        # Preset + Tipo de Body
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        preset_group = QGroupBox()
        preset_group.setStyleSheet("QGroupBox { border: none; color: #E6EEF3; }")
        preset_layout = QHBoxLayout()
        preset_label = QLabel("Preset:")
        preset_label.setStyleSheet("color:#DDE7EF; font-weight:600;")
        preset_layout.addWidget(preset_label)
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(PRESETS.keys())
        self.preset_combo.setStyleSheet("""
            QComboBox { background: #0b1220; color: #E6EEF3; padding: 6px; border-radius:6px; }
            QComboBox QAbstractItemView { background: #071021; color: #E6EEF3; }
        """)
        preset_layout.addWidget(self.preset_combo)

        # badge para o tipo
        self.body_type_label = QLabel("")
        self.body_type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.body_type_label.setFixedHeight(28)
        self.body_type_label.setMinimumWidth(120)
        self.body_type_label.setStyleSheet("color: white; border-radius: 14px; padding: 4px;")
        preset_layout.addWidget(self.body_type_label)
        preset_group.setLayout(preset_layout)
        top_row.addWidget(preset_group, stretch=1)

        # Quick stats area
        stats_group = QGroupBox()
        stats_group.setStyleSheet("QGroupBox { border: none; color: #DDE7EF; }")
        stats_layout = QHBoxLayout()
        self.max_possible_label = QLabel("Máx (preset atual): 0")
        self.max_possible_label.setStyleSheet("color:#CFECEC; font-weight:600;")
        stats_layout.addWidget(self.max_possible_label)
        stats_group.setLayout(stats_layout)
        top_row.addWidget(stats_group, stretch=0)

        layout.addLayout(top_row)
        self.preset_combo.currentTextChanged.connect(self.aplicar_preset)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("color: #203040;")
        layout.addWidget(divider)

        # Central area: peças à esquerda, materiais à direita
        central = QHBoxLayout()
        central.setSpacing(12)

        # Left: Peças por arma
        pieces_group = QGroupBox("Peças por arma")
        pieces_group.setStyleSheet("""
            QGroupBox { font-weight:700; color:#E6EEF3; border: 1px solid #203040; border-radius:8px; padding:8px; }
        """)
        pieces_layout = QGridLayout()
        pieces_layout.setHorizontalSpacing(12)
        pieces_layout.setVerticalSpacing(8)
        self.count_inputs = {}
        for i, p in enumerate(PIECES):
            label = QLabel(p + ":")
            label.setStyleSheet("color:#DDE7EF;")
            spin = QSpinBox()
            spin.setRange(0, 9999)
            spin.setButtonSymbols(QSpinBox.ButtonSymbols.UpDownArrows)
            # Peças: mostrar o 0 por defeito (não usar special value)
            spin.setStyleSheet("QSpinBox { background: #08121A; color: #E6EEF3; padding:4px; border-radius:6px; }")
            pieces_layout.addWidget(label, i, 0)
            pieces_layout.addWidget(spin, i, 1)
            self.count_inputs[p] = spin
        pieces_group.setLayout(pieces_layout)
        central.addWidget(pieces_group, stretch=2)

        # Right: Materiais disponíveis + desejado + botão
        right_v = QVBoxLayout()
        mat_group = QGroupBox("Materiais disponíveis")
        mat_group.setStyleSheet("""
            QGroupBox { font-weight:700; color:#E6EEF3; border: 1px solid #203040; border-radius:8px; padding:8px; }
        """)
        mat_layout = QGridLayout()
        mat_layout.setHorizontalSpacing(12)
        mat_layout.setVerticalSpacing(8)
        self.mat_inputs = {}
        for i, m in enumerate(MATERIALS):
            label = QLabel(m + ":")
            label.setStyleSheet("color:#DDE7EF;")
            spin = QSpinBox()
            spin.setRange(0, 1000000)
            spin.setButtonSymbols(QSpinBox.ButtonSymbols.UpDownArrows)
            # Materiais: mostrar vazio quando o valor for 0 (sem exibir "0")
            spin.setSpecialValueText("")
            spin.setStyleSheet("QSpinBox { background: #08121A; color: #E6EEF3; padding:4px; border-radius:6px; }")
            mat_layout.addWidget(label, i, 0)
            mat_layout.addWidget(spin, i, 1)
            self.mat_inputs[m] = spin
        mat_group.setLayout(mat_layout)
        right_v.addWidget(mat_group)

        # Desejado + botão
        desired_layout = QHBoxLayout()
        desired_label = QLabel("Número de armas desejadas:")
        desired_label.setStyleSheet("color:#DDE7EF;")
        desired_layout.addWidget(desired_label)
        self.desired_input = QSpinBox()
        self.desired_input.setRange(0, 1000000)
        # Desejado: mostrar o 0 por defeito
        self.desired_input.setStyleSheet("QSpinBox { background: #08121A; color: #E6EEF3; padding:4px; border-radius:6px; }")
        desired_layout.addWidget(self.desired_input)
        right_v.addLayout(desired_layout)

        calc_btn = QPushButton("Calcular")
        calc_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #3b6978, stop:1 #2a5368);
                color: white; font-weight:700; padding:8px; border-radius:8px;
            }
            QPushButton:hover { opacity: 0.95; }
        """)
        calc_btn.clicked.connect(self.mostrar_resultado)
        right_v.addWidget(calc_btn)

        central.addLayout(right_v, stretch=1)

        layout.addLayout(central)

        # Resultado (compacto)
        self.result_txt = QTextEdit()
        self.result_txt.setReadOnly(True)
        self.result_txt.setStyleSheet("""
            QTextEdit { background: #041018; color: #E6EEF3; border: 1px solid #203040; border-radius:8px;
                       font-family: 'Segoe UI', sans-serif; font-size:13px; padding:8px; }
        """)
        self.result_txt.setFixedHeight(180)
        layout.addWidget(self.result_txt)

        self.setLayout(layout)

        # Conecta mudanças para recalcular automaticamente
        for spin in self.count_inputs.values():
            spin.valueChanged.connect(self._on_value_changed)
        for spin in self.mat_inputs.values():
            spin.valueChanged.connect(self._on_value_changed)
        self.desired_input.valueChanged.connect(self._on_value_changed)

        # Aplica preset inicial
        self.aplicar_preset()

    def _on_value_changed(self, _=None):
        # recalcula automaticamente
        self.mostrar_resultado()

    def aplicar_preset(self):
        preset = self.preset_combo.currentText()
        vals = PRESETS.get(preset, PRESETS["PDW"])
        for i, p in enumerate(PIECES):
            self.count_inputs[p].setValue(vals[i])
        # Atualiza label do tipo de Body (com cor)
        tipo = BODY_TYPES.get(preset, "")
        color = BODY_TYPE_COLORS.get(tipo, BODY_TYPE_COLORS[""])
        if tipo:
            self.body_type_label.setText(f"{tipo}")
            self.body_type_label.setStyleSheet(
                f"color: white; background: {color}; border-radius: 14px; padding:4px; font-weight:700;"
            )
        else:
            self.body_type_label.setText("")
            self.body_type_label.setStyleSheet("color: white; background: #444444; border-radius: 14px; padding:4px;")

        # Recalcula e atualiza estatísticas rápidas
        self.mostrar_resultado()

    def mostrar_resultado(self):
        # Lê entradas e valida
        try:
            mats = {m: self.mat_inputs[m].value() for m in MATERIALS}
            counts = [self.count_inputs[p].value() for p in PIECES]
            desired = self.desired_input.value()
            if any(c < 0 for c in counts) or any(v < 0 for v in mats.values()) or desired < 0:
                raise ValueError("Valores não podem ser negativos")
        except Exception as e:
            self.result_txt.setHtml(f"<div style='color:#FF8A65'>Erro: insere inteiros não negativos.</div>")
            return

        # Faz o cálculo base
        try:
            max_armas, limites, sobra, neces_por_arma = calcular(mats, counts)
        except Exception as e:
            self.result_txt.setHtml(f"<div style='color:#FF8A65'>Erro no cálculo.</div>")
            return

        # Atualiza label de estatísticas rápidas
        self.max_possible_label.setText(f"Máx (preset atual): {max_armas}")

        # Preparar informações essenciais
        preset_atual = self.preset_combo.currentText()
        tipo = BODY_TYPES.get(preset_atual, "N/A")

        # Quantidades necessárias para 'desired'
        required_total = {m: neces_por_arma[m] * desired for m in MATERIALS}
        falta = {m: max(0, required_total[m] - mats[m]) for m in MATERIALS}

        # Verifica se há faltas
        faltas_list = [(m, falta[m]) for m in MATERIALS if falta[m] > 0]

        # Construir output minimal em HTML
        badge_color = BODY_TYPE_COLORS.get(tipo, "#888888")
        html = f"<div><strong>{preset_atual}</strong>  <span style='background:{badge_color};color:#fff;padding:4px 8px;border-radius:10px;margin-left:8px'>{tipo}</span></div>"
        html += f"<div style='margin-top:6px'>Máx possível (preset atual): <strong>{max_armas}</strong></div>"

        # Desired block (essential)
        html += f"<div style='margin-top:8px'>Desejado: <strong>{desired}</strong></div>"
        if desired == 0:
            html += "<div style='color:#94A3B8;margin-top:6px'>(Nenhuma arma desejada)</div>"
        else:
            if not faltas_list:
                html += "<div style='color:#81C784;margin-top:6px'><strong>Suficiente</strong> — tens materiais para fabricar o desejado.</div>"
            else:
                # Mostrar apenas faltas essenciais
                faltas_html = ", ".join(f"{m}: {q}" for m, q in faltas_list)
                html += f"<div style='color:#FF8A65;margin-top:6px'><strong>Falta:</strong> {faltas_html}</div>"

        # Define o HTML no QTextEdit (compacto)
        self.result_txt.setHtml(html)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Calculadora()
    window.show()
    sys.exit(app.exec())
