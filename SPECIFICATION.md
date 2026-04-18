# Rendszerspecifikáció

## Áttekintés

A rendszer egy Django-alapú alkalmazásból (`managementtool`), egy CoAP szerverből, egy MongoDB és egy MariaDB adatbázisból áll, amelyek Docker Compose segítségével futnak együtt. A fő cél IoT eszközök (Device-ok) állapotának nyomon követése és kezelése, helyszíni bontásban, valamint a miserend.hu-val való integráció.

---

## Fejlesztői eszközök

### Csomagkezelő: `uv`

Az alkalmazás (`managementtool`) `uv`-t használ Python csomagkezelőként. A függőségek `pyproject.toml`-ban vannak definiálva, a lock fájl `uv.lock`.

### Linter: `ruff`

A kód minőségét `ruff` biztosítja (linting + formázás). Konfigurációja szintén a `pyproject.toml`-ban van.

### Makefile

A projekt gyökerében egy `Makefile` található az alábbi célokkal:

| Cél          | Leírás                                                                    |
|--------------|---------------------------------------------------------------------------|
| `make start` | Elindítja az összes szolgáltatást Docker Compose-zal (`docker compose up`)|
| `make dev`   | Fejlesztői módban indít (`docker compose up --build`, hot-reload-dal)    |
| `make lint`  | Futtatja a `ruff`-ot az alkalmazáson                                     |

---

## Infrastruktúra (`docker-compose.yml`)

### Szolgáltatások

| Szolgáltatás    | Leírás                                                           |
|-----------------|------------------------------------------------------------------|
| `coap`          | CoAP szerver – UDP protokollon fogad üzeneteket                  |
| `mariadb`       | MariaDB – minden adat tárolása (ORM modellek + update-ek)        |
| `managementtool`| Django app – Admin felület, CoAP feldolgozás, REST API           |

### Hálózat

Minden szolgáltatás egyazon Docker hálózaton kommunikál egymással. A CoAP szerver UDP/5683-as porton érhető el.

---

## `apps/managementtool`

### Technológia

- Python / Django
- Adatbázis: MariaDB (minden adat)
- CoAP kommunikáció: `aiocoap` vagy hasonló könyvtár
- Felület: Django Admin

### Felelősségek

1. **Django Admin**: `Location`, `Device`, `SIMCard` modellek kezelése, update adatok megjelenítése.
2. **CoAP listener**: UDP/5683-as porton várja az eszközöktől érkező állapotfrissítéseket.
3. **Update tárolás**: A beérkező update-eket MongoDB-ben tárolja.
4. **MiserendRepository**: HTTP-n keresztül lekérdezi a `miserend.hu` API-ját.
5. **REST API**: HTTP endpointokat biztosít az update adatok lekérdezéséhez.

---

### Adatmodellek

#### `Location`

Egy helyszínt reprezentál, amelyhez több Device tartozhat.

| Mező          | Típus     | Leírás                                          |
|---------------|-----------|-------------------------------------------------|
| `id`          | AutoField | Elsődleges kulcs                                |
| `name`        | CharField | Helyszín neve                                   |
| `miserend_id` | IntegerField | Helyszín azonosítója a miserend.hu rendszerben |

#### `SIMCard`

Egy SIM-kártyát reprezentál, amely pontosan egy Device-hoz tartozik. Az adatok az 1NCE szolgáltatóhoz kötődnek.

| Mező               | Típus      | Leírás                                            |
|--------------------|------------|---------------------------------------------------|
| `id`               | AutoField  | Elsődleges kulcs                                  |
| `iccid`            | CharField  | 1NCE elsődleges kulcs (ICCID)                     |
| `imsi`             | CharField  | SIM azonosítója – a Type1 payload-ban is szerepel |
| `end_date`         | DateField  | Adatcsomag lejárati dátuma                        |
| `remaining_volume` | FloatField | Fennmaradó adatmennyiség MB-ban (összesen 500 MB) |

#### `Device`

Egy IoT eszközt reprezentál.

| Mező            | Típus         | Leírás                                 |
|-----------------|---------------|----------------------------------------|
| `id`            | AutoField     | Elsődleges kulcs                       |
| `name`          | CharField     | Eszköz neve                            |
| `serial_number` | CharField     | Gyári sorozatszám                      |
| `location`      | ForeignKey    | Kapcsolat a `Location` modellhez (N:1) |
| `sim_card`      | OneToOneField | Kapcsolat a `SIMCard` modellhez (1:1)  |

#### Kapcsolatok

