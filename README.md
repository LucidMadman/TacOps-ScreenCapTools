# TacOps Screen Capture Tools
Designed to streamline the processing and uploading of large screencapture sets.

Takes the output of the [Enfusion Map Maker](https://github.com/nickludlam/EnfusionMapMaker), converts the screen captures to .webp format and creates a zip archive that preserves the folder structure required for post processing.

Also provides an upload client to upload the zip archive to an AWS server and returns a URL for download of the archive valid for 7 days.

## AWS credentials
To store the AWS credentials locally use the AWS CLI to configure a credential file locally.
### OR
Manually add a config and credential file in `%USERPROFILE%\.aws\`

Config File contains:
```
[default]
region = eu-central-1
output = json
```
credentials file contains:
```
[default]
aws_access_key_id = *example access key*
aws_secret_access_key = *example access key secret*
```
## Enfusion Map Maker
The code to automate the screenshot capture can be downloaded from Nick Ludlam's Github repo [Enfusion Map Maker](https://github.com/nickludlam/EnfusionMapMaker).
This guide is a slightly modified version of Nick's own guide for his script to suit the workflow required to ingeast maps to the TacOps platform.
1) Either clone the repo or download it directly on your local machine somewhere that can be accessed by Arma Reforger Tools.
2) Open Open Reforger Tools and choose 
