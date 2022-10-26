import wikipedia, re

class Wiki():
    wikipedia.set_lang("ru")
    def __init__(self, message_for_wiki):
        self.message_for_wiki = message_for_wiki

    def get_wiki_info(self):
        try:
            wiki_reponse = wikipedia.page(self.message_for_wiki)
            wiki_text = wiki_reponse.content[:1000]
            wiki_found = wiki_text.split(".")
            wiki_found = wiki_found[:-1]
            wiki_result = ""
            for item in wiki_found:
                if not('==' in item):
                    if(len((item.strip()))>3):
                        wiki_result = wiki_result + item + "."
                    else: 
                        break
            wiki_result=re.sub('\([^()]*\)', '', wiki_result)
            wiki_result=re.sub('\([^()]*\)', '', wiki_result)
            wiki_result=re.sub('\{[^\{\}]*\}', '', wiki_result)
            return wiki_result
        except Exception as e:
            return "Не найдено информации в Wikipedia"