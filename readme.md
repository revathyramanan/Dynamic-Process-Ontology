##


### Installing Docker
* Downlaod the most recent version of docker as per your OS from here - https://docs.docker.com/desktop/release-notes/


### Steps to run
* Change the $USER and $UID in .env file. To find out the values `echo $USER` and `echo $UID` from the terminal
* Create two folders insider the project folder 
* * A folder to save the graph database (graph_data)
* * A folder where the original raw data files are stored (This doesn't exist for now. So create an empty folder named raw_files)
* Mention these paths in the docker-compose.yml file. Mention full path.
* * `<path to raw_folder>:/import`
* * `<path to graph_data>:/data`
* Download the plugin [apoc-5.16.0-extended.jar](https://drive.google.com/file/d/12iVJVKnC4H-dYCx_-vhaKJwk9zzpXWzy/view?usp=sharing) and put it into a folder named `plugins` mention full path in the docker-compose file. Better to put this somewhere outside the project folder. 
* * `<path to plugins>:/var/lib/neo4j/plugins`
* command to stand up the docker container `docker compose up --build`
* access the notebook and neo4j from ports `https://localhost:8888` and `https://localhost:7474` respectively
* Username and password for neo4j is in .env file
* Password for Jupyterlab is in .env file
* command to get the docker container down `docker compose down -v`

### ERRORS
* if `docker command not found` after the installation, add it to your path. For mac, ` export PATH="$PATH:/Applications/Docker.app/Contents/Resources/bin/" `
