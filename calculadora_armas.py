from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QTextEdit, QGroupBox
)
from PyQt6.QtCore import Qt
import sys

# Dados (conforme a tua especificação)
REQ_BODY = {"Ferro": 100, "Cobre": 100, "Aluminio": 100, "Plastico": 150}
REQ_OTHER = {"Ferro": 10, "Cobre": 10, "Aluminio": 10, "Plastico": 15}
PIECES = ["Body", "Gun Barrel", "Gun Butt", "Gun Handle", "Gun Spring"]
MATERIALS = ["Ferro", "Cobre", "Aluminio", "Plastico"]
PRESETS = {
    "PDW": [1, 10, 10, 10, 10],   # 1 body + 10 de cada outra peça
    "KBZ": [1, 18, 17, 18, 17],   # 1 body + 18/17/18/17
    "P90": [1, 13, 13, 12, 12]    # 1 body + 13/13/12/12
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
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet("background-color:black; font-size:14px; color:white;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Cabeçalho
        header = QLabel("💥 Calculadora de Armas 💥")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size:24px; font-weight:bold; color:#FFFFFF;")
        layout.addWidget(header)

        # Preset
        preset_layout = QHBoxLayout()
        preset_label = QLabel("Preset:")
        preset_label.setStyleSheet("color:white;")
        preset_layout.addWidget(preset_label)
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(PRESETS.keys())
        preset_layout.addWidget(self.preset_combo)
        layout.addLayout(preset_layout)
        self.preset_combo.currentTextChanged.connect(self.aplicar_preset)

        # Peças
        self.count_inputs = {}
        pieces_group = QGroupBox("Peças por arma")
        pieces_group.setStyleSheet("color:white;")
        pieces_layout = QVBoxLayout()
        for p in PIECES:
            hl = QHBoxLayout()
            label = QLabel(p + ":")
            label.setStyleSheet("color:white;")
            hl.addWidget(label)
            inp = QLineEdit()
            inp.setText("0")
            inp.setStyleSheet("background-color:#333333; color:white;")
            hl.addWidget(inp)
            self.count_inputs[p] = inp
            pieces_layout.addLayout(hl)
        pieces_group.setLayout(pieces_layout)
        layout.addWidget(pieces_group)

        # Materiais
        self.mat_inputs = {}
        mat_group = QGroupBox("Materiais disponíveis")
        mat_group.setStyleSheet("color:white;")
        mat_layout = QVBoxLayout()
        for m in MATERIALS:
            hl = QHBoxLayout()
            label = QLabel(m + ":")
            label.setStyleSheet("color:white;")
            hl.addWidget(label)
            inp = QLineEdit()
            inp.setText("0")
            inp.setStyleSheet("background-color:#333333; color:white;")
            hl.addWidget(inp)
            self.mat_inputs[m] = inp
            mat_layout.addLayout(hl)
        mat_group.setLayout(mat_layout)
        layout.addWidget(mat_group)

        # Desejado: número de armas que o utilizador quer fabricar
        desired_layout = QHBoxLayout()
        desired_label = QLabel("Número de armas desejadas:")
        desired_label.setStyleSheet("color:white;")
        desired_layout.addWidget(desired_label)
        self.desired_input = QLineEdit()
        self.desired_input.setText("0")
        self.desired_input.setStyleSheet("background-color:#333333; color:white;")
        desired_layout.addWidget(self.desired_input)
        layout.addLayout(desired_layout)

        # Botão Calcular (opcional, já recalcula automaticamente)
        calc_btn = QPushButton("Calcular")
        calc_btn.setStyleSheet("background-color:#2B3A67; color:white; font-weight:bold; height:35px;")
        calc_btn.clicked.connect(self.mostrar_resultado)
        layout.addWidget(calc_btn)

        # Resultado
        self.result_txt = QTextEdit()
        self.result_txt.setReadOnly(True)
        self.result_txt.setStyleSheet("background-color:#1C1C1C; color:white; font-family:Courier; font-size:14px;")
        layout.addWidget(self.result_txt)

        self.setLayout(layout)

        # Conecta mudanças manuais nos QLineEdit para recalcular automaticamente
        for inp in self.count_inputs.values():
            inp.textChanged.connect(self._on_text_changed)
        for inp in self.mat_inputs.values():
            inp.textChanged.connect(self._on_text_changed)
        self.desired_input.textChanged.connect(self._on_text_changed)

        # Aplica preset inicial (vai preencher os QLineEdit das peças e recalcular)
        self.aplicar_preset()

    def _on_text_changed(self, _=None):
        # Chamado sempre que um QLineEdit é editado; tentar recalcular (mostrar_resultado trata erros)
        self.mostrar_resultado()

    def aplicar_preset(self):
        preset = self.preset_combo.currentText()
        vals = PRESETS.get(preset, PRESETS["PDW"])
        for i, p in enumerate(PIECES):
            self.count_inputs[p].setText(str(vals[i]))
        # Recalcula imediatamente para mostrar os resultados ao trocar preset
        self.mostrar_resultado()

    def mostrar_resultado(self):
        # Lê entradas e valida
        try:
            mats = {}
            for m in MATERIALS:
                txt = self.mat_inputs[m].text().strip()
                mats[m] = int(txt) if txt != "" else 0
                if mats[m] < 0:
                    raise ValueError("Materiais não podem ser negativos")
            counts = []
            for p in PIECES:
                txt = self.count_inputs[p].text().strip()
                counts.append(int(txt) if txt != "" else 0)
            if any(c < 0 for c in counts):
                raise ValueError("Peças por arma não podem ser negativas")
            # Desired number of weapons
            txtd = self.desired_input.text().strip()
            desired = int(txtd) if txtd != "" else 0
            if desired < 0:
                raise ValueError("Número de armas desejadas não pode ser negativo")
        except Exception as e:
            self.result_txt.setText(f"Erro: insere inteiros não negativos. Detalhe: {e}")
            return

        # Faz o cálculo base para o preset atualmente selecionado
        try:
            max_armas, limites, sobra, neces_por_arma = calcular(mats, counts)
        except Exception as e:
            self.result_txt.setText(f"Erro no cálculo: {e}")
            return

        # Mostrar quantas armas de cada PRESET (PDW/KBZ/P90) consigo fazer com os materiais atuais
        preset_possiveis = {}
        for pname, pcounts in PRESETS.items():
            ma, _, _, _ = calcular(mats, pcounts)
            preset_possiveis[pname] = ma

        # Calcula materiais necessários para 'desired' armas (do preset selecionado)
        required_total = {m: neces_por_arma[m] * desired for m in MATERIALS}
        falta = {m: max(0, required_total[m] - mats[m]) for m in MATERIALS}
        sobra_apos = {m: mats[m] - required_total[m] for m in MATERIALS}  # positivo se sobra, negativo se falta

        # Formata saída
        resultado = f"=== PRESET ATUAL: {self.preset_combo.currentText()} ===\n"
        resultado += "Peças por arma:\n"
        for p, c in zip(PIECES, counts):
            resultado += f"  {p}: {c}\n"

        resultado += "\nMateriais necessários por 1 arma (preset atual):\n"
        for m in MATERIALS:
            resultado += f"  {m}: {neces_por_arma[m]}\n"

        resultado += "\nCom os materiais atuais consegues fabricar (por preset):\n"
        for pname, ma in preset_possiveis.items():
            resultado += f"  {pname}: {ma} armas\n"

        resultado += f"\nMáximo de armas possíveis com os materiais atuais (preset atual): {max_armas}\n"

        resultado += "\nSobra de materiais após fabricar o máximo de armas (preset atual):\n"
        for m in MATERIALS:
            resultado += f"  {m}: {sobra[m]}\n"

        resultado += f"\n---\nPara fabricar {desired} armas (preset atual):\n"
        if desired == 0:
            resultado += "  (Nenhuma arma desejada)\n"
        else:
            resultado += "Materiais necessários no total:\n"
            for m in MATERIALS:
                resultado += f"  {m}: {required_total[m]}  (Tens: {mats[m]}  --> "
                if falta[m] > 0:
                    resultado += f"Falta: {falta[m]})\n"
                else:
                    resultado += f"Suficiente, sobra: {sobra_apos[m]})\n"

            # Indica se é possível fabricar a quantidade desejada do preset atual
            if all(mats[m] >= required_total[m] for m in MATERIALS):
                resultado += "\nResultado: Tens materiais suficientes para fabricar o número desejado de armas.\n"
            else:
                resultado += "\nResultado: Não tens materiais suficientes para fabricar o número desejado. Lista de faltas acima.\n"

        self.result_txt.setText(resultado)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Calculadora()
    window.show()
    sys.exit(app.exec())