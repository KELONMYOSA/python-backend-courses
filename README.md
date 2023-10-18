# Homework 3

> Business scenario:
>
> Our web application will represent a food delivery service from restaurant. 
> The user registers, after which he can choose dishes from the menu and place an order.

### Services

- *fastapi_gateway* - **API gateway**
- *go_auth* - **Authentication server**

---

## How to start

### 1. GO

- Install the dependencies for the `golang` service

```
cd go_auth && go mod tidy & cd ..
```

- Run the `golang` service

```
cd go_auth && set CGO_ENABLED=1 && go run go_auth -port 8081 & cd ..
```

### 3. FastApi

- Install the dependencies for the `fastapi` service

```
pip install -r fastapi_gateway/requirements.txt
```

- Run the `fastapi` service

```
python fastapi_gateway/main.py
```

---

## Gateway arguments

- Host - <code>127.0.0.1</code>
- Port - <code>80</code>
- Docs URL - <code>/docs</code>

---

## Re-generate gRPC code

### 1. Protobuf

- Install the `Protobuf` compiler

```
choco install protoc
```
or
```
sudo apt install protobuf-compiler
```

- Install the `gen-go` and `gen-go-grpc` plugins

```
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
```

- Install the `grpcio-tools` plugin

```
pip install grpcio-tools
```
### 2.1 Python

```
python3 -m grpc_tools.protoc -I protobufs --python_out=./fastapi_gateway/pb_auth/ --pyi_out=./fastapi_gateway/pb_auth/ --grpc_python_out=./fastapi_gateway/pb_auth/ protobufs/auth.proto
```

### 2.2 GO

```
protoc --go_out=. --go-grpc_out=. protobufs/auth.proto
```

---

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