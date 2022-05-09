import json
from figma import Figma
import boto3
import os

def lambda_handler(event, context):
    try:
        params = json.loads(event["body"])
        code = params["code"]
        teamId = params["team_id"]
        redirectUri = params["redirect_uri"]
        print('[code]', code)

        figma = Figma()
        userData = figma.authenticate(code, redirectUri)
        print('[userData]', userData)
        files, projectData = figma.fetchFiles(teamId)

        userId = userData['user_id']
        bucket_name = os.environ['BUCKET_NAME']

        s3_path_for_users = "data/" + "user-"+ str(userId) +".json"
        s3_path_for_files = "data/" + "files-"+ str(userId) +".json"
        s3_path_for_projects = "data/" + "projects-"+ str(userId) +".json"

        s3 = boto3.resource("s3")
        s3.Bucket(bucket_name).put_object(Key=s3_path_for_users, Body=json.dumps(userData))
        s3.Bucket(bucket_name).put_object(Key=s3_path_for_files, Body=json.dumps(files))
        s3.Bucket(bucket_name).put_object(Key=s3_path_for_projects, Body=json.dumps(projectData))
        
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