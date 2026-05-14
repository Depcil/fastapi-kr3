# Контрольная работа №3 — Технологии разработки серверных приложений

## Установка и запуск

```bash
pip install -r requirements.txt
cp .env.example .env

uvicorn main:app --reload
```

## Переменные окружения

```
MODE=DEV          # DEV или PROD
DOCS_USER=admin
DOCS_PASSWORD=admin
```

## curl

### 6.1 Basic Auth

```bash
curl -u admin:secret http://localhost:8000/login-basic/login   # 200
curl -u admin:wrong  http://localhost:8000/login-basic/login   # 401
```

### 6.2 Basic Auth + bcrypt

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"correctpass"}' \
  http://localhost:8000/basic/register

curl -u user1:correctpass http://localhost:8000/basic/login   # 200
curl -u user1:wrongpass   http://localhost:8000/basic/login   # 401
```

### 6.3 Документация

```bash
# DEV
curl -u admin:admin http://localhost:8000/docs   # 200
curl http://localhost:8000/docs                   # 401

# PROD (MODE=PROD в .env)
curl http://localhost:8000/docs                   # 404
```

### 6.4 JWT логин (заглушка)

```bash
curl -X POST "http://localhost:8000/login-jwt?username=john&password=pass"
curl -H "Authorization: Bearer <token>" http://localhost:8000/protected-64
```

### 6.5 JWT + регистрация + rate limit

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"qwerty123"}' \
  http://localhost:8000/register

curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"qwerty123"}' \
  http://localhost:8000/login

curl -H "Authorization: Bearer <token>" http://localhost:8000/protected_resource
```

### 7.1 RBAC

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin1","password":"pw","role":"admin"}' \
  http://localhost:8000/register-rbac

curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin1","password":"pw"}' \
  http://localhost:8000/login

# только admin:
curl -X DELETE -H "Authorization: Bearer <token>" http://localhost:8000/resource   # 200
# guest попытается удалить:
curl -X DELETE -H "Authorization: Bearer <guest_token>" http://localhost:8000/resource   # 403
```

### 8.1 SQLite регистрация

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"test_user","password":"12345"}' \
  http://localhost:8000/db/register
```

### 8.2 Todo CRUD

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"title":"Buy groceries","description":"Milk, eggs, bread"}' \
  http://localhost:8000/todos

curl http://localhost:8000/todos/1

curl -X PUT -H "Content-Type: application/json" \
  -d '{"title":"Updated","description":"X","completed":true}' \
  http://localhost:8000/todos/1

curl -X DELETE http://localhost:8000/todos/1
```
