import sys
import os
import glob
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QFileDialog, QTextEdit, QCheckBox, QGroupBox, 
                             QTabWidget, QTreeView, QSplitter, QFileIconProvider)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QFileInfo
from PyQt6.QtGui import QFont, QTextCursor, QFileSystemModel, QIcon, QPixmap, QPainter, QColor

from helpers.file_helper import FileHelper
from helpers.string_helper import StringHelper
from core.dds_converter import DdsConverter
from core.xml_analyzer import XmlAnalyzer

class StreamRedirector(QObject):
    text_written = pyqtSignal(str)

    def write(self, text):
        self.text_written.emit(str(text))

    def flush(self):
        pass

class CustomIconProvider(QFileIconProvider):
    def __init__(self):
        super().__init__()
        self.html_icon = self._create_icon("< >", "#e34c26")
        self.xml_icon = self._create_icon("XML", "#f39c12")
        self.json_icon = self._create_icon("{ }", "#f1e05a")
        self.py_icon = self._create_icon("PY", "#3572A5")
        
    def _create_icon(self, text, color):
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QColor(color))
        painter.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)
        painter.end()
        return QIcon(pixmap)

    def icon(self, file_info):
        if isinstance(file_info, QFileInfo):
            ext = file_info.suffix().lower()
            if ext == "html": return self.html_icon
            if ext == "xml": return self.xml_icon
            if ext == "json": return self.json_icon
            if ext == "py": return self.py_icon
        return super().icon(file_info)

class EnterpriseXmlTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kurumsal XML Otomasyon ve Analiz Arayüzü v3.1")
        self.setMinimumSize(1000, 750)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e2e; }
            QWidget { color: #cdd6f4; font-family: 'Segoe UI'; }
            QLabel { font-size: 12px; font-weight: bold; }
            QLineEdit { background-color: #313244; border: 1px solid #45475a; border-radius: 5px; padding: 5px; }
            
            QPushButton { background-color: #1565C0; color: #ffffff; font-weight: bold; border-radius: 5px; padding: 8px; border: 1px solid #0D47A1; }
            QPushButton:hover { background-color: #1976D2; border: 1px solid #1565C0; }
            
            QGroupBox { border: 1px solid #45475a; border-radius: 5px; margin-top: 10px; font-weight: bold; color: #64B5F6; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }
            
            QTextEdit { background-color: #11111b; color: #a6e3a1; border: 1px solid #45475a; font-family: Consolas; font-size: 13px; }
            QCheckBox { font-weight: bold; }
            
            QTabWidget::pane { border: 1px solid #45475a; background: #1e1e2e; }
            QTabBar::tab { background: #313244; color: #cdd6f4; padding: 10px 20px; font-weight: bold; border-top-left-radius: 5px; border-top-right-radius: 5px; margin-right: 2px;}
            QTabBar::tab:selected { background: #1565C0; color: #ffffff; }
            
            QTreeView { background-color: #11111b; color: #cdd6f4; border: 1px solid #45475a; }
            QTreeView::item:selected { background-color: #1976D2; color: #ffffff; }
        """)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tab_dashboard = QWidget()
        self.tab_file_viewer = QWidget()
        self.tabs.addTab(self.tab_dashboard, "Otomasyon & Rapor")
        self.tabs.addTab(self.tab_file_viewer, "Dosya Görüntüleyici (Editör)")

        self.setup_dashboard_tab()
        self.setup_file_viewer_tab()

    def setup_dashboard_tab(self):
        layout = QVBoxLayout(self.tab_dashboard)

        config_group = QGroupBox("Klasör ve Ayar Yolları")
        config_layout = QVBoxLayout()

        self.config_input = self.create_path_row("Config Dosyası (.json):", config_layout, is_file=True)
        self.config_input.setText(os.path.abspath("company_rules.json")) 

        self.input_folder = self.create_path_row("JSON Kaynak Klasörü:", config_layout)
        self.input_folder.setText(os.path.abspath("./test_jsonlar"))

        self.output_folder = self.create_path_row("XML Çıktı Klasörü:", config_layout)
        self.output_folder.setText(os.path.abspath("./sonuclar"))

        self.legacy_folder = self.create_path_row("Eski Sistem (Legacy) Klasörü:", config_layout)
        self.legacy_folder.setText(os.path.abspath("./eski_sistemler"))

        config_group.setLayout(config_layout)
        layout.addWidget(config_group)

        action_layout = QHBoxLayout()
        self.check_html = QCheckBox("HTML Raporu Üret")
        self.check_html.setChecked(True)
        action_layout.addWidget(self.check_html)

        self.btn_run = QPushButton("SİSTEMİ ÇALIŞTIR VE ANALİZ ET")
        self.btn_run.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.btn_run.setMinimumHeight(40)
        self.btn_run.clicked.connect(self.run_process)
        action_layout.addWidget(self.btn_run)
        
        layout.addLayout(action_layout)

        console_group = QGroupBox("Sistem Analiz Raporu (Log)")
        console_layout = QVBoxLayout()
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        console_layout.addWidget(self.console_output)
        console_group.setLayout(console_layout)
        layout.addWidget(console_group)

        self.redirector = StreamRedirector()
        self.redirector.text_written.connect(self.append_to_console)
        sys.stdout = self.redirector

    def setup_file_viewer_tab(self):
        layout = QVBoxLayout(self.tab_file_viewer)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(os.getcwd()) 
        
        self.icon_provider = CustomIconProvider()
        self.file_model.setIconProvider(self.icon_provider)
        
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_model)
        self.tree_view.setRootIndex(self.file_model.index(os.getcwd()))
        self.tree_view.setColumnWidth(0, 250)
        self.tree_view.hideColumn(1)
        self.tree_view.hideColumn(2)
        self.tree_view.hideColumn(3)
        self.tree_view.clicked.connect(self.on_tree_clicked)

        self.code_viewer = QTextEdit()
        self.code_viewer.setReadOnly(True)
        self.code_viewer.setPlaceholderText("Görüntülemek için sol taraftan bir JSON veya XML dosyası seçin...")

        splitter.addWidget(self.tree_view)
        splitter.addWidget(self.code_viewer)
        splitter.setSizes([300, 700])

        layout.addWidget(splitter)

    def on_tree_clicked(self, index):
        file_path = self.file_model.filePath(index)
        if os.path.isfile(file_path):
            if file_path.endswith(('.json', '.xml', '.py', '.txt', '.html', '.md')):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.code_viewer.setText(content)
                except Exception as e:
                    self.code_viewer.setText(f"Dosya okunamadı: {e}")
            else:
                self.code_viewer.setText(f"Bu dosya türü önizleme için desteklenmiyor.\nDosya: {file_path}")

    def create_path_row(self, label_text, parent_layout, is_file=False):
        row_layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setFixedWidth(200)
        line_edit = QLineEdit()
        btn_browse = QPushButton("Gözat...")
        btn_browse.setFixedWidth(80)
        
        if is_file:
            btn_browse.clicked.connect(lambda: line_edit.setText(QFileDialog.getOpenFileName(self, "Dosya Seç", "", "JSON Files (*.json)")[0]))
        else:
            btn_browse.clicked.connect(lambda: line_edit.setText(QFileDialog.getExistingDirectory(self, "Klasör Seç")))

        row_layout.addWidget(label)
        row_layout.addWidget(line_edit)
        row_layout.addWidget(btn_browse)
        parent_layout.addLayout(row_layout)
        return line_edit

    def append_to_console(self, text):
        self.console_output.moveCursor(QTextCursor.MoveOperation.End)
        self.console_output.insertPlainText(text)
        self.console_output.moveCursor(QTextCursor.MoveOperation.End)
        QApplication.processEvents()

    def run_process(self):
        self.console_output.clear()
        print("="*60)
        print("[START] MİMARİ OTOMASYONU BAŞLATILIYOR...")
        print("="*60)

        config_path = self.config_input.text().strip()
        config_data = FileHelper.load_json(config_path)
        if not config_data:
            print(f"[ERROR] Config dosyası bulunamadı: {config_path}")
            return

        in_folder = self.input_folder.text().strip()
        out_folder = self.output_folder.text().strip()
        leg_folder = self.legacy_folder.text().strip()

        if not out_folder:
            out_folder = "./sonuclar"
        if not in_folder:
            in_folder = "./test_jsonlar"

        converter = DdsConverter(config=config_data)
        
        grouped_jsons = {}
        item_tracker = {}
        
        if os.path.exists(in_folder):
            json_files = sorted(glob.glob(os.path.join(in_folder, "*.json")))
            print(f"\n[INFO] {len(json_files)} adet JSON bulundu. Birleştirme yapılıyor...")
            
            for json_file in json_files:
                json_data = FileHelper.load_json(json_file)
                if not json_data: continue
                
                grup_ismi = json_data.get("groupName", "Unknown")
                
                if grup_ismi not in grouped_jsons:
                    grouped_jsons[grup_ismi] = []
                    item_tracker[grup_ismi] = set()

                filtered_json = {
                    "name": json_data.get("name", "Unknown"),
                    "groupName": grup_ismi,
                    "items": []
                }

                for item in json_data.get("items", []):
                    clean_name = StringHelper.clean_member_name(item.get("name", ""))
                    
                    if clean_name not in item_tracker[grup_ismi]:
                        filtered_json["items"].append(item)
                        item_tracker[grup_ismi].add(clean_name)
                    else:
                        print(f"    [INFO] '{clean_name}' tekrarı engellendi (Harmonized).")

                grouped_jsons[grup_ismi].append(filtered_json)

        os.makedirs(out_folder, exist_ok=True)
        üretilen_xmller = []
        print(f"\n[INFO] {len(grouped_jsons)} Master XML oluşturuluyor...")
        
        for grup, json_list in grouped_jsons.items():
            out_file = os.path.join(out_folder, f"{grup}.xml")
            
            xml_result = converter.convert(json_list) 
            FileHelper.save_file(out_file, xml_result)
            
            toplam_degisken = sum(len(j["items"]) for j in json_list)
            print(f"  [+] Üretildi: {out_file} ({len(json_list)} Struct, {toplam_degisken} Benzersiz Değişken)")
            üretilen_xmller.append(out_file)

        if leg_folder and os.path.exists(leg_folder):
            print(f"\n[INFO] Kıyaslama Motoru (Analyzer) Başlatıldı...")
            for new_xml in üretilen_xmller:
                filename = os.path.basename(new_xml)
                legacy_xml = os.path.join(leg_folder, filename)
                
                if os.path.exists(legacy_xml):
                    print(f"\n>>> {filename} için Analiz:")
                    analyzer = XmlAnalyzer(legacy_xml_path=legacy_xml, new_xml_path=new_xml)
                    analyzer.print_terminal_report()
                    if self.check_html.isChecked():
                        analyzer.export_html_report(f"rapor_{filename.replace('.xml', '.html')}")
                else:
                    print(f"  [-] Eski sistemde {filename} bulunamadı.")
        print("\n[OK] İŞLEM TAMAMLANDI!")

        # --- EKRANI OTOMATİK YENİLEME (F5 MANTIĞI) ---
        current_path = self.file_model.rootPath()
        self.file_model.setRootPath("")           # Önbelleği (Cache) temizle
        self.file_model.setRootPath(current_path) # Ağacı yeniden yükle

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EnterpriseXmlTool()
    window.show()
    sys.exit(app.exec())
