FROM python:3.12

COPY . /app/

WORKDIR /app

ENV TZ=Asia/Karachi
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip install poetry

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

COPY . .

EXPOSE 8001

CMD ["poetry", "run", "uvicorn", "fastapi_todo_app.main:app", "--reload", "--host", "0.0.0.0",  "--port", "8001"] 