```
Location (1) ──< Device (N)
Device   (1) ──  SIMCard (1)
```

---

#### `DeviceUpdate`

Egy eszköz állapotfrissítését rögzíti egy adott időpontban. A `device_type` mező határozza meg, hogy mely típusspecifikus mezők értelmezettek; a többi mező `NULL`.

##### Közös mezők

| Mező          | Típus         | Leírás                                       |
|---------------|---------------|----------------------------------------------|
| `id`          | AutoField     | Elsődleges kulcs                             |
| `device`      | ForeignKey    | Kapcsolat a `Device` modellhez               |
| `location`    | ForeignKey    | Kapcsolat a `Location` modellhez             |
| `timestamp`   | DateTimeField | Az update érkezésének időpontja              |
| `device_type` | CharField     | Az eszköz típusa: `"type1"` \| `"type2"`     |

##### Type1 mezők (`device_type = "type1"`)

| Mező              | Típus         | Leírás                                                          |
|-------------------|---------------|-----------------------------------------------------------------|
| `imei`            | CharField     | Eszköz IMEI azonosítója                                         |
| `imsi`            | CharField     | SIM azonosítója                                                 |
| `version_product` | IntegerField  | NB-IoT eszköztípus kódja (pl. `4` = SN50v3-NB)                 |
| `version_code`    | IntegerField  | Firmware verzió kódja (pl. `150` = 1.5.0)                      |
| `battery`         | IntegerField  | Akkumulátor feszültsége mV-ban                                  |
| `signal`          | IntegerField  | Jelerősség                                                      |
| `interrupt_1`     | IntegerField  | Megszakítás forrása: `1` = ez ébresztette az eszközt, `0` = nem |
| `interrupt_2`     | IntegerField  | Lásd `interrupt_1`                                              |
| `interrupt_3`     | IntegerField  | Lásd `interrupt_1`                                              |
| `input_1`         | IntegerField  | Bemenet szintje: `1` = gyónás folyamatban, `0` = nincs gyónás  |
| `input_2`         | IntegerField  | Lásd `input_1`                                                  |
| `input_3`         | IntegerField  | Lásd `input_1`                                                  |
| `confession`      | IntegerField  | Az eszköz által érzékelt aktív gyónások száma                   |

##### Type2 mezők (`device_type = "type2"`)

Later.

---

### Payload feldolgozás

Az eszközök eltérő formátumban küldhetnek adatot CoAP-on keresztül. Minden eszköztípushoz külön feldolgozó osztály tartozik, amelyek egy közös interfészt valósítanak meg. A `process()` metódus minden esetben egy egységes `DeviceUpdate` dict-et ad vissza.

```python
class PayloadProcessor:
    # Közös interfész minden eszköztípus feldolgozójához
    def process(self, raw_payload: bytes) -> dict: ...

class Type1PayloadProcessor(PayloadProcessor):
    def process(self, raw_payload: bytes) -> dict: ...

class Type2PayloadProcessor(PayloadProcessor):
    def process(self, raw_payload: bytes) -> dict: ...

class PayloadProcessorFactory:
    # A beérkező CoAP üzenet alapján (pl. device_type mező vagy URI) kiválasztja
    # a megfelelő feldolgozót
    def get_processor(self, device_type: str) -> PayloadProcessor: ...
    # device_type == "type1"  -->  Type1PayloadProcessor
    # device_type == "type2"  -->  Type2PayloadProcessor
```

#### Type1 payload mezői

A Type1 eszközök (NB-IoT, pl. SN50v3-NB) az alábbi nyers mezőket küldik:

| Mező              | Típus   | Leírás                                                          |
|-------------------|---------|-----------------------------------------------------------------|
| `IMEI`            | String  | Eszköz IMEI azonosítója                                         |
| `IMSI`            | String  | SIM azonosítója                                                 |
| `version_product` | Integer | NB-IoT eszköztípus kódja (pl. `4` = SN50v3-NB)                 |
| `version_code`    | Integer | Firmware verzió kódja (pl. `150` = 1.5.0)                      |
| `battery`         | Integer | Akkumulátor feszültsége mV-ban                                  |
| `signal`          | Integer | Jelerősség                                                      |
| `interrupt_1`     | Integer | Megszakítás forrása: `1` = ez ébresztette az eszközt, `0` = nem |
| `interrupt_2`     | Integer | Lásd `interrupt_1`                                              |
| `interrupt_3`     | Integer | Lásd `interrupt_1`                                              |
| `input_1`         | Integer | Bemenet szintje: `1` = gyónás folyamatban, `0` = nincs gyónás  |
| `input_2`         | Integer | Lásd `input_1`                                                  |
| `input_3`         | Integer | Lásd `input_1`                                                  |
| `time`            | Integer | UNIX timestamp                                                  |
| `confession`      | Integer | Az eszköz által érzékelt aktív gyónások száma                   |

