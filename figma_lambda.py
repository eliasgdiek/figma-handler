import base64
import string
import random
import urllib3
import sqlite3
from sqlite3 import Error
import os
import json

DB_NAME = '/tmp/fabric.db'
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
            print('[dddddd]', data)
            self.authData = data
            userData = self.getUserData()
            self.userData = userData
            data['userData'] = userData

            connectionData = self.checkConnection(userData['email'])
            if connectionData == False:
                isSaved = self.saveUser(data)
                print('[isSaved]', isSaved)

            user = self.getUserFromDB(userData['email'])
            self.userId = user[0]

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
            print('[projectData]', projectData)

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
            print('[filesData]', filesData)
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
                conn = sqlite3.connect(DB_NAME)
                try:
                    sql = "INSERT INTO projects (user_id, team_id, team_name, project_id, project_name) VALUES (?, ?, ?, ?, ?)"
                    val = (self.userId, teamId, teamName, project['id'], project['name'])
                    conn.execute(sql, val)
                    conn.commit()
                except:
                    try:
                        sql = "UPDATE projects SET user_id = ?, team_id = ?, team_name = ?, project_name = ? WHERE project_id = ?"
                        val = (self.userId, teamId, teamName, project['name'], project['id'])
                        conn.execute(sql, val)
                        conn.commit()
                    except:
                        pass

                filesData = self.fetchFilesInProject(project['id'])

                if len(filesData['files']) == 0:
                    print('[fetchFiles]', 'No files found in your team project')
                    return None

                for file in filesData['files']:
                    files.append(file)
                    try:
                        sql = "INSERT INTO files (user_id, project_id, key, name, thumbnail_url, last_modified) VALUES (?, ?, ?, ?, ?, ?)"
                        val = (self.userId, project['id'], file['key'], file['name'], file['thumbnail_url'], file['last_modified'])
                        conn.execute(sql, val)
                        conn.commit()
                    except:
                        try:
                            sql = "UPDATE files SET user_id = ?, project_id = ?, name = ?, thumbnail_url = ?, last_modified = ? WHERE key = ?"
                            val = (self.userId, project['id'], file['name'], file['thumbnail_url'], file['last_modified'], file['key'])
                            conn.execute(sql, val)
                            conn.commit()
                        except:
                            pass
                
            
            conn.close()
            return files
            
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print('[Error fetchFiles]', message)
            return None

    def createDB(self):
        conn = None
        try:
            conn = sqlite3.connect(DB_NAME)
            print(sqlite3.version)
        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()
    
    def createTables(self):
        conn = None
        try:
            conn =sqlite3.connect(DB_NAME)
            myCursor = conn.cursor()
            sql = "CREATE TABLE users (\
                    id INTEGER PRIMARY KEY AUTOINCREMENT,\
                    email VARCHAR(255) NOT NULL UNIQUE,\
                    figma_id VARCHAR(255) NULL,\
                    figma_handle VARCHAR(255) NULL,\
                    figma_img VARCHAR(1000) NULL,\
                    state VARCHAR(50) NOT NULL,\
                    access_token VARCHAR(255) NOT NULL,\
                    refresh_token VARCHAR(255),\
                    expires_in INT,\
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,\
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP);"
            myCursor.execute(sql)
            sql = "CREATE TABLE projects (\
                    id INTEGER PRIMARY KEY AUTOINCREMENT,\
                    user_id INTEGER NOT NULL,\
                    team_id VARCHAR(255) NOT NULL,\
                    team_name VARCHAR(255) NOT NULL,\
                    project_id VARCHAR(255) NOT NULL UNIQUE,\
                    project_name VARCHAR(255) NOT NULL,\
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,\
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP\
                );"
            myCursor.execute(sql)
            sql = "CREATE TABLE files (\
                    id INTEGER PRIMARY KEY AUTOINCREMENT,\
                    user_id INTEGER NOT NULL,\
                    project_id VARCHAR(255) NOT NULL,\
                    key VARCHAR(255) NOT NULL UNIQUE,\
                    name VARCHAR(255) NOT NULL,\
                    thumbnail_url TEXT NULL,\
                    last_modified DATETIME NOT NULL,\
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,\
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP\
                );"
            myCursor.execute(sql)

        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()
