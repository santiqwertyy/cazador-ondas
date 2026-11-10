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
Escuché los `.wav` de H1 y L1, se oye el chirp y con eso di por superada la fase 0. Empecé la fase 1 con el notebook `02-fft`: escribí `dft()`, que calcula la transformada por la definición, y `fft()`, el algoritmo de Cooley–Tukey, que parte la señal en muestras pares e impares hasta llegar a una sola. Las comparé con `numpy.fft` y medí cuánto tarda cada una. Después escondí un seno de 123 Hz y amplitud 0.1 en ruido de amplitud 1 y lo busqué en el espectro. Más tarde pasé la FFT a `src/senal.py` y escribí ahí `welch()`, `blanquear()` y `pasa_banda()`. En `03-welch` comparé la PSD con `scipy.signal.welch` y con gwpy, y en `04-blanqueado` blanqueé y filtré GW150914 y lo comparé con gwpy. Por la noche seguí con la fase 2 en `05-chirp`: escribí el generador de chirp newtoniano y estimé la masa chirp comparando el espectrograma de los datos con los de un banco de plantillas procesadas igual que los datos. Validé el método con 72 chirps inyectados en el ruido real de H1 y L1, y también sin ruido. Hice la FFT unas 35 veces más rápida calculando las dos mitades en una sola llamada. Después diagnostiqué por qué fallaba (`docs/fase2-diagnostico.md`) y, saliéndome del plan, escribí el *matched filtering* a mano en `src/filtro_adaptado.py` y el notebook `06-masa-chirp`, con plantillas IMRPhenomD generadas con ripple, que instalé en `cazador`. Analicé GW150914 con una cuadrícula de masa chirp, razón de masas y giro, y lo validé con inyecciones en el ruido real.

**Salió:**
`dft()` difiere de `numpy.fft` en ~1e-11 y `fft()` en ~5e-14, o sea, son iguales salvo por el redondeo. Con 2048 muestras, `dft()` tarda ~0.5 s y `fft()` ~0.05 s; cada vez que se duplican las muestras, la primera tarda 4 veces más y la segunda apenas el doble. `numpy.fft` es unas mil veces más rápida que las dos. En el tiempo, el seno no se ve dentro del ruido, pero en el espectro hay un pico justo en 123 Hz, 94 veces más alto que la mediana. Mi Welch coincide con scipy y gwpy en una parte en 10^10. Mi blanqueado coincide con el de gwpy en ~3e-11 en H1 y L1, así que la fase 1 está superada. Para lograrlo hizo falta copiar dos detalles de gwpy: el filtro blanqueador dura solo 2 s (truncado del espectro inverso) y `whiten()` estima la ASD sin solapamiento. Filtrado entre 35 y 350 Hz, mi resultado se parece al de gwpy con correlación 0.98; la diferencia es que gwpy usa un filtro elíptico que dentro de la banda oscila entre 0.63 y 1. Lo blanqueado no tiene desviación 1 sino 1.21 (H1) y 1.47 (L1): las líneas estrechas, como la de 1012 Hz en L1, se cuelan porque un filtro de 2 s no las puede recortar. La masa chirp de GW150914 sale 29.25 M☉ en H1 y 28.75 M☉ en L1, comparando hasta 250 Hz; el catálogo da 30.2 M☉. Sin ruido, el método recupera la masa exacta. Con ruido, tiene un sesgo de −2.9 % y una dispersión de ±5.6 %, así que solo 39 de las 72 inyecciones quedan a menos del 5 %. Con 150 Hz el método falla incluso sin ruido, porque cada fila del espectrograma mezcla ±32 Hz. El espectrograma fallaba por dos razones: la masa se intercambiaba con el instante de fusión (−3.4 % por milisegundo), y GW150914 no es newtoniano, así que según qué parte de la señal mirara la masa iba de 25 a 38 M☉. Con *matched filtering*, la masa chirp con H1 y L1 es 30.8 M☉ (90 %: 29.4 a 32.2), y el catálogo da 30.2. El giro sale −0.05 (LIGO: −0.06) y la señal llega a L1 7.1 ms antes que a H1. Cambiar el modelo, la PSD o el segmento la mueve 0.2 M☉ como mucho. En las inyecciones, H1+L1 tiene sesgo −0.2 % y dispersión 1.2 %, y las 30 quedan a menos del 5 %: fase 2 superada.

