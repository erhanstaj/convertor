class StringHelper:
    @staticmethod
    def clean_member_name(name: str) -> str:
        return name.rstrip('_')

    @staticmethod
    def format_struct_name(raw_name: str, remove_pref: str, add_pref: str) -> str:
        if raw_name.lower().startswith(remove_pref.lower()):
            clean_name = raw_name[len(remove_pref):]
        else:
            clean_name = raw_name

        if clean_name.islower():
            clean_name = clean_name.capitalize()
            
        return f"{add_pref}{clean_name}"
