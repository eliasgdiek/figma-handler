from figma import Figma

def migrate():
    figma = Figma()
    figma.createDB()
    figma.createTables()

def main():
    figma = Figma()
    figma.authenticate()
    
    teamId = '1103011244724301023'
    figma.fetchFiles(teamId)

if __name__ == '__main__':
    main()
    # migrate()