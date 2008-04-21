###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2008, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

import Products.ZenModel.RRDDataSource as RRDDataSource
from Products.ZenModel.ZenPackPersistence import ZenPackPersistence
from AccessControl import ClassSecurityInfo, Permissions
from Products.ZenUtils.ZenTales import talesCompile, getEngine

class LDAPMonitorDataSource(ZenPackPersistence, RRDDataSource.RRDDataSource):
    
    LDAP_MONITOR = 'LDAPMonitor'
    
    sourcetypes = (LDAP_MONITOR,)
    sourcetype = LDAP_MONITOR

    eventClass = '/Status/LDAP'
        
    ldapServer = '${dev/id}'
    ldapBaseDN = '${here/zLDAPBaseDN}'
    ldapBindDN = '${here/zLDAPBindDN}'
    ldapBindPassword = '${here/zLDAPBindPassword}'
    useSSL = False
    port = 389
    timeout = 60

    _properties = RRDDataSource.RRDDataSource._properties + (
        {'id':'ldapServer', 'type':'string', 'mode':'w'},
        {'id':'ldapBaseDN', 'type':'string', 'mode':'w'},
        {'id':'ldapBindDN', 'type':'string', 'mode':'w'},
        {'id':'ldapBindPassword', 'type':'string', 'mode':'w'},
        {'id':'useSSL', 'type':'boolean', 'mode':'w'},
        {'id':'port', 'type':'int', 'mode':'w'},
        {'id':'timeout', 'type':'int', 'mode':'w'},
        )
        
    _relations = RRDDataSource.RRDDataSource._relations + (
        )


    factory_type_information = ( 
    { 
        'immediate_view' : 'editLDAPMonitorDataSource',
        'actions'        :
        ( 
            { 'id'            : 'edit',
              'name'          : 'Data Source',
              'action'        : 'editLDAPMonitorDataSource',
              'permissions'   : ( Permissions.view, ),
            },
        )
    },
    )

    security = ClassSecurityInfo()


    def __init__(self, id, title=None, buildRelations=True):
        RRDDataSource.RRDDataSource.__init__(self, id, title, buildRelations)
        #self.addDataPoints()


    def getDescription(self):
        if self.sourcetype == self.LDAP_MONITOR:
            return self.ldapServer + self.ldapBaseDN
        return RRDDataSource.RRDDataSource.getDescription(self)


    def useZenCommand(self):
        return True


    def getCommand(self, context):
        parts = self.useSSL and ['check_ldaps'] or ['check_ldap']
        if self.ldapServer:
            parts.append('-H %s' % self.ldapServer)
        if self.ldapBaseDN:
            parts.append('-b %s' % self.ldapBaseDN)
        if self.ldapBindDN:
            parts.append('-D %s' % self.ldapBindDN)
        if self.ldapBindPassword:
            parts.append('-P %s' % self.ldapBindPassword)
        if self.port:
            parts.append('-p %d' % self.port)
        if self.timeout:
            parts.append('-t %d' % self.timeout)

        cmd = ' '.join(parts)
        cmd = '$ZENHOME/libexec/' + \
                    RRDDataSource.RRDDataSource.getCommand(self, context, cmd)
        return cmd


    def checkCommandPrefix(self, context, cmd):
        return cmd


    def addDataPoints(self):
        if not hasattr(self.datapoints, 'time'):
            self.manage_addRRDDataPoint('time')


    def zmanage_editProperties(self, REQUEST=None):
        '''validation, etc'''
        if REQUEST:
            # ensure default datapoint didn't go away
            self.addDataPoints()
            # and eventClass
            if not REQUEST.form.get('eventClass', None):
                REQUEST.form['eventClass'] = self.__class__.eventClass
        return RRDDataSource.RRDDataSource.zmanage_editProperties(self, REQUEST)