A `Type1PayloadProcessor.process()` ezeket a mezőket mappolja az egységes `DeviceUpdate` struktúrára. Az `IMEI` alapján azonosítható a Device, az `IMSI` alapján a SIMCard.

---

### miserend.hu API integráció

**Végpont:** `POST https://miserend.hu/api/v4/lorawan`

Kísérleti API, amely LoRaWAN eszközök gyóntatási adatait fogadja. A `MiserendRepository` ezt a végpontot hívja. Azonos `deduplicationId`-val kétszer nem fogad adatot.

#### Kérés mezői

| Mező                          | Kötelező | Típus / Formátum                                          | Leírás                                                        |
|-------------------------------|----------|-----------------------------------------------------------|---------------------------------------------------------------|
| `deduplicationId`             | igen     | UUID: `^[a-f0-9]{8}-...-[a-f0-9]{12}$`                   | Minden küldéshez egyedi UUID; ismételt ID-t a szerver elutasít|
| `time`                        | igen     | `YYYY-MM-DDTHH:MM:SS.sss+00:00`                           | Az esemény időbélyege                                         |
| `deviceInfo`                  | igen     | object                                                    | Eszközinformációk                                             |
| `deviceInfo/devEui`           | igen     | 16 hex karakter: `^[a-f0-9]{16}$`                         | Az eszköz egyedi EUI azonosítója                              |
| `deviceInfo/tags/templom_id`  | igen     | integer                                                   | A misézőhely azonosítója – `Location.miserend_id`             |
| `deviceInfo/tags/local_id`    | igen     | integer                                                   | Helyi eszközazonosító az adott misézőhelyen belül             |
| `object/Mód`                  | igen     | enum: `1` (ajtó állapot) \| `2` (vízszivárgás érzékelés) | Az eszköz működési módja                                      |
| `object/Satus_Door`           | Mód 1    | enum: `1` (nyitva) \| `0` (zárva)                        | Ajtó állapota – Mód 1 esetén kötelező                         |
| `object/Status_Leak`          | Mód 2    | enum: `1` (szivárgás) \| `0` (nincs szivárgás)           | Vízszivárgás állapota – Mód 2 esetén kötelező                 |

#### Válasz

| Mező    | Leírás                                     |
|---------|--------------------------------------------|
| `error` | `0` = sikeres, `1` = hiba                  |
| `text`  | Hiba esetén a hiba szöveges leírása        |

#### `MiserendLorawanPayload` adatstruktúra

A `MiserendRepository` ezt a struktúrát várja bemenetként:

```python
@dataclass
class MiserendLorawanPayload:
    deduplication_id: str   # UUID, minden híváshoz egyedi
    time: str               # YYYY-MM-DDTHH:MM:SS.sss+00:00
    dev_eui: str            # 16 hex karakter
    templom_id: int         # Location.miserend_id
    local_id: int           # helyi eszközazonosító
    mode: int               # 1 = ajtó, 2 = vízszivárgás
    door_status: int | None # 0/1, mode=1 esetén kötelező
    leak_status: int | None # 0/1, mode=2 esetén kötelező
```

---

### Repository osztályok

```python
class LocationRepository:
    def get_all(self) -> QuerySet[Location]: ...
    def get_by_id(self, location_id: int) -> Location: ...

class DeviceRepository:
    def get_all(self) -> QuerySet[Device]: ...
    def get_by_id(self, device_id: int) -> Device: ...
    def get_by_location(self, location_id: int) -> QuerySet[Device]: ...

class SIMCardRepository:
    def get_by_id(self, sim_card_id: int) -> SIMCard: ...
    def get_by_device(self, device_id: int) -> SIMCard: ...

class DeviceUpdateRepository:
    def create(self, update: DeviceUpdate) -> None: ...
    def list_by_device(self, device_id: int) -> QuerySet[DeviceUpdate]: ...
    def list_by_location(self, location_id: int) -> QuerySet[DeviceUpdate]: ...
    def retrieve_latest_by_device(self, device_id: int) -> DeviceUpdate: ...

class MiserendRepository:
    # POST https://miserend.hu/api/v4/lorawan
    def report_confession(self, payload: MiserendLorawanPayload) -> None: ...
    # Hibás válasz (error: 1) esetén kivételt dob
```

