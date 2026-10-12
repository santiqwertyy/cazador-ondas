## 2026-09-29
**Hecho:**
Terminé la estructura básica del proyecto: el README con el objetivo y los pasos para montar el entorno, el `environment.yml` de conda (Python 3.12, gwpy, gwosc, numpy, scipy, matplotlib y jupyterlab), las carpetas `datos/`, `notebooks/` y `src/`, la licencia MIT y este diario.

**Salió:**
Todavía nada con salida: solo archivos y carpetas, nada que ejecutar.

**No entendí:**
Fue muy básico hoy, así que entendí todo.

**Siguiente:**
Estudiar GW150914 y descargar 32 segundos de sus datos desde GWOSC.

## 2026-10-12
**Hecho:**
Calculé la ventana de 32 s (fin - inicio) y volví a revisar t0. Descargué los datos de H1 y L1 de GWOSC con `fetch_open_data` y le puse `cache=True` para no bajarlos de nuevo cada vez. Imprimí los dos objetos para ver qué traían e intenté graficarlos.

**Salió:**
La ventana dio 32.0 y t0 es 1126259462.4. Los dos TimeSeries se descargaron: empiezan en 1126259446.3999 s (t0 - 16) y tienen dt = 0.000244140625 s, o sea 4096 muestras por segundo. Los valores son del orden de 1e-19 a 1e-21 y sin unidades. El kernel se cayó justo después de imprimir los datos, así que no salió ningún gráfico.

**No entendí:**
Por qué se cayó el kernel.

**Siguiente:**
Arreglar el kernel y graficar los 32 segundos de H1 y L1.
