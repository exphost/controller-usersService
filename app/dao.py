import ldap
import passlib.hash
class DAO:
    def __init__(self, base, uri, dn, password):
        self.base = base
        self.l = ldap.initialize(uri)
        self.l.simple_bind_s(dn,password)

    def create_user(self, login, gn, sn, mail, password, org="users"):
        dn="cn={login},ou={org},{base}".format(login=login, base=self.base, org=org)
        entry = [
            ('objectClass', [b"inetOrgPerson", b"postfixUser"]),
            ('cn', login.encode()),
            ('gn', gn.encode()),
            ('sn', sn.encode()),
            ('mail', mail.encode()),
            ('userPassword', ("{crypt}%s"%(passlib.hash.sha512_crypt.hash(password))).encode())
        ]
        print(dn, entry)
        print(self.l.add_s(dn, entry))
