FROM alpine:latest

RUN apk update && apk add --no-cache \
    openssh \
    tcpdump \
    tshark \
    netcat-openbsd \
    && ssh-keygen -A \
    && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && echo "root:root" | chpasswd

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]