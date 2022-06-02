# NRL-OTTAR-AsyncServer

<h4>Requirements:</h4>
<li>Python 3.10</li>
<li>PostgresSQL 14.3</li>
<li>FastAPI</li>
<li>Docker</li>

<h3>Docker</h3>
$ docker-compose build <br>
$ docker-compose up -d <br>
```
[+] Running 3/3
 ⠿ Container ottar-asyncserver-db-1   Running                                                                                                                              0.0s
 ⠿ Container ottar-asyncserver-api-1  Started                                                                                                                              2.0s
 ⠿ Container pgadmin                  Running                                                                                                                              0.0s
```

<h3>Python3 env:</h3>
cd <proj_dir><br> 
python3 -m venv env<br> 
source env/bin/activate<br> 
pip3 install -r requirements.txt<br> 

<h4>deactivate:<h4/> 
source env/bin/activate
