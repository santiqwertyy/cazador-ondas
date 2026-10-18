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

## 2026-10-16
**Hecho:**
Encontré por qué se caía el kernel: numpy con MKL cargaba un `libiomp5md.dll` viejo de anaconda base, y hasta multiplicar dos matrices pequeñas tumbaba Python. Cambié el entorno a OpenBLAS (`libblas=*=*openblas`), instalé scipy desde conda-forge, añadí `nbstripout` y registré el kernel "Python (cazador)". En el notebook quité el parche del `PATH`, definí `EVENTO` y `MEDIA_VENTANA` y escribí la función `cargar()`, que descarga de GWOSC solo la primera vez y después lee la copia de `datos/`. También ordené el repo: `.gitkeep` en `datos/` y `src/`, `.gitignore` ampliado, `.gitattributes` para `nbstripout` y el README con las fases y el estado.

**Salió:**
Ya no se cae el kernel y los 32 s de H1 y L1 se descargan una sola vez: en `datos/` quedaron `H1_GW150914_32s.hdf5` y `L1_GW150914_32s.hdf5` (cerca de 1 MB cada uno).

**No entendí:**
La caída del kernel (`0xc06d007f`), porque no estaba en mi código: Python moría hasta con `plot([1, 2, 3])`, y el parche del `PATH` solo funcionaba si esa celda corría primero. Al final resultó que numpy con MKL cargaba un `libiomp5md.dll` viejo de anaconda base, que está en el PATH de usuario. Lo que sigo sin entender bien es por qué Windows elige esa DLL de base y no la del entorno `cazador`.

**Siguiente:**
Calcular el espectro de ruido con `datos_h1.asd(fftlength=4)`, después blanquear y filtrar la señal para ver el chirp.

## 2026-10-17
**Hecho:**
Revisé el proyecto entero: seguridad, GitHub, entorno y funcionamiento. Descubrí que el commit `e982184` había devuelto el notebook a la versión del 12/10 (otra vez con el parche del `PATH` y `cache=True`, sin `cargar()`), así que lo restauré desde `072f0ce`. Quité del entorno `mkl` y tres paquetes que solo él usaba (`tbb`, `libhwloc` y `libwinpthread`): 565 MB que habían quedado de la primera instalación aunque numpy ya usaba OpenBLAS. En el notebook añadí `gps_evento()`, que pide el tiempo del evento a GWOSC solo la primera vez y lo guarda en `datos/`, y moví `DATOS` junto a las demás constantes.

**Salió:**
El notebook corre entero sin errores, también sin internet (lo probé cortando la red con un proxy falso). En `datos/` apareció `GW150914_gps.txt` con 1126259462.4, el mismo valor que da GWOSC. numpy, scipy y gwpy siguen funcionando sin MKL. El historial del repo está limpio: no hay contraseñas, tokens ni rutas de mi PC, y nbstripout sí quita las salidas.

**No entendí:**
Cómo acabó la versión vieja del notebook guardada encima de la buena. Lo más probable es que VS Code la tuviera abierta y la guardara antes del commit, pero no lo sé seguro.

**Siguiente:**
Revisar el diff y hacer commit de lo de hoy. Después, calcular el espectro de ruido con `datos_h1.asd(fftlength=4)` y blanquear y filtrar la señal para ver el chirp.
