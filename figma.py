from dotenv import load_dotenv
from os.path import join, dirname
import os
import string
import random
import requests
import urllib3
import sqlite3
from sqlite3 import Error
import json

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

http = urllib3.PoolManager()

DB_NAME = 'fabric.db'

# http://localhost:3000/api/callback?code=2IHhCieGwQ24SmoIqq1W6cCIj&state=9F181CQ1HO

class Figma():
    def __init__(self):
        self.appName = os.environ.get('FIGMA_APP_NAME')
        self.clientId = os.environ.get('FIGMA_CLIENT_ID')
        self.clientSecret = os.environ.get('FIGMA_CLIENT_SECRET')
        self.baseURL = 'https://api.figma.com/v1'
        self.state = str(''.join(random.choices(string.ascii_uppercase + string.digits, k = 10)))
        self.scope = 'file_read'
        self.redirectUri = 'http://localhost:3000/figma'
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

    def getUserFromDB(self, email):
        try:
            conn = sqlite3.connect(DB_NAME)
            sql = "SELECT * from users WHERE email = (?)"
            var = (email, )
            myCursor = conn.execute(sql, var)
            result = myCursor.fetchone()
            return result
        except:
            return None

    def getProjectFromDB(self, projectId):
        try:
            conn = sqlite3.connect(DB_NAME)
            sql = "SELECT * from projects WHERE project_id = (?)"
            var = (projectId, )
            myCursor = conn.execute(sql, var)
            result = myCursor.fetchone()
            return result
        except:
            return None

    def getFileFromDB(self, fileKey):
        try:
            conn = sqlite3.connect(DB_NAME)
            sql = "SELECT * from files WHERE key = (?)"
            var = (fileKey, )
            myCursor = conn.execute(sql, var)
            result = myCursor.fetchone()
            return result
        except:
            return None

    def getProjectsFromDB(self, teamId):
        try:
            conn = sqlite3.connect(DB_NAME)
            sql = "SELECT * from projects WHERE team_id = (?)"
            var = (teamId, )
            myCursor = conn.execute(sql, var)
            result = myCursor.fetchall()
            return result
        except:
            return None

    def getFilesFromDB(self, projectId):
        try:
            conn = sqlite3.connect(DB_NAME)
            sql = "SELECT * from files WHERE project_id = (?)"
            var = (projectId, )
            myCursor = conn.execute(sql, var)
            result = myCursor.fetchall()
            return result
        except:
            return None

    def checkConnection(self, email):
        try:
            data = self.getUserFromDB(email)
            if data[1] == email:
                return True
            else:
                return False
        except:
            return False

    def saveUser(self, data):
        try:
            conn = sqlite3.connect(DB_NAME)
            sql = "INSERT INTO users (email, figma_id, figma_handle, figma_img, state, access_token, refresh_token, expires_in) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            val = (data['userData']['email'], data['userData']['id'], data['userData']['handle'], data['userData']['img_url'], data['state'], data['access_token'], data['refresh_token'], data['expires_in'])
            conn.execute(sql, val)
            conn.commit()
            conn.close()
            return True
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print('[saveUser]', message)
            return False

    def getUserData(self):
        try:
            header = { "Authorization": "Bearer " + self.authData['access_token'] }
            res2 = requests.get(self.baseURL + '/me', headers = header)
            userData = res2.json()
            return userData
        except:
            return False

    def authenticate(self, code):
        try:
            authUrl = 'https://www.figma.com/api/oauth/token?client_id='+ self.clientId +'&client_secret='+ self.clientSecret +'&redirect_uri='+ self.redirectUri +'&code='+ code +'&grant_type=authorization_code'
            res = http.request('POST', authUrl, retries = False)
            data = json.loads(res.data.decode('UTF-8'))
            data['state'] = self.state
            self.authData = data
            userData = self.getUserData()
            self.userData = userData
            data['userData'] = userData

            # connectionData = self.checkConnection(userData['email'])
            # if connectionData == False:
                # isSaved = self.saveUser(data)

            # user = self.getUserFromDB(userData['email'])
            # self.userId = user[0]

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
            print('[res]', projectData)

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
            res = requests.get(url, headers=header)
            filesData = res.json()
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
