import xml.etree.ElementTree as ET
import os
from typing import Dict

class XmlAnalyzer:
    def __init__(self, legacy_xml_path: str, new_xml_path: str):
        self.legacy_xml_path = legacy_xml_path
        self.new_xml_path = new_xml_path

    def _parse_xml_safely(self, filepath: str) -> ET.Element:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            if "<?xml" in content:
                content = content.split("?>")[-1]
            return ET.fromstring(f"<DummyRoot>{content}</DummyRoot>")
        except ET.ParseError as e:
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
        print("[REPORT] SONAR/LINTER SEVİYESİ XML MİMARİ ANALİZ RAPORU")
        print("="*75)
        print(f"[*] Eski Sistem: {report['legacy_count']} Değişken | Yeni Sistem: {report['new_count']} Değişken")
        print("-" * 75)
        if report["critical"]:
            print("[CRITICAL] KRİTİK BULGULAR (Veri Kaybı)")
            for item in report["critical"]: print(f"  [-] {item}")
        if report["warnings"]:
            print("[WARNING] TİP VE YAPI UYARILARI")
            for item in report["warnings"]: print(f"  [!] {item}")
        if report["improvements"]:
            print("[INFO] MİMARİ İYİLEŞTİRMELER (Best Practices)")
            for item in report["improvements"]: print(f"  [+] {item}")
        if not report["critical"] and not report["warnings"]:
            print("[OK] KUSURSUZ UYUM: Veri kaybı veya tip uyuşmazlığı bulunamadı. Yapı güvenli.")
        print("="*75 + "\n")

    def export_html_report(self, save_path="rapor.html"):
        report = self.analyze()
        if report["status"] == "error":
            print(f"[HATA] HTML Raporu oluşturulamadı: {report['message']}")
            return

        html_content = f"""<!DOCTYPE html>