**No entendí:**
- Por qué la mediana de varios periodogramas sale sistemáticamente baja. Cada valor del periodograma de ruido gaussiano sigue una distribución exponencial (χ² con 2 grados de libertad), cuya mediana es ln 2 veces la media, y la corrección para k segmentos (k impar) es 1 − 1/2 + 1/3 − … + 1/k. No sé deducir esa serie ni por qué tiende a ln 2.
- El principio de incertidumbre tiempo–frecuencia en el blanqueado. Cortar la respuesta del filtro a 2 s equivale a suavizar 1/ASD con una resolución de ~0.5 Hz, y por eso la línea de 1012 Hz de L1 se cuela 837 veces por encima del ruido. Tampoco entiendo por qué, fuera de las líneas, el nivel blanqueado queda en 1.14 y no en 1.
- La degeneración entre masa chirp e instante de fusión. En el espectrograma, una plantilla 3.4 % más liviana que termina 1 ms después se ve casi igual. Con *matched filtering* desaparece porque la fase cuenta los ciclos uno por uno, pero no sé calcular eso (la matriz de Fisher y las elipses de error en el espacio de parámetros).
- Por qué el máximo de una función con ruido no está donde estaría sin ruido. Con el espectrograma, la masa 40 salía 4–5 % baja con ruido y exacta sin él; el ruido de cada píxel crece donde hay señal (por el término cruzado señal·ruido), pero no sé llevar eso a una fórmula del sesgo.
- La serie post-newtoniana. Cerca del choque los agujeros negros de GW150914 van a ~0.5 c, la serie en potencias de v/c converge mal y cada término cambia el ritmo del chirp (el término "de cola", 4π·x^(3/2), lo acelera). No entiendo de dónde sale ese término (viene de la onda que rebota en la curvatura del espacio-tiempo que crea la masa de la propia binaria).
- La correlación masa chirp–giro. Con giros alineados la fusión se retrasa (el efecto "hang-up") y la señal tiene más ciclos, así que un giro mayor se confunde con una masa mayor: ~12 % de masa por cada 0.25 de giro. No sé por qué el giro alarga la órbita.
- Por qué exp(SNR²/2) hace de verosimilitud. El producto interno ponderado por 1/S(f) es el producto escalar natural cuando el ruido es gaussiano y coloreado, y al maximizar en amplitud y fase queda SNR²/2 en el exponente. No sé si los intervalos que salen así son bayesianos o frecuentistas, aunque en las inyecciones cubren bien (29 de 30).

**Siguiente:**
Fase 3: validar el *matched filtering* contra PyCBC (en WSL2 o Colab), armar el banco de plantillas para búsqueda y buscar 5 eventos más de O1/O2.

## 2026-10-31
**Hecho:**
Seguí con la fase 3. Pasé el generador de formas de onda del notebook 06 a `src/plantillas.py` y agregué a `src/filtro_adaptado.py` dos funciones: `parecido()`, que mide cuánto se parecen dos formas de onda (el producto interno normalizado, maximizado en tiempo y fase), y `snr_red()`, que junta H1 y L1 buscando para cada instante de H1 el mayor SNR de L1 a menos de 10 ms. En el notebook `07-banco` armé el banco de plantillas a mano: por cada combinación de razón de masas y giro, recorro la masa chirp de 6 a 45 M☉ y pongo una plantilla nueva cada vez que el parecido con la anterior baja a 0.90. Para elegir qué combinaciones usar probé 9 y medí con 100 señales de otro modelo (IMRPhenomXAS) cuánto se parecía cada una a la mejor plantilla del banco. En el notebook `08-eventos-o1-o2` busqué con ese banco en 128 s de datos de H1 y L1 alrededor de GW150914 y de seis eventos más de O1 y O2, y metí 10 señales falsas en el ruido real para ver si las encontraba. Por la tarde revisé todo el código y todos los `.md` con `docs/prompt-revision.md`: comprobé la normalización del filtro con el ruido real, medí cuánto tardaría la fase 4, corregí detalles de los notebooks 07 y 08, fijé las versiones de `environment.yml`, decidí no instalar WSL2 (la PC no da para tanto) y preparé el notebook `09-validacion-pycbc` para comparar mi filtro con PyCBC en Google Colab. Al final hice el modo difícil de la fase 3: escribí a mano la forma de onda TaylorF2 (la espiral post-newtoniana, con la fase hasta 3.5PN) y en el notebook `10-taylorf2` la comparé con la de ripple, miré cuánto aporta cada orden y en qué masas deja de servir frente a IMRPhenomD. A la noche empecé la fase 4: escribí el test χ² de Allen, la compuerta para *glitches* fuertes, la lectura de los segmentos de calidad de GWOSC y la coincidencia con *time slides* para medir el fondo, y bajé 2.2 h de datos alrededor de GW150914 para probar la cadena entera.

