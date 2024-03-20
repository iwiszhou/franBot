FROM python
WORKDIR /franBot
COPY . /franBot
RUN pip install update
RUN pip install -r requirements.txt

CMD python chatbot.py