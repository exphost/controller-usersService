import ldap
import passlib.hash


class MockDAO:
    def __init__(self, app):
        self.base = app.config['LDAP_BASE']
        self.db = {}

    def create_user(self, login, gn, sn, mail, password, org="users"):
        dn = "cn={login},ou={org},{base}".format(
                login=login,
                base=self.base, org=org
            )
        pass_hash = passlib.hash.sha512_crypt.hash(password).encode()
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
