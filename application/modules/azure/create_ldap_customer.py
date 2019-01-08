import ldap

import ldap.modlist as modlist
from application.config.config_file import ldap_connection, ldap_connection_dn, ldap_connection_password
from application.models.models import TblCustomer, TblUsers
from application import app, db


def azureldapcustomer(customer_id, display_name, customer_gid_id, user_principal_name, mail_nickname, customer_email,
                      password):
    #   try:

    connect = ldap.initialize(ldap_connection)
    connect.simple_bind_s(ldap_connection_dn, ldap_connection_password)

    # The dn of our new entry/object

    dn = "ou=" + customer_id + ",dc=kwartile,dc=local"

    # A dict to help build the "body" of the object

    ou_attrs = {}
    ou_attrs['objectclass'] = ['top', 'organizationalRole', 'simpleSecurityObject']
    ou_attrs['ou'] = customer_id
    ou_attrs['cn'] = 'ldapadm'
    ou_attrs['userPassword'] = 'aDifferentSecret'
    ou_attrs['description'] = 'User object for replication using slurpd'
    if customer_gid_id == None:
        gid_id = 500
    else:
        gid_id = customer_gid_id + 1
    ou_creation = modlist.addModlist(ou_attrs)
    connect.add_s(dn, ou_creation)
    #	gid_id=500
    # The dn of our new entry/object

    dn1 = "cn=" + str(display_name) + "," + "ou=" + str(customer_id) + ",dc=kwartile,dc=local"
    group_attr = {}
    group_attr['objectClass'] = ['posixGroup', 'top']

    # A dict to help build the "body" of the object

    group_attr['cn'] = str(display_name)
    group_attr['description'] = 'ini group untuk semua dosen dokter'
    group_attr['gidNumber'] = str(gid_id)
    my_logger.info(group_attr)
    group_creation = modlist.addModlist(group_attr)
    connect.add_s(dn1, group_creation)
    update_customer_query = db.session.query(TblCustomer).filter(TblCustomer.uid_customer_id == customer_id)
    update_customer_query.update({"int_gid_id": gid_id})
    update_customer_query.update({"txt_customer_dn": dn1})
    db.session.commit()

    dn_user = "cn=" + str(customer_email) + ",cn=" + str(display_name) + ",ou=" + customer_id + ",dc=kwartile,dc=local"
    userlist = {
        "objectClass": ["inetOrgPerson", "posixAccount"],
        "uid": [str(user_principal_name)],
        "sn": [str(mail_nickname)],
        "displayName": [str(display_name)],
        "userPassword": [str(password)],
        "uidNumber": ["1021"],
        "gidNumber": [str(gid_id)],
        "loginShell": ["/bin/bash"],
        "homeDirectory": ["/home/users/"]
    }
    # addModList transforms your dictionary into a list that is conform to ldap input.
    addinguser = connect.add_s(dn_user, ldap.modlist.addModlist(userlist))
    user_insertion = TblUsers(uid_customer_id=customer_id, var_user_name=customer_email, txt_dn=dn_user, bool_active=1)
    db.session.add(user_insertion)
    db.session.commit()
#    except Exception as e:
#        return e.message
#    except ldap.LDAPError as e:
#        return jsonify(str(e))
