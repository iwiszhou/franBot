## All in one : Redis + Redis-Commander + Chatbots + API-server + Nginx

This repository makes use of container technologies to put the above mentioned services into a single VM.
**Redis** is a NoSQL database and used to store and retrieve app's data
**Redis-Commander** is a web-based Redis GUI to view the data stored in **Redis** through browsers
**Chatbots** are our telegram-chatbot servers to handle those conversations with our users 
**Nginx** acts as a reverse-proxy server and a load balancer to equally assign requests to the **Chatbots** so that they handle those requests from **Telegram** 
**API-server** serve as a backend server providing resources for HTML pages


## Deployment steps

1. Generate a Self-Signed Certificate

	**openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx-selfsigned.key -out nginx-selfsigned.crt**

	> Please be reminded to fill the common name as your VM's IP. 
	Others can be filled as '.'; Otherwise, it will not work.

2. Copy nginx-selfsigned.key and nginx-selfsigned.crt to ~/nginx

3. Copy nginx-selfsigned.crt to ~/chatbot

4. Put your VM's IP in line 161 of index.html in nginx folder

5. Fill in your tokens in sample-env and rename it to .env

5. Run the following command in your VM to start services

	> docker-compose up -d

## Reference
**Polling vs. Webhook:** [Webhooks · python-telegram-bot/python-telegram-bot Wiki · GitHub](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#creating-a-self-signed-certificate-using-openssl)

**Example of echobot:** [echobot.py - python-telegram-bot v21.0.1](https://docs.python-telegram-bot.org/en/stable/examples.echobot.html)

**NGINX with Self-Signed Certificate:** [NGINX with Self-Signed Certificate on Docker | by Miladev95 | Medium](https://medium.com/@miladev95/nginx-with-self-signed-certificate-on-docker-a514bb1a4061)

**Load Balance in NGINX:** [GitHub - NeroCube/docker-nginx-load-balancing: Use Nginx with multiple Node.js web server to try load balancing in Docker](https://github.com/NeroCube/docker-nginx-load-balancing)

**CI/CD in GCP:** [CI/CD pipeline with Google Compute Engine and GitHub Actions, part I | Medium](https://medium.com/plumbersofdatascience/building-a-ci-cd-pipeline-for-apache-airflow-dags-part-i-6ac072cd732d)
