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

## 2026-10-29
**Hecho:**
Terminé la fase 1. Agregué las constantes `DURACION_FFT`, `BANDA`, `RECORTE` y `RETRASO_MAXIMO`. Calculé el espectro de ruido (ASD) de H1 y L1 con segmentos de 4 s y lo grafiqué en log-log. Escribí `blanquear()`, que blanquea y filtra entre 35 y 350 Hz, y recorté de t0 - 0.2 s a t0 + 0.1 s. Con `retraso_entre()` medí por correlación cruzada cuánto tarda la señal de un detector al otro, y superpuse L1 desplazado e invertido sobre H1. Al final hice el Q-transform de los dos detectores con `graficar_q()`.

**Salió:**
El ruido es mínimo y casi plano (~1e-23 /√Hz) entre 100 y 1000 Hz. Abajo de ~30 Hz sube mucho (ruido sísmico), hay picos en 60 Hz y sus armónicos y otros en ~35, ~500 y ~1000 Hz. Cerca de 2000 Hz cae de golpe. Después de blanquear y filtrar, el ruido queda con amplitud ~0.4 y el chirp llega a ~3 justo en t0. L1 llega 7.3 ms antes que H1 con correlación -0.55: la señal es la misma pero invertida, y al desplazar e invertir L1 las dos curvas coinciden. En el Q-transform se ve la curva del chirp, que sube de ~35 Hz a ~250-300 Hz en unos 0.1 s y termina en t0 + 0.42 s (L1) y t0 + 0.43 s (H1).

**No entendí:**
Entendí todo 

**Siguiente:**
Fase 2: *matched filtering* de GW150914. PyCBC no va bien en Windows nativo, así que primero ver si funciona en WSL2 o si escribo el filtro a mano con numpy.

## 2026-10-30
**Hecho:**
Escuché los `.wav` de H1 y L1, se oye el chirp y con eso di por superada la fase 0. Empecé la fase 1 con el notebook `02-fft`: escribí `dft()`, que calcula la transformada por la definición, y `fft()`, el algoritmo de Cooley–Tukey, que parte la señal en muestras pares e impares hasta llegar a una sola. Las comparé con `numpy.fft` y medí cuánto tarda cada una. Después escondí un seno de 123 Hz y amplitud 0.1 en ruido de amplitud 1 y lo busqué en el espectro. Más tarde pasé la FFT a `src/senal.py` y escribí ahí `welch()`, `blanquear()` y `pasa_banda()`. En `03-welch` comparé la PSD con `scipy.signal.welch` y con gwpy, y en `04-blanqueado` blanqueé y filtré GW150914 y lo comparé con gwpy.

**Salió:**
`dft()` difiere de `numpy.fft` en ~1e-11 y `fft()` en ~5e-14, o sea, son iguales salvo por el redondeo. Con 2048 muestras, `dft()` tarda ~0.5 s y `fft()` ~0.05 s; cada vez que se duplican las muestras, la primera tarda 4 veces más y la segunda apenas el doble. `numpy.fft` es unas mil veces más rápida que las dos. En el tiempo, el seno no se ve dentro del ruido, pero en el espectro hay un pico justo en 123 Hz, 94 veces más alto que la mediana. Mi Welch coincide con scipy y gwpy en una parte en 10^10. Mi blanqueado coincide con el de gwpy en ~3e-11 en H1 y L1, así que la fase 1 está superada. Para lograrlo hizo falta copiar dos detalles de gwpy: el filtro blanqueador dura solo 2 s (truncado del espectro inverso) y `whiten()` estima la ASD sin solapamiento. Filtrado entre 35 y 350 Hz, mi resultado se parece al de gwpy con correlación 0.98; la diferencia es que gwpy usa un filtro elíptico que dentro de la banda oscila entre 0.63 y 1. Lo blanqueado no tiene desviación 1 sino 1.21 (H1) y 1.47 (L1): las líneas estrechas, como la de 1012 Hz en L1, se cuelan porque un filtro de 2 s no las puede recortar.

**No entendí:**

**Siguiente:**
Fase 2: generar un chirp newtoniano y estimar la masa chirp de GW150914 a partir del espectrograma.
