import xml.etree.ElementTree as ET
from xml.dom import minidom
from interfaces.iconverter import IConverter
from core.type_analyzer import TypeAnalyzer
from helpers.string_helper import StringHelper

class DdsConverter(IConverter):
    def __init__(self, config: dict):
        self.config = config
        self.analyzer = TypeAnalyzer(config)

    def convert(self, json_data_list: list) -> str:
        remove_pref = self.config.get("naming", {}).get("remove_prefix", "msg")
        add_pref = self.config.get("naming", {}).get("add_prefix", "Type")

        # HİLE: XML'in çökmemesi için geçici bir <DummyRoot> açıyoruz.
        wrapper = ET.Element("DummyRoot")

        for json_data in json_data_list:
            raw_name = json_data.get("name", "Unknown")
            struct_name = StringHelper.format_struct_name(raw_name, remove_pref, add_pref)

            struct_element = ET.SubElement(wrapper, "struct", name=struct_name)
            items = json_data.get("items", [])

            for item in items:
                raw_type = item.get("type", "")
                raw_name_item = item.get("name", "")
                
                clean_name = StringHelper.clean_member_name(raw_name_item)
                member_element = ET.SubElement(struct_element, "member", name=clean_name)
                
                if self.analyzer.is_basic(raw_type):
                    final_type = "u_int16" if raw_type in ["unint", "uint"] else raw_type
                    member_element.set("type", final_type)
                else:
                    member_element.set("type", "nonBasic")
                    mapped_name = self.analyzer.map_type_name(raw_type)
                    member_element.set("nonBasicTypeName", mapped_name)
                    
        rough_string = ET.tostring(wrapper, encoding='utf-8', method='xml')
        parsed = minidom.parseString(rough_string)
        pretty_xml = parsed.toprettyxml(indent="  ")
        
        # HİLEYİ TEMİZLEME: DummyRoot etiketlerini metinden kesip atıyoruz
        lines = pretty_xml.split('\n')
        final_lines = []
        for line in lines:
            if "<DummyRoot>" in line or "</DummyRoot>" in line:
                continue
            if line.strip():
                if line.startswith("  "):
                    final_lines.append(line[2:]) # Hizayı bir tık geri çek
                else:
                    final_lines.append(line)
                    
        return '\n'.join(final_lines)
