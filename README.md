# jobsity-challenge

## Overview
The project consists of an FastAPI app that executes the ingestion, transformation and queries required. Data is stored and modelled in `PostGIS`, a spatial database extender for `PostgreSQL`. 

The data pipeline was coded using Python and it executes the data processing SQL using SQLAlchemy. In order to minimize duplicated code and hardcode the queries in the scripts, the pipeline uses a yaml configuration file `pipeline_params.yaml` which allows to change the logic and add new queries in a fast way.   
The first step of the pipeline is the ingestion which consists of a Python code, which triggers a copy command in Postgres and loads the data in the `raw` schema.  
The next step is the transformation using the raw data to build a data model that supports all the queries. The data model is stored in the `dwh` schema.  
Finally, the data can be consumed using the API.  

Some tables contain some indexes (Spatial a B-trees) in specific columns to optimize the queries and to allow the scalability with 100 million of rows.  
This scenario was tested using a fake data generator to generate the data, then once the data was loaded into the database, the queries were executed successfully in a short time, taking into consideration the data volume involved. 

## Requirements
1) Docker is required for running the project. The versions used to create this project: 
```
docker: version 20.10.7,
docker-compose: version 1.28.2
```

2) If you want to receive the notifications pushed by the pipeline, you will need to join to the slack channel provided through the email sent.


## Installation
1) Clone the repository  
`git clone https://github.com/EzuA/jobsity-challenge.git`

2) Add the slack webhook url to the `.env` file in the repository root directory using the url provided. This variable is optional and is used to push the notifications in slack.

2) The complete solution is containerized and it can be run executing (in root directory):  
`docker-compose up`

    Then, open in a web browser:

    `http://localhost:8001/`

    You will see the welcome message:
    
    `{"message":"Welcome to jobsity challenge API"}`

3) Accessing interactive API documentation:

    `http://localhost:8001/docs#/`

## How to run it
In the API docs you can see the available methods of the API in two categories:  
    **Data pipeline process**:  
        - *init_db*: Drops and recreates the tables in the database.     
        - *ingest*: Run ingestion in raw table using the csv files indicated in the parameter `landing_file` set in the config file `pipeline_params.yaml`.  
        - *transform*: Run the transformation for the data model.  
        - *run_all*: Run the complete data pipeline.  <br />
    **Execute querys**  
        - *weekly_average_region*: Gets the weekly average number of trips for a specific region.    
        - *weekly_average_bounding_box*: Gets the weekly average number of trips defined by a bounding box.  

### Example run:
You can run every process using the "Try it out" button of every method.  
The first method you need to run is **run_all** (because the database is empty by default):

![Ingest](img/api_ingest.png?raw=true "Ingest")

You can change the body parameters if it is necessary, but for now you can run with the default values:   
    - `full_load`: Cleans the table and then executes the data load.  
    - `init_db`: Drops and recreates all tables in the database.

Finally, click on the execute button:

![Ingest](img/api_ingest_execution.png?raw=true "Ingest")


The same applies to queries:  

![Query](img/api_query_execution.png?raw=true "Query")

## Scalability test
The test was executed in a machine with an I5 10th generation and 20GB RAM with limited disk space.  
The performance can be improved using a more powerful machine, postgres RDS instances o Redshift cluster.  


![Query](img/avg_by_region.png?raw=true "Query")
<br /><br />

![Query](img/avg_by_box.png?raw=true "Query")

## AWS Cloud set up

![Query](img/aws_arch.png?raw=true "Query")
