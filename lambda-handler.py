import json
from figma import Figma

def lambda_handler(event, context):
    try:
        # figma = Figma()
        # figma.createDB()
        # figma.createTables()
        # return {
        #     'statusCode': 200,
        #     'body': json.dumps('ok')
        # }
        
        print('[event]', event)
        params = json.loads(event["body"])
        code = params["code"]
        teamId = params["team_id"]
        redirectUri = params["redirect_uri"]
        print('[params]', params)

        figma = Figma()
        figma.authenticate(code, redirectUri)
        files = figma.fetchFiles(teamId)
        
        return {
            'statusCode': 200,
            'body': json.dumps(files)
        }
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print('[lambda_handler]', message)
        return {
            'statusCode': 500,
            'body': json.dumps('error')
        }