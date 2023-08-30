# Metrolinx Transit Insights Tool :train2:

### Description 

This Python web app allows you to input official Metrolinx CSV data to recieve  various summaries and data visualizations such as usage, stops, and money spent in seconds! 

### Getting your official data

To get your Metrolinx CSV data:
- Go to the [Presto Card Transit Usage Report](https://www.prestocard.ca/en/my-products/transit-usage-report)
- Select the year and transit usage settings to your preference
- **Export CSV**

### Running the locally application with Docker

#### Prerequisties
- Ensure you have Docker Desktop installed and open
- Add your Bing Maps API key to the `env.temp` file
- Rename `env.temp` to `.env` 

Steps:
- In the root directory, run
    - `docker build -t transit-tool .`
    - `docker run transit-tool`
- The app should be deployed at `http://localhost:8501`

### Contact
For any questions or concerns, reach out at kevlau82@gmail.com

