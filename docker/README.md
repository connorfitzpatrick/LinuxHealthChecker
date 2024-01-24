- From the /docker directory, create the image:
  docker build -t linux-server .

- Create key:
  ssh-keygen -t rsa -m PEM -f id_rsa

- See Images:
  docker images

- See Containers:
  docker ps -a

- Stop and Remove Container:
  docker stop <container_id>
  docker rm <container_id>

- Run docker container:
  docker run -d --name server1 -it -p 58897:22 server1

- ssh to docker container:
  ssh remote_user@localhost -p 58897
