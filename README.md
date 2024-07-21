# Pyqt5-MonitorGUI

This is a desktop application based on the PyQt5 library, designed for energy management and thermal comfort monitoring in office buildings.

## Features

### Main Window
![Main Window](Image/2.png)
- Displays measurement data and machine learning results
- Allows users to change tags and report energy-saving information

### Login Window
![Login Window 1](Image/0.png) ![Login Window 2](Image/01.png)
- User account sign-in functionality
- Option to change device location near user's seat

### Thermal Comfort Voting & 24-Hour Data Review
![Voting and Data Review](Image/v.png)
- Users can vote on their actual thermal sensation in the office
- View past 24-hour data for various indicators through real-time API interaction with MySQL database

#### Thermal Comfort Model
The current thermal comfort model is based on Professor Fanger's PMV model from 1962. Once sufficient data is collected, the model will be adapted to suit the current office environment, providing a more accurate reflection of thermal comfort conditions and optimizing the use of air conditioning and other appliances.

### Tag Customization
![Tag Change](Image/tag2.png)
- Users can choose and customize tags for data acquisition
- Interface updates dynamically based on selected tags

## Installation

[Add installation instructions here]

## Usage

[Add usage instructions here]

## Contributing

[Add contribution guidelines here]

## License

MIT License

Copyright (c) [2024] [CHEN YUTONG]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
