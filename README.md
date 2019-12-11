#  Tuxae-Jupyter-Manager

Build/Deploy jupyter environments for Tuxae members.

## Prerequisites

### Docker install

- Debian: [https://docs.docker.com/install/linux/docker-ce/debian/](https://docs.docker.com/install/linux/docker-ce/debian/)

### DNS configuration

```bash
server.domain.tld.         0           A                <IPv4 address A.B.C.D>
*.domain.tld.              0           CNAME            server.domain.tld.
domain.tld.                0           CAA              0 issuewild "letsencrypt.org."
```
See [https://letsencrypt.org/docs/caa/](https://letsencrypt.org/docs/caa/) for more details about CAA DNS entries.

## Install

- `cp docker-compose.yml{,.dist}`
- Update emails/passwords configuration
- `MAIL_USERNAME` has to be a gmail email
- Use [start.sh](./start.sh)


## Manual deployment

### Docker registry

The web application provide an access to docker images from the local registry

Example to add an image to the local registry:
```bash
docker pull jupyter/datascience-notebook:latest
docker tag jupyter/datascience-notebook:latest 127.0.0.1:5000/datascience-notebook
docker push 127.0.0.1:5000/datascience-notebook
```

You can check available images on [http://127.0.0.1:5000/v2/\_catalog](http://127.0.0.1:5000/v2/_catalog)

```bash
curl http://127.0.0.1:5000/v2/_catalog
{"repositories":["datascience-notebook"]}
```

### Reverse proxy

#### nginx-proxy 

Github repository: [https://github.com/jwilder/nginx-proxy](https://github.com/jwilder/nginx-proxy)

```
docker run --detach \
	--name nginx-proxy \
	--publish 80:80 \
	--publish 443:443 \
	--volume /etc/nginx/certs \
	--volume /etc/nginx/vhost.d \
	--volume /usr/share/nginx/html \
	--volume /var/run/docker.sock:/tmp/docker.sock:ro \
	jwilder/nginx-proxy
```

#### nginx-proxy-letsencrypt

Github repository: [https://github.com/JrCs/docker-letsencrypt-nginx-proxy-companion](https://github.com/JrCs/docker-letsencrypt-nginx-proxy-companion)

```
docker run --detach \
	--name nginx-proxy-letsencrypt \
	--volumes-from nginx-proxy \
	--volume /var/run/docker.sock:/var/run/docker.sock:ro \
	--env "DEFAULT_EMAIL=mail@domain.tld" \
	jrcs/letsencrypt-nginx-proxy-companion
```
(You can use `--env "DEBUG=true"` if needed)


### Web application 

```
docker build -t webapp app/
docker run --detach \
	--name webapp \
	--volume /var/run/docker.sock:/var/run/docker.sock:ro \
	--volume /opt/database:/app/database:rw \
	--env "VIRTUAL_PORT=80" \
      	--env "VIRTUAL_HOST=subdomain.domain.tld" \
      	--env "LETSENCRYPT_HOST=subdomain.domain.tld" \
      	--env "LETSENCRYPT_EMAIL=mail@domain.tld" \
      	--env "DEFAULT_ADMIN_EMAIL=mail@example.org" \
      	--env "DEFAULT_ADMIN_PASSWORD=password" \
      	--env "DOCKER_REGISTRY_URI=127.0.0.1:5000" \
      	--env "EXTERNAL_URI=https://subdomain.domain.tld" \
      	--env "MAIL_USERNAME=mail@gmail.com" \
      	--env "MAIL_PASSWORD=password" \
      	--env "SERVER_DOMAIN=domain.tld" \
	webapp
```

## Result 

- [project.pdf](./slides/project.pdf)
- [project.pptx](./slides/project.pptx)

## Annex

### Troubleshooting

`docker logs nginx-proxy-letsencrypt`:
```
2019-12-08 06:11:14,854:ERROR:simp_le:1396: CA marked some of the authorizations as invalid, which likely means it could not access http://example.com/.well-known/acme-challenge/X. Did you set correct path in -d example.com:path or --default_root? Are all your domains accessible from the internet? Please check your domains' DNS entries, your host's network/firewall setup and your webserver config. If a domain's DNS entry has both A and AAAA fields set up, some CAs such as Let's Encrypt will perform the challenge validation over IPv6. If your DNS provider does not answer correctly to CAA records request, Let's Encrypt won't issue a certificate for your domain (see https://letsencrypt.org/docs/caa/). Failing authorizations: https://acme-v02.api.letsencrypt.org/acme/authz-v3/1612130256
```

Use `--env "DEBUG=true"` while running `jrcs/letsencrypt-nginx-proxy-companion` \
This link might help: [https://github.com/JrCs/docker-letsencrypt-nginx-proxy-companion/blob/master/docs/Invalid-authorizations.md](https://github.com/JrCs/docker-letsencrypt-nginx-proxy-companion/blob/master/docs/Invalid-authorizations.md)

### Additionnal information

- [https://tevinjeffrey.me/how-to-setup-nginx-proxy-and-lets-encrypt-with-docker/](https://tevinjeffrey.me/how-to-setup-nginx-proxy-and-lets-encrypt-with-docker/)
- [http://jasonwilder.com/blog/2014/03/25/automated-nginx-reverse-proxy-for-docker/](http://jasonwilder.com/blog/2014/03/25/automated-nginx-reverse-proxy-for-docker/)
- [https://gist.github.com/tevjef/da02244a881651416842387380293dcd](https://gist.github.com/tevjef/da02244a881651416842387380293dcd)
