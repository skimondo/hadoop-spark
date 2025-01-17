#!/bin/bash

docker stop namenode resourcemanager datanode historyserver nodemanager && docker rm namenode resourcemanager datanode historyserver nodemanager 2>/dev/null

# Check if the repo already exists
if [ ! -d "hadoop/docker-hadoop" ]; then
    echo "Cloning the repository..."
    git clone https://github.com/arminZolfaghari/docker-hadoop.git hadoop/docker-hadoop
else
    echo "Repository already exists. Skipping clone."
fi

# Run docker-compose only if the directory exists
if [ -d "hadoop/docker-hadoop" ]; then
    echo "Starting Docker containers..."
    cd hadoop/docker-hadoop && docker-compose up -d && cd ../..
else
    echo "Error: hadoop/docker-hadoop directory not found!"
    exit 1
fi

# Wait for all containers to be healthy
echo "Waiting for containers to be healthy..."
for container in namenode resourcemanager datanode historyserver nodemanager; do
    while [ "$(docker inspect -f '{{.State.Health.Status}}' $container)" != "healthy" ]; do
        echo "Waiting for $container to be healthy..."
        sleep 5
    done
done
echo "All containers are healthy."

# Copy files to namenode container and execute Hadoop commands
docker cp ../projet namenode:/ 

docker exec namenode hadoop fs -rm -r 33100036-treated.csv 2>/dev/null
docker exec namenode hadoop fs -rm -r resultat 2>/dev/null
docker exec namenode rm projet/part-00000 2>/dev/null

docker exec namenode hadoop fs -put /projet/33100036-eng/33100036-treated.csv &&
docker exec namenode hadoop jar /opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar \
  -file /projet/hadoop/mapper.py -mapper "python3 mapper.py" \
  -file /projet/hadoop/reducer.py -reducer "python3 reducer.py" \
  -input "33100036-treated.csv" -output "resultat" &&
docker exec namenode hdfs dfs -get resultat/part-00000 projet/part-00000 &&
docker cp namenode:/projet/part-00000 hadoop/part-00000 &&
cat hadoop/part-00000

