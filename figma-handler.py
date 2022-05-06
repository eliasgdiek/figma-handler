from figma import Figma

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
        data = figma.authenticate(code)
        print('[data]', data)
        
        # teamId = '1103011244724301023'
        # figma.fetchFiles(teamId)

        return 'success'
    except:
        print('[ERROR in fetchAll]')
        return 'failed'

if __name__ == '__main__':
    # getAllFiles()
    fetchAll()
    # migrate()