FROM python:3.9
WORKDIR /app
COPY requirements.txt /app
RUN pip install pip --upgrade && pip install -r requirements.txt
CMD [ "python", "chatbot_pro.py" ]