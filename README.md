# TimeWarp
Time Warp is the idea around node based warping of maya's time. This tool consists of two parts; it's custom node 
called warpStatus and the GUI interface that allows you to add remove and bake out warps.

------------

## Install
TimeWarp can be installed in multiple ways.
### Drag and Drop
For simple installation use the drag_drop_install.py file into maya's viewport. This will launch a GUI follow the prompts to install.

![adambakerart_maya_dnd](https://github.com/adamjrbaker/timeWarp/assets/25186874/e95516a3-be54-4615-bbdc-194eb227273c)

### Manual Install
1. Copy the folder "src/python/timeWarp" into your maya/scripts/ preferences directory. So your resulting path will be like:

    **Windows**
    `C:/Users/<user>/Documents/maya/scripts/timeWarp`

    **Linux (Centos)**
    `/home/<user>/maya/scripts/timeWarp`

    **OSX**
    `/Users/<user>/Library/Preferences/Autodesk/maya/timeWarp`
     *OSX Note: To open the Preferences directory:*
     *Select Finder > Go, press Alt and the Library folder will appear in the menu.*

2. Copy **timeWarp.mod** file to documents/maya/modules, create the folder “modules” if it does not exist.

3. Open the .mod file and change "/path/to/timeWarp" to your path to the TimeWarp folder. Hit save.
    **Windows**
    `C:/Users/<user>/Documents/maya/scripts/`

    **Linux (Centos)**
    `/home/<user>/maya/scripts/`

    **OSX**
    `/Users/<user>/Library/Preferences/Autodesk/maya/`
     *OSX Note: To open the Preferences directory:*
     *Select Finder > Go, press Alt and the Library folder will appear in the menu.*

4. While inside the timeWarp.mod file set the correct version number. this can be found in the _version.py file or in the download page.

5. Open Maya, the make sure plugin in loaded for menu to load.

## Overview

Time Warp is created to be as simple as possible for all animators to use, allowing them to quickly alter the speed of animation. With the control to alter single nodes over the default Maya time warp that alters the whole scene.

### UI
To launch the UI there are two options, from the menu or from a shelf button. If you choses to add a shelf button when using the Drag and Drop install method you will be presented with a new button on your Custom shelf.
![adambakerart_maya_gui](https://github.com/user-attachments/assets/3914bd46-7cf3-4a8d-ae3f-d760ce337e94)

If not or you do a manual install the UI can be launch from the ATK menu bar at the top of your maya session. From here you do have the ability to add a shelf button at any time.  For those who would like todo it yourself run the command:
```python 
from timeWarp.api import widget
widget.launch()
```
and the shelf icon can be found: `\timeWarp\icons\TimeWarpShelf.svg`

### Usage

#### Create
Creating a warp makes at WarpStatus node with the used defined name. This node will stay unevaluated until a node is added to the warp. Note this will create a warp the length of your timeline.

#### Adding To Warp
When you are ready selected the nodes you wish to add into this warp. You will see a new curve will appear. This will be your Warp Curve that your can manipulate to change the animation.
![adambakerart_maya_applyWarp](https://github.com/adamjrbaker/timeWarp/assets/25186874/f836cf8b-393d-4ced-93e9-51beb26d618e)

#### Bake Warp
The bake warp option provides a simple and convent way to convert the adjusted animation back to world time. This tool will bake the effected nodes on one's within the current frame range. Post bake the tool with then delete the warp from existence. If you would like to bake out only a select number of nodes effected by the warp you will need to selected them and bake it out using Maya'ss Bake Simulation option.