**Salió:**
Sin giros negativos, el banco no llegaba: con 1060 plantillas solo 87 de 100 señales encontraban una plantilla con parecido de 0.95 o más, y las que fallaban tenían giro negativo o una masa mucho más chica que la otra. El banco final tiene 866 plantillas en 5 líneas, y con 200 señales nuevas 186 superan 0.95 (mediana 0.982). Los seis eventos nuevos aparecen en el lugar correcto, a menos de 0.05 s del tiempo del catálogo: GW151012 con SNR de red 9.8 (catálogo 9.3), GW151226 12.8 (12.7), GW170104 13.6 (13.8), GW170608 15.3 (15.3), GW170814 16.6 (17.7) y GW170823 12.0 (12.2). GW150914 da 24.6, con L1 7.3 ms antes que H1. La masa chirp de la mejor plantilla queda cerca de la del catálogo pasada al detector (por ejemplo, 9.7 frente a 9.8 en GW151226), y las 10 señales inyectadas se encontraron todas, con el SNR que tenían (mediana 1.00; repitiendo después de la revisión, con las mismas señales en otros instantes, 0.95, que con solo 10 está dentro del ruido). Con la PSD de 128 s, el SNR de GW150914 en H1 baja de 21.9 a 20.4. No es que la PSD de 32 s saliera baja: el filtro divide por la PSD estimada, y la inversa de una estimación con ruido sale más grande en promedio aunque la estimación no tenga sesgo (desigualdad de Jensen). Con 8 segmentos (32 s) el SNR² se infla ~26 %, con 32 (128 s) ~6 %. Eso explica también el 1.14 del blanqueado de la fase 1 que no entendía, y lo confirmé con el ruido real: el promedio de ρ² fuera del evento da 2.13–2.31, justo lo esperado con ese sesgo (sin sesgo sería 2), así que la normalización del filtro está bien. Al repetir los notebooks 07 y 08 después de la revisión, el banco salió idéntico y los 7 eventos dieron exactamente los mismos números. La FFT inversa propia es 9 veces más lenta que la de numpy: un mes de O3 tardaría ~100 días en esta PC. Mi TaylorF2 es igual a la de ripple (amplitud hasta 2e-15, fase hasta 3e-11 rad). Orden a orden, la serie no converge de a poco sino oscilando: con una binaria de estrellas de neutrones (Mc 1.2), el parecido con la versión completa es 0.14 a 1PN, 0.94 al sumar el término de cola (1.5PN), 0.41 a 2PN, 0.91 a 2.5PN y 0.97 a 3PN. Frente a IMRPhenomD, TaylorF2 da 0.999 con Mc 1.2, 0.977 con Mc 6, 0.947 con Mc 8.5 y solo 0.56 con Mc 30: para GW150914 la espiral sola no alcanza, porque la ISCO cae en 64 Hz y la señal más fuerte viene después. La masa chirp del catálogo para GW150914 es 27.9 M☉ en la fuente, unos 30.7 en el detector, y coincide con los 30.8 de la fase 2. En GW170814 apareció un *glitch*: 5.7 s antes del evento, L1 da SNR 13.9 y H1 casi nada. Boss 2 superado. En Google Colab (notebook `09-validacion-pycbc`), mi serie de SNR de GW150914 coincide con la de `pycbc.filter.matched_filter` hasta 7e-16 (el redondeo de la máquina) en H1 y L1, con el mismo pico (20.6303 y 14.1760) en el mismo instante y el mismo σ; las plantillas de ripple dan parecido 1.00000 con las de LALSuite (IMRPhenomD e IMRPhenomXAS, 5 puntos del banco), y mi TaylorF2 coincide con la de PyCBC en amplitud (3e-15) y fase (3e-11 rad). Fase 3 superada.

**No entendí:**
- Por qué el giro negativo necesita sus propias plantillas y no lo cubre una masa distinta, si en la fase 2 la masa y el giro se confundían tanto (~12 % por cada 0.25 de giro).
- Por qué el *glitch* de GW170814 se parece justo a la plantilla más pesada, la más corta del banco.
- Cuánto vale de verdad "el disparo más fuerte en 20 s": ¿cuántas veces el ruido solo daría 9.8 como GW151012? Eso es el FAR de la fase 4.
- La desigualdad de Jensen: por qué el promedio de 1/X es mayor que 1/(promedio de X), y cómo se calcula cuánto mayor para la mediana de varios periodogramas.
- Por qué la serie post-newtoniana oscila: agregar el término de 2PN empeora el parecido (de 0.94 a 0.41) en lugar de mejorarlo.