---

### Service osztályok

```python
class LocationService:
    def __init__(self, location_repository: LocationRepository): ...
    def list_locations(self) -> list[Location]: ...

class DeviceService:
    def __init__(self, device_repository: DeviceRepository): ...
    def list_devices(self) -> list[Device]: ...

class DeviceUpdateService:
    def __init__(
        self,
        update_repository: DeviceUpdateRepository,
        processor_factory: PayloadProcessorFactory,
    ): ...
    def process_coap_update(self, device_type: str, raw_payload: bytes) -> None: ...
    # 1. processor_factory.get_processor(device_type) alapján kiválasztja a feldolgozót
    # 2. processor.process(raw_payload) --> egységes DeviceUpdate objektum
    # 3. update_repository.create(update) --> MariaDB
    def list_updates_by_device(self, device_id: int) -> QuerySet[DeviceUpdate]: ...
    def list_updates_by_location(self, location_id: int) -> QuerySet[DeviceUpdate]: ...
    def retrieve_latest_update_by_device(self, device_id: int) -> DeviceUpdate: ...

class MiserendService:
    def __init__(self, miserend_repository: MiserendRepository): ...
    def report_confession(self, device: Device, location: Location, mode: int, door_status: int | None, leak_status: int | None) -> None: ...
    # Összerakja a MiserendLorawanPayload-ot és átadja a repository-nak
```

---

### Django Admin

Mindhárom ORM modell regisztrálva van az admin felületen. A `Device` és `Location` admin nézetekben az update adatok is megjelennek (csak olvasható nézetben), a `DeviceUpdateService`-en keresztül.

---

### URL-ek és View osztályok

#### Admin és gyökér

| URL       | View                     | Viselkedés                         |
|-----------|--------------------------|------------------------------------|
| `/`       | `RootRedirectView`       | Átirányítás a `/admin/` útvonalra |
| `/admin/` | Django Admin (beépített) | Django Admin felület               |

```python
class RootRedirectView(RedirectView):
    # GET /  -->  302  /admin/
    permanent = False
    url = '/admin/'
```

#### REST API – update endpointok

| URL                                        | View                       | Metódus    |
|--------------------------------------------|----------------------------|------------|
| `/api/locations/{location_id}/updates/`    | `LocationUpdateListView`   | `list`     |
| `/api/devices/{device_id}/updates/`        | `DeviceUpdateListView`     | `list`     |
| `/api/devices/{device_id}/updates/latest/` | `DeviceUpdateLatestView`   | `retrieve` |

```python
class LocationUpdateListView(ListAPIView):
    # GET /api/locations/{location_id}/updates/
    # Visszaadja az adott helyszín összes eszközének update-jeit
    def list(self, request, location_id): ...

class DeviceUpdateListView(ListAPIView):
    # GET /api/devices/{device_id}/updates/
    # Visszaadja az adott eszköz összes update-jét
    def list(self, request, device_id): ...

class DeviceUpdateLatestView(RetrieveAPIView):
    # GET /api/devices/{device_id}/updates/latest/
    # Visszaadja az adott eszköz legutolsó update-jét
    def retrieve(self, request, device_id): ...
```

---

## Adatfolyam

```
[IoT eszköz]
     |
     | CoAP (UDP/5683)
     v
[coap szerver]
     |
     | belső üzenet
     v
[managementtool – CoAP listener]
     |-- DeviceUpdateService.process_coap_update()
     |     |-- PayloadProcessorFactory.get_processor()
     |     |-- PayloadProcessor.process()  -->  egységes DeviceUpdate dict
     |     `-- DeviceUpdateRepository.create()  -->  MariaDB
     `-- MiserendService  -->  MiserendRepository  -->  miserend.hu

[Django Admin / REST API kliens]
     |-- DeviceUpdateService.list_updates_by_location()
     |-- DeviceUpdateService.list_updates_by_device()
     `-- DeviceUpdateService.retrieve_latest_update_by_device()
```

---

## Fejlesztési megjegyzések

- A mezők `(later)` jelöléssel bírnak ahol még nem véglegesek; ezeket a specifikáció bővítésekor kell kitölteni.
- A `MiserendRepository` belső implementációja a miserend.hu API dokumentációja alapján kerül kidolgozásra.
- Minden adat MariaDB-ben van; a `DeviceUpdate` is Django ORM modell.
