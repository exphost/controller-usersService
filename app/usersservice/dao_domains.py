import requests


class DAODomains:
    def __init__(self, app):
        self.requests = requests
        self.api = app.config['APIGATEWAY_URL']

    def get_domains(self, org, token):
        query = '''query GetDomains($org: String) {
            domain(org: $org) {
                domains {
                    name,
                    org,
                },
                error
            }
        }'''
        variables = {'org': org}
        response = self.requests.post(
            self.api,
            json={
                "query": query,
                "variables": variables
            },
            cookies={
                'accessToken': token.split(' ')[1]
            }
        )
        print(response.json())
        return response.json()['data']['domain']['domains']

    def check_domain_access(self, domain, org, token):
        return domain in [d['name'] for d in self.get_domains(org, token)]
