import requests
from requests_toolbelt.utils import dump
#import urllib.parse
from urlparse import urlparse
import json


class OracleComputeCloud():
    '''
    this class encapsulates operations that can be performed on Oracle Compute Cloud service
    '''

    # get operations

    def __init__(self, endPointUrl, authenticationDomain, cookies=None):
        '''
        Must provide an end point URL and an authentication domain
        '''

        self.__endPointUrl = endPointUrl
        self.__authenticationDomain = authenticationDomain
        self.__cookies = cookies
        self.__contentType = 'application/oracle-compute-v3+json'
        self.__accept = 'application/oracle-compute-v3+json'
        self.debug = False

        # define all resource paths
        self.resourcePaths = {
                                'ipAssociation': '/ip/association',
                                'securityApplication': '/secapplication',
                                'securityAssociation': '/secassociation',
                                'securityIPList': '/seciplist',
                                'securityList': '/seclist',
                                'securityRule': '/secrule',
                                'account': '/account',
                                'imageList': '/imagelist',
                                'machineImage': '/machineimage',
                                'instance': '/instance',
                                'shape': '/shape',
                                'SSHKey': '/sshkey',
                             }

    def login(self, user, password):
        '''
        returns cookies if login is successful, None otherwise
        '''
        if (self.__cookies != None):
            return self.__cookies

        url = self.__endPointUrl + '/authenticate/'
        headerString = {'Content-Type':self.__contentType, 'Accept':self.__accept}
        fullUsername = '/Compute-' + self.__authenticationDomain + '/' + user
        authenticationString = {"password": password, "user": fullUsername}

        response = requests.post(url, json=authenticationString, headers=headerString)

        #data = dump.dump_all(response)
        #print(data.decode('utf-8'))

        if response.status_code == 204:
            self.__cookies = response.cookies
            self.__user = user
            return response.cookies

    def refresh(self, cookies=None):
        if (cookies != None):
            self.__cookies = cookies

        url = self.__endPointUrl + '/refresh/'
        headerString = {'Content-Type':self.__contentType, 'Accept':self.__accept}
        response = requests.get(url, headers=headerString, cookies=self.__cookies)

        #data = dump.dump_all(response)
        #print(data.decode('utf-8'))

        if response.status_code == 204:
            return self.__cookies

    def buildContainerUri(self, isPublic=None, user=None):
        container = '/Compute-' + self.__authenticationDomain
        if isPublic == True:
            return  '/oracle/public'

        if user == None:
            return container #+ '/' + self.__user
        #else:
            #return container #+ '/' + user

    # utility methods
    def getResources(self, resourcePath, container, resourceName='ALL', queryParams=None):
        url = self.__endPointUrl + resourcePath

        if resourceName == 'ALL':
            url = url + container
            if not url.endswith('/'):
                url += '/'
            if queryParams != None and type(queryParams) is dict:
                url += '?' + urllib.parse.urlencode(queryParams)
            if url.endswith('?'):
                url = url[:-1]

        elif resourceName.startswith('/'):
            url = url + resourceName
        else:
            url = url + '/' + resourceName

        headerString = {'Content-Type':self.__contentType, 'Accept':self.__accept}
        response = requests.get(url, headers=headerString, cookies=self.__cookies)

        self.debugLog(response)

        if response.status_code == 200:
            jsonResponse = response.json()
            return (jsonResponse['result'] if resourceName=='ALL' else jsonResponse)
        elif response.status_code == 404:
            return []
        #else:
        #    raise OCCException('Response code: ' + str(response.status_code) + ', ' + str(response.content))

    def getIPAssociations(self, ipAssociationName='ALL', user=None, queryParams=None):
        resourcePath = self.resourcePaths['ipAssociation']
        container = self.buildContainerUri(user=user)
        return self.getResources(resourcePath, container, ipAssociationName, queryParams)

    def getSecurityApplications(self, securityApplicationName='ALL',  user=None, queryParams=None):
        resourcePath = self.resourcePaths['securityApplication']
        container = self.buildContainerUri( user=user)
        return self.getResources(resourcePath, container, securityApplicationName, queryParams)

    def getSecurityApplications1(self, securityApplicationName='ALL', isPublic=True, user=None, queryParams=None):
        resourcePath = self.resourcePaths['securityApplication']
        container = self.buildContainerUri(isPublic, user)
        return self.getResources(resourcePath, container, securityApplicationName, queryParams)

    def getSecurityAssociations(self, securityAssociationName='ALL', user=None, queryParams=None):
        resourcePath = self.resourcePaths['securityAssociation']
        container = self.buildContainerUri(user=user)
        return self.getResources(resourcePath, container, securityAssociationName, queryParams)

    def getSecurityIPLists(self, securityIPListName='ALL', user=None, queryParams=None):
        resourcePath = self.resourcePaths['securityIPList']
        container = self.buildContainerUri( user=user)
        return self.getResources(resourcePath, container, securityIPListName, queryParams)

    def getSecurityIPLists1(self, securityIPListName='ALL', isPublic=True, user=None, queryParams=None):
        resourcePath = self.resourcePaths['securityIPList']
        container = self.buildContainerUri(isPublic, user=user)
        return self.getResources(resourcePath, container, securityIPListName, queryParams)

    def getSecurityLists(self, securityListName='ALL', user=None):
        resourcePath = self.resourcePaths['securityList']
        container = self.buildContainerUri(user)
        return self.getResources(resourcePath, container, securityListName)

    def getSecurityRules(self, securityRuleName='ALL', user=None, queryParams=None):
        resourcePath = self.resourcePaths['securityRule']
        container = self.buildContainerUri(user)
        return self.getResources(resourcePath, container, securityRuleName, queryParams)

    def getAccounts(self, accountName='ALL'):
        resourcePath = self.resourcePaths['account']
        container = '/Compute-' + self.__authenticationDomain
        return self.getResources(resourcePath, container, accountName)

    def getImageLists(self, imageListName='ALL', isPublic=True, user=None):
        '''
        if imageListName == 'ALL'
            returns a list of dictionaries of image list details
        else
            returns a dictionary

        '''
        resourcePath = self.resourcePaths['imageList']
        container = self.buildContainerUri(user)
        return self.getResources(resourcePath, container, imageListName)

    def getMachineImages(self, machineImageName='ALL', isPublic=True, user=None):
        resourcePath = self.resourcePaths['machineImage']
        container = self.buildContainerUri(isPublic, user)
        return self.getResources(resourcePath, container, machineImageName)

    def getInstances(self, instanceName='ALL', user=None):
        '''
        if instanceName == 'ALL'
            returns a list of dictionaries of instance details
        else
            returns a dictionary
        '''
        resourcePath = self.resourcePaths['instance']
        container = self.buildContainerUri(user=user)
        return self.getResources(resourcePath, container, instanceName)

    def getShapes(self, shapeName='ALL'):
        '''
        if shapeName == None:
            return a list of dictionaries of all shapes, each of which contains a set of shape information
        else
            return a dictionaries of the named shape

        sample returns
        [{"nds_iops_limit": 0, "ram": 7680, "cpus": 2.0, "root_disk_size": 0, "uri": "https://api-z24.compute.us6.oraclecloud.com/shape/oc3", "io": 200, "name": "oc3"},
         {"nds_iops_limit": 0, "ram": 15360, "cpus": 2.0, "root_disk_size": 0, "uri": "https://api-z24.compute.us6.oraclecloud.com/shape/oc1m", "io": 200, "name": "oc1m"}]
        '''

        resourcePath = self.resourcePaths['shape']
        container = ''
        return self.getResources(resourcePath, container, shapeName)

    def getSSHKeys(self, sshKeyName='ALL', user=None):
        resourcePath = self.resourcePaths['SSHKey']
        container = self.buildContainerUri(user)
        return self.getResources(resourcePath, container, sshKeyName)

    '''
    utility operations
    '''
    def buildResourceName(self, simpleName):
        if not simpleName.startswith('/'):
            return "/Compute-" + self.__authenticationDomain + '/' + self.__user + '/' + simpleName
        else:
            return  "/Compute-" + self.__authenticationDomain + '/' + self.__user + simpleName

    def debugLog(self, response):
        # debug
        if self.debug:
            data = dump.dump_all(response)
            print(data.decode('utf-8'))


class OCCException(Exception):
    pass
    #return render_to_response('invalid.html')

