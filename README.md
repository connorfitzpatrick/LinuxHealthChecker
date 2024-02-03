Run backend by cding into myBackend and running:

- `python manage.py runserver`

Run frontend by cding into frontend and running:

- `npm start`

Zookeeper:

- `cd downloads/kafka_2.13-3.6.1`
- `bin/zookeeper-server-start.sh config/zookeeper.properties`

Kafka:

- `cd downloads/kafka_2.13-3.6.1`
- `bin/kafka-server-start.sh config/server.properties`

Set up Docker containers by cding into docker and running:

- `docker run -p 58897:22 server1`
