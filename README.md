# Homework 1

## How to start

```
python main.py
```

## FastAPI arguments

- Host - <code>127.0.0.1</code>
- Port - <code>80</code>
- Docs URL - <code>/docs</code>

## Endpoints

### <code>**GET**</code> /users/{id}

> *Returns json user data by user_id from https://reqres.in*

**Request**

```
http://127.0.0.1/users/1
```

**Response body**

```
{
  "data": {
    "id": 1,
    "email": "george.bluth@reqres.in",
    "first_name": "George",
    "last_name": "Bluth",
    "avatar": "https://reqres.in/img/faces/1-image.jpg"
  },
  "support": {
    "url": "https://reqres.in/#support-heading",
    "text": "To keep ReqRes free, contributions towards server costs are appreciated!"
  }
}
```

### <code>**POST**</code> /users

> *Returns code 201 and user data if the user was created*

**Request body**

```
{
  "name": "John",
  "job": "Accountant"
}
```

**Response body**

```
{
  "name": "John",
  "job": "Accountant",
  "id": "686",
  "createdAt": "2023-09-23T15:38:47.222Z"
}
```

### <code>**GET**</code> /compliment

> *Returns a simple dictionary with the specified delay*

**Request**

```
http://127.0.0.1/compliment?delay=3
```

**Response body**

```
{
  "You're": "wonderful"
}
```