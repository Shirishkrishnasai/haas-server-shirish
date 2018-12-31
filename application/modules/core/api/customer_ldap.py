import ldap
import ldap.modlist as modlist

from application.config.common_config import ldap_connection,ldap_connection_dn,ldap_connection_password

def ldapcustomer():
    connect = ldap.initialize(ldap_connection)
    connect.simple_bind_s(ldap_connection_dn, ldap_connection_password)
# The dn of our new entry/object
    dn="ou=customer7,dc=kwartile,dc=local"

# A dict to help build the "body" of the object
    attrs = {}
    attrs['objectclass'] = ['top', 'organizationalRole', 'simpleSecurityObject']
    attrs['ou'] = 'customer7'
    attrs['cn']='ldapadm'
    attrs['userPassword'] = 'aDifferentSecret'
    attrs['description'] = 'User object for replication using slurpd'
    # Convert our dict to nice syntax for the add-function using modlist-module
    ldif = modlist.addModlist(attrs)

# Do the actual synchronous add-operation to the ldapserver
    data=connect.add_s(dn,ldif)
    print data
    