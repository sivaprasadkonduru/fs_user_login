FROM python:3.8.8
WORKDIR /fs_user_login
RUN pip install -r requirements.txt
EXPOSE 8080
WORKDIR /user_login_app
CMD ["python", "./api.py"]