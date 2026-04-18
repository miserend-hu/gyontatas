# Gyóntatás

IoT eszközök állapotának nyomon követése és kezelése helyszínenként, a [miserend.hu](https://miserend.hu) rendszerrel integrálva.

Az eszközök CoAP protokollon keresztül küldik az állapotfrissítéseket (gyónások száma, bemenet állapotok, akkumulátor, jelszint). Az adatok MariaDB-ben tárolódnak, és Django Admin felületen kezelhetők.

## Architektúra

```
[IoT eszköz]
    │ CoAP POST /update/type1
    ▼
[coap – Node.js bridge]
    │ HTTP POST /api/coap/type1/
    ▼
[managementtool – Django]
    ├── MariaDB (Device, Location, SIMCard, DeviceUpdate)
    └── miserend.hu API
```

**Szolgáltatások:**

| Szolgáltatás     | Leírás                                                  |
|------------------|---------------------------------------------------------|
| `coap`           | Node.js CoAP–HTTP bridge, UDP/5683                      |
| `managementtool` | Django app – Admin felület + REST API, HTTP/8000         |
| `mariadb`        | MariaDB adatbázis                                        |

**Modellek:** `Location` · `Device` · `SIMCard` · `DeviceUpdate`

**REST API endpointok:**
- `GET /api/locations/{id}/updates/`
- `GET /api/devices/{id}/updates/`
- `GET /api/devices/{id}/updates/latest/`

---

# Lokális telepítés

### Követelmények

- Docker + Docker Compose
- `make`

### Indítás

```bash
make dev    # első indítás vagy kódváltozás után
make start  # gyors újraindítás
```

### Adatbázis feltöltése

```bash
make seed
```

A `seed.yml` fájlban konfigurálható a kezdeti adat (felhasználók, helyszínek, SIM kártyák, eszközök).

### Admin felület

```
http://localhost:8000
```

Alapértelmezett bejelentkezés a seed után: `root` / `root`

### Makefile parancsok

| Parancs       | Leírás                                                              |
|---------------|---------------------------------------------------------------------|
| `make start`  | Elindítja a konténereket (`docker compose up`)                      |
| `make dev`    | Újrabuildelve indítja el a konténereket (`docker compose up --build`) |
| `make seed`   | Feltölti az adatbázist a `seed.yml` alapján                         |
| `make purge`  | Törli az összes konténert és adatot (`docker compose down -v`)      |
| `make lint`   | Futtatja a `ruff` lintert és formátum-ellenőrzést                   |
