import requests


class DAODomains:
    def __init__(self, app):
        self.requests = requests
        self.api = app.config['APIGATEWAY_URL']

    def get_domains(self, org, token):
        response = self.requests.post(
            self.api,
            json={
                'query': '''{
                    domain(org: "test-pr") {
                        domains {
                            name,
                            org,
                        },
                        error
                    }
                }'''
            },
            cookies={
                'accessToken': token.split(' ')[1]
            }
        )
        return response.json()['data']['domain']['domains']

    def check_domain_access(self, domain, org, token):
        return domain in [d['name'] for d in self.get_domains(org, token)]
