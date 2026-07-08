# <img src="assets/images/vismot.svg" alt="Vismot logo" width="45" align="texttop"> Vismot 
Vismot is a tool designed to elicit linear smooth pursuit and saccadic eye movements in a controlled and standardised manner for research and therapeutic applications.

## Usage
Upon running the program the user is presented with a visual target in the form of a circle that oscillates. Pressing `space` toggles the display of an enumerated list of definable settings, and pressing the number corresponding to a specific setting while pressing `left` or `right` will change the value of said setting.

The settings are as follows:
1.  **Angle** defines the angle of the linear oscillation. One can also press `r` to quickly inverse this angle.
2. **Size** defines the diameter in pixels of the visual target.
3. **Speed** defines frequency of the oscillation.
4. **Motion** defines the waveform of the oscillation. Here the sine and triangle wave will elicit smooth pursuit eye movements, while the square wave will elicit saccadic eye movements.
5. **Theme** defines the color scheme of the application. 
6. **Axes** defines whether or not to display the axis and the perpendicular axis of the oscillation angle. 
7. **Amplitude** defines the amplitude of the oscillation.

These settings are retained across sessions and can be shared via the `settings.json' file for replication purposes.

## Installation

### For Windows Users (Download & Run)

1. Go to the [Releases](https://github.com/ErikNikolajsen/Vismot/releases) page.
2. Download the latest `Vismot.zip` file.
3. Extract the ZIP archive anywhere on your PC.
4. Double-click `Vismot.exe` to run the application.

### For Developers (Run from Code)

1. Install Python (tested to work on 3.11)
2. Install Pygame (tested to work on 2.6.1) via:
```sh
pip install pygame
```
3. Open a shell and set the working directory to the root of the project.
4. Run the application via.:
```sh
python main.py
```


## Support
Please contact <erik.nikolajsen@gmail.com> for enquiries concerning the application.

## License
This project is proprietary. All rights are reserved by the copyright holder. For full details, please refer to the [LICENSE](https://github.com/ErikNikolajsen/Vismot/blob/main/LICENSE.txt) file.
