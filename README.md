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

[1NCE API]
    │ SIM kártyák szinkronizálása
    ▼
[scheduler]
    └── Napi feladatok (sim_card_refresh, device_update_purge)
```

**Szolgáltatások:**

| Szolgáltatás     | Leírás                                                        |
|------------------|---------------------------------------------------------------|
| `coap`           | Node.js CoAP–HTTP bridge, UDP/5683                            |
| `managementtool` | Django app – Admin felület + REST API, HTTP/8000              |
| `scheduler`      | Napi ütemező (SIM frissítés, régi rekordok törlése)           |
| `mariadb`        | MariaDB adatbázis                                             |

**Modellek:** `Location` · `Device` · `SIMCard` · `DeviceUpdate`

**REST API endpointok:**
- `GET /api/locations/{id}/updates/`
- `GET /api/devices/{id}/updates/`
- `GET /api/devices/{id}/updates/latest/`

---

## Lokális telepítés

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

### Eszköz konfiguráció

Az IoT eszközöket az alábbi CoAP paraméterekkel kell beállítani:

| Paraméter | Érték                                 |
|-----------|---------------------------------------|
| Protokoll | CoAP (UDP)                            |
| Szerver   | a szerver domain neve vagy IP-címe    |
| Port      | `5683`                                |
| Path      | `/update/type1` vagy `/update/type2`  |
| Metódus   | `POST`                                |

### 1NCE integráció

A SIM kártyák adatai (IMSI, lejárat, fennmaradó adatmennyiség) automatikusan szinkronizálódnak a 1NCE API-ból. A szükséges környezeti változókat az `env-example` alapján kell beállítani:

```bash
cp env-example .env
```

Majd töltsd ki a `.env` fájlban:

```
ONENECE_CLIENT_ID=...
ONENECE_CLIENT_SECRET=...
```

Az Admin felületen a SIM kártyák listájáról a **Refresh from 1NCE** gombbal manuálisan is elindítható a szinkronizáció, vagy kézzel:

```bash
make shell
python manage.py sim_card_refresh
```

### Ütemezett feladatok

A `scheduler` szolgáltatás minden éjfélkor automatikusan lefuttatja:

- `sim_card_refresh` – SIM kártyák adatainak frissítése 1NCE-ből
- `device_update_purge` – 1 évnél régebbi DeviceUpdate rekordok törlése

### Makefile parancsok

| Parancs               | Leírás                                                                            |
|-----------------------|-----------------------------------------------------------------------------------|
| `make start`          | Elindítja a konténereket                                                          |
| `make stop`           | Leállítja a konténereket                                                          |
| `make restart`        | Újraindítja a konténereket                                                        |
| `make dev`            | Újrabuildelve indítja el a konténereket                                           |
| `make migrate`        | Django migrációkat futtat a futó konténerben                                      |
| `make upgrade`        | Leáll, `git pull`, újrabuildelve háttérben indít, majd migrál                     |
| `make seed`           | Feltölti az adatbázist a `seed.yml` alapján                                       |
| `make purge`          | Törli az összes konténert és adatot (`docker compose down -v`)                    |
| `make lint`           | Futtatja a `ruff` lintert és formátum-ellenőrzést                                 |
| `make simulate`       | Szimulált eszközüzenetet küld Docker konténerből (`ARGS` paraméterrel)            |
| `make simulate_local` | Szimulált eszközüzenetet küld a hostról `localhost:5683`-ra (`ARGS` paraméterrel) |