**Siguiente:**
Terminar las pruebas de la fase 4 con GW150914 (notebook 12, ~2.2 h de cálculo) y después preparar mayo de 2019, el mes de O3 del boss, con un banco nuevo. Crear la cuenta de Kaggle.

## 2026-11-07
**Hecho:**
Revisé con Claude todo el código y los documentos; el informe, con lo que falta y lo que hay que decidir, está en `docs/revision-2026-11-07.md`. La preparación de cada segmento (compuerta, PSD y transformada) ahora puede usar la FFT de numpy, como el filtro, y el notebook 12 la usa. `gps_evento` y `catalogo` piden el catálogo GWTC-2.1 de forma explícita. Repetí el prototipo del 12 con el recorte de 8 s en los extremos de cada tramo y después ejecuté el 12 completo, con las 866 plantillas. Empecé la etapa 4.4 con el notebook `13-mayo-2019`: segmentos de calidad, eventos del catálogo y lista de archivos de mayo de 2019.

**Salió:**
Con la FFT de numpy, la preparación del 12 pasó de 460 s a 85 s; con la FFT propia, todo da igual bit a bit que antes. Sin el catálogo explícito, GWOSC devolvía para GW190503 la versión de IAS (con el GPS 0.1 s corrido) y con GW190521 fallaba. El recorte arregla P27: el ρ² medio en la parte válida es 2.053 (esperado ≈ 2.03) y L1 ya no se llena de disparos basura. El notebook 12 tardó 2 h 16 min. GW150914 da SNR de red reponderado 22.60, por encima de los 19.4 años de fondo, y el ruido más fuerte del fondo llega a 9.15. Los demás candidatos son los que predice el fondo: 6 con red ≥ 7, donde se esperaban 4.0 ± 2.0. Mini-boss de la 4.3 superado. La compuerta deja disparos en los segundos que la rodean (36 en H1 y 83 en L1, cuando lo normal serían 1.5), pero el χ² los baja a 5.3 o menos. Mayo de 2019 tiene 18.31 días analizables y los 9 eventos de GWTC-2.1 caen dentro. Su masa chirp en el detector va de 18.7 a 98.7, y el banco actual llega hasta 45, así que no alcanza. Son 452 archivos de 4096 s por detector, ~118 GB. La coincidencia con todos los *time slides* no escala a un mes, porque el fondo crece con el cuadrado del tiempo: habrá que hacerla por días.

**No entendí:**
- Por qué con el banco completo GW150914 sube tanto (de 14.6 con 1 de cada 20 plantillas a 22.6) y el ruido más fuerte del fondo casi no cambia (de 8.94 a 9.15), si con 20 veces más plantillas el ruido tiene 20 veces más intentos.
- Qué IFAR conviene dar cuando ningún punto del fondo supera al candidato: "> 19.4 años" o (N+1)/T, como en los artículos de LIGO.

**Siguiente:**
Hacer commit y push, ejecutar en Colab la celda del χ² del 09 y crear la cuenta de Kaggle. Aprobar los criterios del boss y armar el banco para O3 (notebook 14).

## 2026-11-09
**Hecho:**
No toqué el buscador: preparé con Claude las herramientas para trabajar mejor. Quedó `pruebas/regresion.py`, que en unos 20 s comprueba las funciones de `src/` con ruido sintético y guarda una referencia para ver si algo cambia bit a bit. También una carpeta `.claude/` (fuera de git) con comandos para empezar y cerrar cada sesión, ejecutar notebooks y revisar el código, y un equipo de agentes: un verificador, un bibliotecario, cuatro físicos (dirección, estadística, formas de onda y detector) y dos ingenieros (GPU y pipeline). Claude buscó además quién encontró señales fuera de los catálogos oficiales y cómo.

**Salió:**
La regresión pasa con 0 fallos y detecta dos errores puestos a propósito en una copia. O4b es público desde el 26 de mayo de 2026, junto con GWTC-5.0 (390 candidatos en total), así que los datos de la fase 5 ya existen. Los grupos independientes (IAS, OGC) sí añadieron candidatos a los catálogos en O1–O3, pero siempre cerca del umbral y sobre todo en masa alta. Al probar la compuerta con un *glitch* artificial fuerte, el centro quedó 0.125 s antes del pico (P33). Los agentes nuevos y los avisos automáticos todavía no están probados.

**No entendí:**
(por completar)

**Siguiente:**
Abrir la sesión en `cazador-ondas` y usar `/retomar`. Hacer commit y push, la celda del χ² del 09 en Colab y la cuenta de Kaggle. Lanzar el consejo sobre masa alta en O4b como nicho de la fase 5 y seguir con el banco para O3 (notebook 14).
