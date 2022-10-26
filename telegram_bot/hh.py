import requests
import json

class Vacancies():
    hh_url = url = "https://api.hh.ru/vacancies"
    params = {
    'text': 'NAME:devops Кипр',
    'area': 1,
    'per_page': 100
    }
    def send_request(self, req_url, req_params):
        req = requests.get(url=req_url, params=req_params)
        data = req.content.decode()
        data = req.json()
        req.close()
        return data

    def get_vacancies(self):
        found_cyprus_job = []
        vacancies = self.send_request(self.hh_url, self.params)
        for i in vacancies['items']:
            job_name = i['name']
            job_url = i['alternate_url']
            salary = i['salary']
            if salary == None:
                salary = "не указана"
            else:
                salary_from = salary['from']
                salary_to = salary['to']
                currency = salary['currency']
                gross = salary['gross']
                if salary_from == None:
                    salary_from = "0"
                elif salary_to == None:
                    salary_to = "0"
                if gross == False:
                    gross = "до вычета"
                elif gross == True:
                    gross = "на руки"
                salary = f"от {salary_from} до {salary_to} {currency} {gross}"
            jobs = f"Вакансия: {job_name}, ЗП: {salary}, URL: {job_url}"
            found_cyprus_job.append(jobs)
        message = "\n\n".join(map(str, found_cyprus_job))
        return message

