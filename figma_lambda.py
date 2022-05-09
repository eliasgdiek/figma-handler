import base64
import string
import random
import urllib3
import sqlite3
from sqlite3 import Error
import os
import json

http = urllib3.PoolManager()

class Figma():
    def __init__(self):
        print('[app]', os.environ['FIGMA_APP_NAME'])
        self.appName = os.environ['FIGMA_APP_NAME']
        self.clientId = os.environ['FIGMA_CLIENT_ID']
        self.clientSecret = os.environ['FIGMA_CLIENT_SECRET']
        self.baseURL = 'https://api.figma.com/v1'
        self.state = str(''.join(random.choices(string.ascii_uppercase + string.digits, k = 10)))
        self.scope = 'file_read'
        self.redirectUri = 'https://fabric-figma.vercel.app/figma'
        self.authData = None
        self.userData = None
        self.userId = None

    def getCode(self):
        try:
            codeUrl = 'https://www.figma.com/oauth?client_id='+ self.clientId +'&redirect_uri='+ self.redirectUri +'&scope='+ self.scope +'&state='+ self.state +'&response_type=code'
            print('Please visit the following URL, and enter the code below!')
            print(codeUrl)
            code = input("Enter code:")
            return code
        except:
            return ''

    def getUserData(self):
        try:
            header = { "Authorization": "Bearer " + self.authData['access_token'] }
            res = http.request('GET', self.baseURL + '/me', headers=header, retries = False)
            userData = json.loads(res.data.decode('UTF-8'))
            print('[userData]', userData)
            return userData
        except:
            return False

    def authenticate(self, code, redirectUri):
        try:
            _redirectURI = redirectUri if redirectUri else self.redirectUri
            authUrl = 'https://www.figma.com/api/oauth/token?client_id='+ self.clientId +'&client_secret='+ self.clientSecret +'&redirect_uri='+ _redirectURI +'&code='+ code +'&grant_type=authorization_code'
            res = http.request('POST', authUrl, retries = False)
            data = json.loads(res.data.decode('UTF-8'))
            data['state'] = self.state

            self.authData = data
            userData = self.getUserData()
            self.userData = userData
            data['userData'] = userData

            return data

        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
            return None

    def fetchProjects(self, teamId):
        try:
            header = { "Authorization": "Bearer " + self.authData['access_token'] }
            url = self.baseURL + '/teams/'+ teamId +'/projects'
            res = http.request('GET', url, headers=header, retries = False)
            projectData = json.loads(res.data.decode('UTF-8'))

            return projectData
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print('[Error fetchProjects]', message)
            return None

    def fetchFilesInProject(self, projectId):
        try:
            header = { "Authorization": "Bearer " + self.authData['access_token'] }
            url = self.baseURL + '/projects/'+ projectId +'/files'
            res = http.request('GET', url, headers=header, retries = False)
            filesData = json.loads(res.data.decode('UTF-8'))
            return filesData
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print('[Error fetchProjects]', message)
            return None


    def fetchFiles(self, teamId):
        try:
            projectData = self.fetchProjects(teamId)
            teamName = projectData['name']
            projects = projectData['projects']
            files = []

            if len(projects) == 0:
                print('[fetchFiles]', 'No projects found in the provied team')
                return None

            for project in projects:
                filesData = self.fetchFilesInProject(project['id'])
                for file in filesData['files']:
                    files.append(file)

            return (files, projectData)
            
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print('[Error fetchFiles]', message)
            return None
