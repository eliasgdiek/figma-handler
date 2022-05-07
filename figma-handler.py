from figma import Figma
import json

def migrate():
    try:
        figma = Figma()
        figma.createDB()
        figma.createTables()
        return 'success'
    except:
        print('[ERROR in migrate]')
        return 'failed'

def getAllProjects():
    try:
        figma = Figma()
        code = figma.getCode()
        figma.authenticate(code)
        teamId = '1103011244724301023'
        projects = figma.getProjectsFromDB(teamId)
        print('[projects]', projects)

        return projects
    except:
        print('[ERROR in getFiles]')
        return None

def getAllFiles():
    try:
        figma = Figma()
        code = figma.getCode()
        figma.authenticate(code)
        teamId = '1103011244724301023'
        projects = figma.getProjectsFromDB(teamId)
        allFiles = []
        for project in projects:
            project_id = project[4]
            files = figma.getFilesFromDB(project_id)
            for file in files:
                allFiles.append(file)
        
        print('[allFiles]', allFiles)
        return allFiles
    except:
        print('[ERROR in getFiles]')
        return None

def fetchAll():
    try:
        figma = Figma()
        code = figma.getCode()
        userData = figma.authenticate(code)
       
        teamId = '1103011244724301023'
        files, projectData = figma.fetchFiles(teamId)

        userId = userData['user_id']

        with open("user-"+ str(userId) +".json", "w") as f:
            json.dump(userData, f)

        with open("files-"+ str(userId) +".json", "w") as f:
            json.dump(files, f)

        with open("projects-"+ str(userId) +".json", "w") as f:
            json.dump(projectData, f)

        return 'success'
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print('[Error fetchAll]', message)
        return 'failed'

if __name__ == '__main__':
    # getAllFiles()
    fetchAll()
    # migrate()