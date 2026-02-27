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

5) Now select the Enfusion Map Maker Project and right click -> Open with Addons
![Open With Addons](Docs/Img/OpenWithAddons.png)

6) Select the mod of the map that you wish to capture

7) Once the project has loaded open the world editor and then open the world file that you want to capture

8) We're going to create some marker points for the start and and of the capture to aid pos processing.  Once your world has loaded create a new sub-scene to place the markers in.

9) Place a find the Barrel_Filled.et and place one in the world at coords 0,0,0 and set it's scale to 10. Press F to jump the camera to that location.
![Barrel at Origin](Docs/Img/OriginBarrel.png)

10) From there you can look around and you'll see the World Bounds defined as a yellow wireframe box.  You want to move the camera to the opposite corner from where the origin barrel is placed. If you can't see the yellow bounding box check that you have World Bounds enabled in the View menu.
![World Bounds](Docs/Img/WorldBounds.png)

11) Move the camera to the opposite corner of the map and place another barrel on the opposite corner of the world box.  The world bounds box *should* always be square so make sure your a and z values are identical.  If there is terrain that needs to be captured very close to the edge of the world bounds map consider moving the barrel outside the world bounds.

**IMPORTANT** the barrel coordinates must but in multiples of the map step, for our workflow we use a map step of 100 so make sure the coordinates of the end barrel are rounded up to multpiles of 100.  e.g. if a map is 4096x4096 the barrel should be placed at 5000,0,5000.

12) Now open up the the weather editor panel and make sure the weather is set to clear.  Experiment with the time of day to find a sweat spot of the shadows not being too long but also having some. Usually late morning or early afternoon is baout right but each terrain si different.

13) Load up the Map Maker tool by selecting the Castle icon in the tool bar and selecting "current tool" in the properties window
![Launch Map Maker](Docs/Img/LaunchMapMaker.png)

14) If you have a second monitor it's helpful to move the Auto Screenshot tool and Log Console to the other monitor
![Tool windows](Docs/Img/ConsoleCaptureToolWindows.png)

15) In the Auto Camera Screenshot window set:
- Start Coords to 0,0,0 (same as the origin barrel)
- End Coords to the same as the end barrel
- Camera Height = 950
-  Absolute Camera Height disabeld
- Step Size = 100
- Field of View = 15
- Move sleep, adjust this to ensure that your machine has rendered everything in frame before the screenhot is captured, I use 1200 (ms)
- Discontinuous move sleep, same as move sleep but for large moves, I use 2000 (ms)
- Screenshot sleep, delay after a screenshot is taken before moving, I use 200 (ms)
- Screenshot Output, mapoutput (can be changed but only changes the folder name not location)
- Output File prefix = map name, no spaces keep it short the post processing tools use this to name the archive as well
- Tile Filename suffix, _tile.png
HDR Brightness = 0.000
![Auto Camera Screenshot Settings](Docs/Img/AutoCameraScreenshotSettings.png)

16) Now if you press the move to start and move to end buttons the camera should move to an exact top view of each barrel, lined up on the world bounds
