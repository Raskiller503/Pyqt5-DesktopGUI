# Desktop Application based on Pyqt5 library

This is a desktop application based on the PyQt5 library, designed for energy management and thermal comfort monitoring in office buildings.

## 1. Application overview

### 1.1 Main Window
![Main Window](Image/2.png)
The main window provides a comprehensive overview of the office environment, focusing on three key aspects:

1). **Thermal Condition**
   - Displays real-time temperature, humidity, and mean radiant temperature
   - Shows thermal comfort predictions based on the PMV model

2). **Health Condition**
   - Monitors and displays indicators related to occupant health
   - Includes metrics such as CO2 levels and air quality index

3). **Energy Condition**
   - Presents current energy consumption data
   - Displays energy-saving recommendations and predictions

Additional features:
- Machine learning prediction results for energy consumption
- User-friendly interface for changing tags and reporting energy-saving actions
- Interactive elements for detailed data exploration

### 1.2 Login Window
![Login Window 1](Image/00.png)
- User account sign-in functionality
- Option to change device location near user's seat

### 1.3 Thermal Comfort Voting & 24-Hour Data Review
![Voting and Data Review](Image/v.png)
- Users can vote on their actual thermal sensation in the office
- View past 24-hour data for various indicators through real-time API interaction with MySQL database

### 1.4 Thermal Comfort Model
The current thermal comfort model is based on Professor Fanger's PMV model from 1962. Once sufficient data is collected, the model will be adapted to suit the current office environment, providing a more accurate reflection of thermal comfort conditions and optimizing the use of air conditioning and other appliances.

### 1.5 Tag Customization
![Tag Change](Image/tag2.png)
- Users can choose and customize tags for data acquisition
- Interface updates dynamically based on selected tags

## 2. Installation

To set up and run this project, follow these steps:

1. Clone the repository:
```bash
   git clone https://github.com/Raskiller503/Pyqt5-DesktopGUI.git
cd Pyqt5-DesktopGUI
```
2. Ensure you have Python 3.7 or higher installed on your system.
3. Install the required dependencies:
pip install -r requirements.txt
This will install all necessary libraries including PyQt5.
4. Set up the MySQL database:
- Install MySQL if not already installed
- Create a new database for the project
- Update the database connection settings in the configuration file (if applicable)

5. Run the application:
python main.py

## 3. License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 4. Reference
For smart phone application (iOS system), please [download](https://apps.apple.com/jp/app/bi-tech/id6451035366). \
For more detailed information, please refer to the following paper:
- __Yutong CHEN__,
[Development of Low-Cost IoT Units for Thermal Comfort Measurement and AC Energy Consumption Prediction System](https://kth-my.sharepoint.com/personal/torunw_ug_kth_se/_layouts/15/onedrive.aspx?ga=1&id=%2Fpersonal%2Ftorunw%5Fug%5Fkth%5Fse%2FDocuments%2Fbox%5Ffiles%2FRoomVent%2FRoomVent%5F2024%5FProceedings%2F240425%201400a%20Session%2026%20IC%20Thermal%20comfort%201%2FPrint%20439%20Final%2Epdf&parent=%2Fpersonal%2Ftorunw%5Fug%5Fkth%5Fse%2FDocuments%2Fbox%5Ffiles%2FRoomVent%2FRoomVent%5F2024%5FProceedings%2F240425%201400a%20Session%2026%20IC%20Thermal%20comfort%201![image](https://github.com/user-attachments/assets/537ab711-703e-4c39-b811-ccc46ccde782)
), presented at RoomVent2024.
