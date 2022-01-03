import ldap
import passlib.hash


class MockDAO:
    def __init__(self, app):
        self.base = app.config['LDAP_BASE']
        self.db = {}

    def _look_for_email(self, mail):
        # sum([len(list(filter(lambda i:i[1]=="mb1", y))) for y in x.values()])
        print("AAAAA")
        for entry in self.db.values():
            print(entry)
            if list(filter(lambda i: i[1] == mail.encode(), entry)):
                return True
        return False

    def create_user(self, login, gn, sn, mail, password, org="users"):
        dn = "cn={login},ou={org},{base}".format(
                login=login,
                base=self.base, org=org
            )
        pass_hash = passlib.hash.sha512_crypt.hash(password).encode()
        if self._look_for_email(mail):
            raise ldap.ALREADY_EXISTS
        if self.db.get(dn, None):
            raise ldap.ALREADY_EXISTS
        entry = [
            ('objectClass', [b"inetOrgPerson"]),
            ('cn', login.encode()),
            ('gn', gn.encode()),
            ('sn', sn.encode()),
            ('mail', mail.encode()),
            ('userPassword', "{crypt}%s" % pass_hash),
        ]
        self.db[dn] = entry
