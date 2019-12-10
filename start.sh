#!/bin/bash

FULL_PATH=$(realpath $0)
DIR_PATH=$(dirname $FULL_PATH)

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

function build_project() {
	# Build project using docker-compose 
	echo "${green}[*] Make all project environment${reset}"
	echo "${purple}[+] Clean project workspace${reset}"
	docker-compose down
	echo "${purple}[+] Build project${reset}"
	docker-compose build --no-cache
	echo "${purple}[+] Start project${reset}"
	docker-compose up -d
}

function registry() {
	# Add some docker images to local registry
	echo "${green}[*] Adding jupyter/datascience-notebook to local registry${reset}"
	echo "${purple}[+] Pulling jupyter/datascience-notebook${reset}"
	docker pull jupyter/datascience-notebook:latest
	echo "${purple}[+] Adding tag for jupyter/datascience-notebook on local registry${reset}"
	docker tag jupyter/datascience-notebook:latest 127.0.0.1:5000/datascience-notebook
	echo "${purple}[+] Pushing jupyter/datascience-notebook on local registry${reset}"
	docker push 127.0.0.1:5000/datascience-notebook
}

function main() {
	flush
	build_project
	registry
}

main
echo "${green}[*] Done!${reset}"
