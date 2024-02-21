FROM ubuntu:latest

RUN mkdir -p /var/run/sshd

# Install dropbear SSH server
RUN apt-get update && \
    apt-get install -y sysstat && \
    apt-get install -y openjdk-8-jdk && \
    apt-get install -y openssh-server sudo && \
    apt-get install -y net-tools

RUN useradd -rm -d /home/remote_user -s /bin/bash remote_user && \
    echo 'remote_user:password1234' | chpasswd && \
    usermod -aG sudo remote_user

RUN mkdir /home/remote_user/.ssh && \
    chmod 700 /home/remote_user/.ssh

COPY id_rsa.pub /home/remote_user/.ssh/authorized_keys

RUN chown remote_user:remote_user -R /home/remote_user/.ssh && \
    chmod 600 /home/remote_user/.ssh/authorized_keys

CMD [ "/usr/sbin/sshd", "-D" ]
