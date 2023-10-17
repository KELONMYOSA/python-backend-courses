# Homework 3

> Business scenario:
>
> Our web application will represent a food delivery service from restaurant. 
> The user registers, after which he can choose dishes from the menu and place an order.

## How to start

### FastApi
```
fastapi_gateway\venv\Scripts\activate
python fastapi_gateway\main.py
```

## FastAPI arguments

- Host - <code>127.0.0.1</code>
- Port - <code>80</code>
- Docs URL - <code>/docs</code>

## How to run tests

### All tests

```
python -m pytest fastapi_gateway
```

### Unit tests

```
python -m pytest fastapi_gateway/tests/unit
```

### Integration tests

```
python -m pytest fastapi_gateway/tests/integration
```