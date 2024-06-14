# Features
1) Upload WhatsApp chat data CSV file
2) Select timestamp and attribute columns for visualization
3) Choose visualization type (Line chart, Scatter plot, Bar Chart)
4) Generate report in PDF fromat. 

# Requirements
1) Python
2) Streamlit
3) Pandas
4) Plotly
5) Arrow
6) FPDF

# Usage
1) Clone this repository to your local machine. 
2) Install the required packages using 'pip install -r requirements.txt'
3) Access Chronochat Visualizer visualization tool: https://chronochat-visualizer.streamlit.app/
4) Upload message.csv file that contain WhatsApp chat data (get from dataset folder)
5) All the data in the CSV file is display in the system.
6) Choose vizualization type (Line Chart, Scatter PLot, Bar Chart).
7) Select timestamp and attribute columns for visualization.
8) Result table shows the result of attributes selected.
9) Insert title and description for report purposes.   
10) Generate report in PDF format.

# Note
* The timestamp column in the CSV file should be in epoch format so that the time can be converted to datetime using arrow
* The attribute columns should be numeric.
* Rows with NaN values in the selected columns will be dropped.

