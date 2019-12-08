#  Tuxae-Jupyter-Manager

Build/Deploy jupyter environments for Tuxae members

## Prerequisites
Install docker ([link](https://docs.docker.com/install/linux/docker-ce/debian/))

## Install

Use [start.sh](./start.sh)

## Docker registry

The web application provide an access to docker images from the local registry

Example to add image to the local registry:
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

## DNS configuration

```bash
server.domain.tld.         0           A                157.159.191.54    
*.domain.tld.              0           CNAME            server.domain.tld.
domain.tld.                0           CAA              0 issuewild "letsencrypt.org."
```

## Reverse proxy

Useful ressources:
- [https://github.com/jwilder/nginx-proxy](https://github.com/jwilder/nginx-proxy)
- [https://github.com/JrCs/docker-letsencrypt-nginx-proxy-companion](https://github.com/JrCs/docker-letsencrypt-nginx-proxy-companion)
- [https://letsencrypt.org/docs/caa/](https://letsencrypt.org/docs/caa/)


### Troubleshooting

```
2019-12-08 06:11:14,854:ERROR:simp_le:1396: CA marked some of the authorizations as invalid, which likely means it could not access http://example.com/.well-known/acme-challenge/X. Did you set correct path in -d example.com:path or --default_root? Are all your domains accessible from the internet? Please check your domains' DNS entries, your host's network/firewall setup and your webserver config. If a domain's DNS entry has both A and AAAA fields set up, some CAs such as Let's Encrypt will perform the challenge validation over IPv6. If your DNS provider does not answer correctly to CAA records request, Let's Encrypt won't issue a certificate for your domain (see https://letsencrypt.org/docs/caa/). Failing authorizations: https://acme-v02.api.letsencrypt.org/acme/authz-v3/1612130256
```

Use `--env "DEBUG=true"` while running `jrcs/letsencrypt-nginx-proxy-companion` \
This link might help: [https://github.com/JrCs/docker-letsencrypt-nginx-proxy-companion/blob/master/docs/Invalid-authorizations.md](https://github.com/JrCs/docker-letsencrypt-nginx-proxy-companion/blob/master/docs/Invalid-authorizations.md)

### Additionnal information

- [https://tevinjeffrey.me/how-to-setup-nginx-proxy-and-lets-encrypt-with-docker/](https://tevinjeffrey.me/how-to-setup-nginx-proxy-and-lets-encrypt-with-docker/)
- [http://jasonwilder.com/blog/2014/03/25/automated-nginx-reverse-proxy-for-docker/](http://jasonwilder.com/blog/2014/03/25/automated-nginx-reverse-proxy-for-docker/)
- [https://gist.github.com/tevjef/da02244a881651416842387380293dcd](https://gist.github.com/tevjef/da02244a881651416842387380293dcd)


## Web application 

### Features / Todo

- Manage whitelist domains for email registration
- Mount  /var/run/docker.sock inside webapp container
