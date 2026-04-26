# C++ Game Server (JSON-only workflow)

Build and run from `arcade_project/cpp_server/`.

## Compile

```bash
make SERIALIZER=JSON
```

This creates `server_json`.

## Run locally

```bash
./server_json --port 8080
```

## Run on ECE

```bash
ssh your_username@ece-000.eng.temple.edu
cd path/to/Comp2Final/arcade_project/cpp_server
make SERIALIZER=JSON
./server_json --port 80XX
```

## SSH tunnel from laptop

```bash
ssh -L 8006:localhost:80XX your_username@ece-000.eng.temple.edu -N
```

Then run local clients against `localhost --port 8006` with `--serializer json`.
