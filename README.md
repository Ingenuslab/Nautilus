
# Omni-Navigator MCP

Este proyecto implementa un servidor de navegación web controlado por API, diseñado para ser utilizado desde un cliente en Termux.

## Configuración del Servidor (en un PC/Servidor externo)

1.  **Clonar el repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd omni-navigator
    ```

2.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Instalar navegadores de Playwright:**
    ```bash
    playwright install
    ```

4.  **Ejecutar el servidor:**
    ```bash
    python app.py
    ```

## Uso desde Termux (Cliente)

Para conectarse al servidor desde Termux, puede usar un script de Python como el siguiente:

```python
import requests

# Reemplace con la IP de su servidor
SERVER_IP = '192.168.1.100' 
PORT = 5000
TARGET_URL = 'https://www.google.com'

try:
    response = requests.get(f'http://{SERVER_IP}:{PORT}/scrape', params={'url': TARGET_URL})
    response.raise_for_status()  # Lanza una excepción para códigos de error HTTP
    data = response.json()
    print(data)
except requests.exceptions.RequestException as e:
    print(f"Error al contactar con el servidor de scraping: {e}")
```
