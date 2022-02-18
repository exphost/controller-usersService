import ldap
import passlib.hash


class MockDAO:
    def __init__(self, app):
        self.base = app.config['LDAP_BASE']
        self.users_db = {}
        self.groups_db = {}

    def _look_for_email(self, mail):
        # sum([len(list(filter(lambda i:i[1]=="mb1", y))) for y in x.values()])
        print("AAAAA")
        for entry in self.users_db.values():
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
        if self.users_db.get(dn, None):
            raise ldap.ALREADY_EXISTS
        entry = [
            ('objectClass', [b"inetOrgPerson"]),
            ('cn', login.encode()),
            ('gn', gn.encode()),
            ('sn', sn.encode()),
            ('mail', mail.encode()),
            ('userPassword', "{crypt}%s" % pass_hash),
        ]
        self.users_db[dn] = entry

    def create_group(self, name, owner, members, org="groups"):
        dn = "cn={name},ou={org},{base}".format(
                name=name,
                base=self.base, org=org
            )
        if self.groups_db.get(dn, None):
            raise ldap.ALREADY_EXISTS

        owner_dn = "cn={name},ou=users,{base}".format(
                name=owner,
                base=self.base
            )
        entry = [
            ('objectClass', [b"groupOfNames"]),
            ('cn', name.encode()),
            ('owner', owner_dn.encode()),
            ('member', ["cn={name},ou=users,{base}".format(
                name=member,
                base=self.base
            ).encode() for member in members])
        ]
        self.groups_db[dn] = entry
        return entry
