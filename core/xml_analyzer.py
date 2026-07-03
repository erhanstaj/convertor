import xml.etree.ElementTree as ET
import os
from typing import Dict

class XmlAnalyzer:
    def __init__(self, legacy_xml_path: str, new_xml_path: str):
        self.legacy_xml_path = legacy_xml_path
        self.new_xml_path = new_xml_path

    def _parse_xml_safely(self, filepath: str) -> ET.Element:
        """Çoklu Root içeren veya hatalı XML'leri çökmek yerine Dummy içine alıp güvenle okur."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            if "<?xml" in content:
                content = content.split("?>")[-1]
            return ET.fromstring(f"<DummyRoot>{content}</DummyRoot>")
        except ET.ParseError as e:
            # İŞTE SENIOR KORUMASI: Bozuk XML gelse bile sistem çökmez, uyarır ve atlar.
            print(f"    [CRITICAL ERROR] {filepath} dosyası hatalı XML yapısına sahip! (Hata: {e})")
            return ET.fromstring("<DummyRoot></DummyRoot>")

    def _parse_members(self, root: ET.Element) -> Dict[str, dict]:
        members = {}
        for member in root.findall(".//member"):
            name = member.attrib.get("name")
            if name:
                members[name] = {
                    "type": member.attrib.get("type", "unknown"),
                    "nonBasicTypeName": member.attrib.get("nonBasicTypeName")
                }
        return members

    def analyze(self) -> dict:
        if not os.path.exists(self.legacy_xml_path):
            return {"status": "error", "message": "Eski XML bulunamadı."}
        if not os.path.exists(self.new_xml_path):
            return {"status": "error", "message": "Yeni XML bulunamadı."}

        root_legacy = self._parse_xml_safely(self.legacy_xml_path)
        root_new = self._parse_xml_safely(self.new_xml_path)

        legacy_members = self._parse_members(root_legacy)
        new_members = self._parse_members(root_new)

        report = {
            "status": "success",
            "legacy_count": len(legacy_members),
            "new_count": len(new_members),
            "critical": [], "warnings": [], "improvements": []
        }

        legacy_keys = set(legacy_members.keys())
        new_keys = set(new_members.keys())

        missing_in_new = legacy_keys - new_keys
        added_in_new = new_keys - legacy_keys

        if missing_in_new:
            report["critical"].append(f"Eski sistemde olan {list(missing_in_new)} yeni XML'de eksik!")
        if added_in_new:
            report["improvements"].append(f"Yeni sisteme {list(added_in_new)} başarıyla eklendi.")

        for key in legacy_keys.intersection(new_keys):
            leg_type = legacy_members[key]["type"]
            new_type = new_members[key]["type"]
            if leg_type != new_type:
                report["warnings"].append(f"Tip Degisimi: '{key}' tipi '{leg_type}' iken '{new_type}' yapildi.")

        return report

    def print_terminal_report(self):
        report = self.analyze()
        if report["status"] == "error": return
        print("\n" + "="*75)
        print("[REPORT] SONAR/LINTER SEVIYESI XML MIMARI ANALIZ RAPORU")
        print("="*75)
        print(f"[*] Eski Sistem: {report['legacy_count']} Degisken | Yeni Sistem: {report['new_count']} Degisken")
        print("-" * 75)
        
        if report["critical"]:
            print("[CRITICAL] KRITIK BULGULAR (Veri Kaybi)")
            for item in report["critical"]: print(f"  [-] {item}")
            
        if report["warnings"]:
            print("[WARNING] TIP VE YAPI UYARILARI")
            for item in report["warnings"]: print(f"  [!] {item}")
            
        if report["improvements"]:
            print("[INFO] MIMARI IYILESTIRMELER (Best Practices)")
            for item in report["improvements"]: print(f"  [+] {item}")
            
        if not report["critical"] and not report["warnings"]:
            print("[OK] KUSURSUZ UYUM: Veri kaybi veya tip uyusmazligi bulunamadi. Yapi guvenli.")
        print("="*75 + "\n")

    def export_html_report(self, save_path="rapor.html"):
        report = self.analyze()
        if report["status"] == "error":
            print(f"[ERROR] HTML Raporu oluşturulamadı: {report['message']}")
            return

        html_content = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>XML Mimari Analiz Raporu</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; margin: 0; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; background: #fff; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
        h1 {{ border-bottom: 2px solid #2c3e50; padding-bottom: 10px; color: #2c3e50; }}
        .stats {{ display: flex; justify-content: space-between; background: #ecf0f1; padding: 15px; border-radius: 5px; font-weight: bold; font-size: 1.1em; }}
        .section {{ margin-top: 25px; }}
        .section h2 {{ font-size: 1.3em; margin-bottom: 10px; }}
        .critical {{ border-left: 5px solid #e74c3c; padding: 10px; background: #fadbd8; margin-bottom: 10px; }}
        .warning {{ border-left: 5px solid #f39c12; padding: 10px; background: #fdebd0; margin-bottom: 10px; }}
        .success {{ border-left: 5px solid #27ae60; padding: 10px; background: #d5f5e3; margin-bottom: 10px; }}
        .item {{ margin: 5px 0; font-size: 0.95em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>[REPORT] XML Mimari Analiz ve Karar Destek Raporu</h1>
        <div class="stats">
            <span>[*] Eski Sistem: {report['legacy_count']} Değişken</span>
            <span>[*] Yeni Sistem: {report['new_count']} Değişken</span>
        </div>
        
        <div class="section">
            <h2 style="color: #e74c3c;">[CRITICAL] Kritik Bulgular (Veri Kaybı / Hata)</h2>"""
        
        if report["critical"]:
            for item in report["critical"]:
                html_content += f'<div class="critical item">[-] {item}</div>'
        else:
            html_content += '<div class="item" style="color: gray;">Sorun bulunamadı.</div>'

        html_content += """
        </div>
        <div class="section">
            <h2 style="color: #f39c12;">[WARNING] Tip ve Yapı Uyarıları</h2>"""
            
        if report["warnings"]:
            for item in report["warnings"]:
                html_content += f'<div class="warning item">[!] {item}</div>'
        else:
            html_content += '<div class="item" style="color: gray;">Uyarı bulunamadı.</div>'

        html_content += """
        </div>
        <div class="section">
            <h2 style="color: #27ae60;">[INFO] Mimari İyileştirmeler</h2>"""
            
        if report["improvements"]:
            for item in report["improvements"]:
                html_content += f'<div class="success item">[+] {item}</div>'
        else:
            html_content += '<div class="item" style="color: gray;">İyileştirme bulunamadı.</div>'

        html_content += """
        </div>
    </div>
</body>
</html>"""

        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"[*] HTML Raporu başarıyla oluşturuldu: {save_path}")
