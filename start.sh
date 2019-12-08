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

