import argparse
import os
import glob

# Kurumsal Mimarimizden İçe Aktarımlar
from helpers.file_helper import FileHelper
from helpers.string_helper import StringHelper
from core.dds_converter import DdsConverter
from core.xml_analyzer import XmlAnalyzer

def main():
    parser = argparse.ArgumentParser(description="Otomatik JSON-XML Otomasyonu (Headless/Server Mode)")
    parser.add_argument("-c", "--config", default="company_rules.json", help="Sistem Ayar Dosyası")
    parser.add_argument("--html", action="store_true", help="Analiz sonucunu HTML olarak çıkartır")
    args = parser.parse_args()

    config_data = FileHelper.load_json(args.config)
    if not config_data:
        print(f"[ERROR] Config dosyası bulunamadı: {args.config}")
        return

    paths = config_data.get("paths", {})
    input_folder = paths.get("input_json_folder", "./test_jsonlar")
    output_folder = paths.get("output_xml_folder", "./sonuclar")
    legacy_folder = paths.get("legacy_xml_folder", "./eski_sistemler")

    converter = DdsConverter(config=config_data)

    print("="*60)
    print("[START] HEADLESS (ARAYÜZSÜZ) OTOMASYON BAŞLATILIYOR...")
    print("="*60)
    
    grouped_jsons = {}
    item_tracker = {}
    
    if os.path.exists(input_folder):
        json_files = sorted(glob.glob(os.path.join(input_folder, "*.json")))
        print(f"\n[INFO] {len(json_files)} adet JSON bulundu. Gruplama ve Tekrar Önleme yapılıyor...")
        
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

    os.makedirs(output_folder, exist_ok=True)
    üretilen_xmller = []
    print(f"\n[INFO] {len(grouped_jsons)} Master XML oluşturuluyor...")
    
    for grup, json_list in grouped_jsons.items():
        out_file = os.path.join(output_folder, f"{grup}.xml")
        
        xml_result = converter.convert(json_list) 
        FileHelper.save_file(out_file, xml_result)
        
        toplam_degisken = sum(len(j["items"]) for j in json_list)
        print(f"  [+] Üretildi: {out_file} ({len(json_list)} Struct, {toplam_degisken} Benzersiz Değişken)")
        üretilen_xmller.append(out_file)

    if legacy_folder and os.path.exists(legacy_folder):
        print(f"\n[INFO] Kıyaslama Motoru (Analyzer) Başlatıldı...")
        for new_xml in üretilen_xmller:
            filename = os.path.basename(new_xml)
            legacy_xml = os.path.join(legacy_folder, filename)
            
            if os.path.exists(legacy_xml):
                print(f"\n>>> {filename} için Analiz:")
                analyzer = XmlAnalyzer(legacy_xml_path=legacy_xml, new_xml_path=new_xml)
                analyzer.print_terminal_report()
                if args.html:
                    analyzer.export_html_report(f"rapor_{filename.replace('.xml', '.html')}")
            else:
                print(f"  [-] Eski sistemde {filename} bulunamadı.")
    print("\n[OK] İŞLEM TAMAMLANDI!")

if __name__ == "__main__":
    main()
