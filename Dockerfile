FROM python:3.12
WORKDIR /whale-backend
COPY ./requirements.txt /whale-backend/
RUN pip install --no-cache-dir --upgrade -r /whale-backend/requirements.txt
COPY . /whale-backend/.
EXPOSE 8000
CMD ["fastapi", "run", "ready/main.py", "--proxy-headers", "--port", "8000"]