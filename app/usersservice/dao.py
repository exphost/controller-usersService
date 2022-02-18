import ldap
import passlib.hash


class DAO:
    def __init__(self, app):
        self.base = app.config['LDAP_BASE']
        self.ldap = ldap.initialize(app.config['LDAP_URI'])
        self.ldap.simple_bind_s(
            app.config['LDAP_DN'],
            app.config['LDAP_PASSWORD']
        )

    def _look_for_email(self, mail):
        m = self.ldap.search_s(self.base,
                               ldap.SCOPE_SUBTREE,
                               "(mail={mail})".format(mail=mail),
                               ['mail']
                               )
        return m

    def create_user(self, login, gn, sn, mail, password, org="users"):
        dn = "cn={login},ou={org},{base}".format(
            login=login,
            base=self.base,
            org=org
        )
        if self._look_for_email(mail):
            raise ldap.ALREADY_EXISTS
        pass_hash = passlib.hash.sha512_crypt.hash(password)
        entry = [
            ('objectClass', [b"inetOrgPerson"]),
            ('cn', login.encode()),
            ('gn', gn.encode()),
            ('sn', sn.encode()),
            ('mail', mail.encode()),
            ('userPassword', ("{crypt}%s" % pass_hash).encode()),
        ]
        print(dn, entry)
        print(self.ldap.add_s(dn, entry))

    def create_group(self, name, owner, members, org="groups"):
        dn = "cn={name},ou={org},{base}".format(
                name=name,
                base=self.base, org=org
            )
        owner_dn = "cn={name},ou=users,{base}".format(
                name=owner,
                base=self.base,
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
        print(dn, entry)
        print(self.ldap.add_s(dn, entry))
