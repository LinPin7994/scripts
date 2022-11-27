from weather import Weather
from hh import Vacancies
from wiki import Wiki
from exchange import Exchange

def main():
    #city = input("Enter city: ")
    #w = Weather(city)
    #print(w.get_current_weather())
    #vac = Vacancies()
    #print(vac.get_vacancies())
    #w = input("Enter wiki request")
    #wiki = Wiki(w)
    #print(wiki.get_wiki_info())
    e = Exchange("EURRUB")
    resp = e.get_currency_exchange()
    print(resp)
if __name__ == "__main__":
    main()