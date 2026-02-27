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
2) Open Open Reforger Tools and choose Add Project -> Add Exisitng Project
![Open Project](Docs/Img/ChooseProject.png)
3) Navigate to the folder that you stored the Enfusion Map Marker files
4) Select the addon.gproj file in the enfusion folder
5) No select the Enfusion Map Maker Project and right click -> Open with Addons
![Open With Addons](Docs/Img/OpenWithAddons.png)
6) Select the mod of the map that you wish to capture
7) Once the project has loaded open the world editor and then open the world file that you want to capture
8) Load up the Map Maker tool by selecting the Castle icon in the tool bar and selecting "current tool" in the properties window
![Launch Map Maker](Docs/Img/LaunchMapMaker.png)

