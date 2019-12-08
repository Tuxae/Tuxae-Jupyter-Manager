#!/bin/bash

FULL_PATH=$(realpath $0)
DIR_PATH=$(dirname $FULL_PATH)
DEFAULT_EMAIL="aurelien@duboc.xyz"
DOMAIN="jupyter.t35h.re"

red=`tput setaf 1`
green=`tput setaf 2`
orange=`tput setaf 3`
purple=`tput setaf 5`
reset=`tput sgr0`

function flush() {
	# Flush all docker components
	echo "${red}[!] Flushing all docker components${reset}"
	echo "${orange}[+] Flushing docker containers${reset}"
	docker rm --force $(docker ps -a -q)
	echo "${orange}[+] Flushing docker images${reset}"
	docker rmi $(docker images -q) --force
	echo "${orange}[+] Flushing docker volumes${reset}"
	docker volume rm --force $(docker volume ls -q)  
}

function registry() {
	# Add docker registry listening on localhost
	echo "${green}[*] Adding local docker registry${reset}"
	docker run --detach -p 127.0.0.1:5000:5000 --restart=always --name registry registry:2
	# Add some docker images to local registry
	echo "${green}[*] Adding jupyter/datascience-notebook to local registry${reset}"
	echo "${purple}[+] Pulling jupyter/datascience-notebook${reset}"
	docker pull jupyter/datascience-notebook:latest
	echo "${purple}[+] Adding tag for jupyter/datascience-notebook on local registry${reset}"
	docker tag jupyter/datascience-notebook:latest 127.0.0.1:5000/datascience-notebook
	echo "${purple}[+] Pushing jupyter/datascience-notebook on local registry${reset}"
	docker push 127.0.0.1:5000/datascience-notebook
}

function reverse_proxy() {
	echo "${green}[*] Manage reverse proxy with letsencrypt SSL certificates${reset}"
	echo "${purple}[+] Starting jwilder/nginx-proxy${reset}"
	docker run --detach \
		--name nginx-proxy \
		--publish 80:80 \
		--publish 443:443 \
		--volume /etc/nginx/certs \
		--volume /etc/nginx/vhost.d \
		--volume /usr/share/nginx/html \
		--volume /var/run/docker.sock:/tmp/docker.sock:ro \
		jwilder/nginx-proxy
	echo "${purple}[+] Starting jwilder/nginx-proxy-letsencrypt${reset}"
	# if necessary use: --env "DEBUG=true" \
	docker run --detach \
		--name nginx-proxy-letsencrypt \
		--volumes-from nginx-proxy \
		--volume /var/run/docker.sock:/var/run/docker.sock:ro \
		--env "$DEFAULT_EMAIL" \
		jrcs/letsencrypt-nginx-proxy-companion
	echo "${purple}[+] Starting grafana with nginx-proxy configuration${reset}"
	docker run --detach \
		--name grafana \
		--env "VIRTUAL_HOST=grafana.$DOMAIN" \
		--env "VIRTUAL_PORT=3000" \
		--env "LETSENCRYPT_HOST=grafana.$DOMAIN" \
		--env "LETSENCRYPT_EMAIL=$DEFAULT_EMAIL" \
			grafana/grafana
}
