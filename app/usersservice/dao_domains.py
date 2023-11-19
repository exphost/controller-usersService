import requests


class DAODomains:
    def __init__(self, app):
        self.requests = requests
        self.api = app.config['DOMAINSSERVICE_ENDPOINT']

    def get_domains(self, org, token):
        response = self.requests.get(
            self.api + '/api/domains/v1/domains/?org=' + org,
            headers={'Authorization': token}
        )
        return response.json()

    def check_domain_access(self, domain, org, token):
        return domain in [d['name'] for d in self.get_domains(org, token)]
