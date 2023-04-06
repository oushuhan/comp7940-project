FROM python:3.9
WORKDIR /app
COPY . /app
RUN pip install pip --upgrade && pip install -r requirements.txt
CMD [ "python", "/app/chatbot_pro.py" ]