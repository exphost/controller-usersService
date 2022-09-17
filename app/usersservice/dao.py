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

    def create_user(self, login, gn, sn, mail, password, org="users"):
        dn = "cn={login},ou={org},{base}".format(
            login=login,
            base=self.base,
            org=org
        )
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

    def get_user(self, cn):
        try:
            u = self.ldap.search_s("ou=users," + self.base,
                                   ldap.SCOPE_SUBTREE,
                                   "(cn={cn})".format(cn=cn),
                                   ['cn', 'mail', 'gn', 'sn']
                                   )[0][1]
            g = self.ldap.search_s("ou=groups," + self.base,
                                   ldap.SCOPE_SUBTREE,
                                   "(member=cn={cn},ou=users,{base})".format(
                                        cn=cn, base=self.base),
                                   ['cn'])
            groups = [x[1]['cn'][0].decode() for x in g]
            return {'cn': u['cn'][0].decode(),
                    'gn': u['givenName'][0].decode(),
                    'sn': u['sn'][0].decode(),
                    'mail': u['mail'][0].decode(),
                    'groups': groups
                    }

        except IndexError:
            return None

    def create_email(self, mail, cn, sn, password, aliases, ou="mails"):
        dn = "maildrop={mail},ou={ou},{base}".format(
            mail=mail,
            base=self.base,
            ou=ou
        )
        pass_hash = passlib.hash.sha512_crypt.hash(password)
        entry = [
            ('objectClass', [b"person", b"postfixUser"]),
            ('cn', cn.encode()),
            ('sn', sn.encode()),
            ('maildrop', mail.encode()),
            ('mailacceptinggeneralid', aliases),
            ('userPassword', ("{crypt}%s" % pass_hash).encode()),
        ]
        print(dn, entry)
        ret = self.ldap.add_s(dn, entry)
        print(ret)
        return ret

    def get_emails(self, domain, ou="mails"):
        mails = self.ldap.search_s(
            "ou=" + ou + "," + self.base,
            ldap.SCOPE_SUBTREE,
            "(mailacceptinggeneralid=*@{domain})".format(domain=domain),
            )
        return mails
