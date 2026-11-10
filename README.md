# Cazador de ondas

Buscador de ondas gravitacionales escrito desde cero en Python sobre los datos públicos de LIGO/Virgo (GWOSC).

## Objetivo

Recorrer tramos largos de datos y encontrar una señal que no esté en los catálogos, preferiblemente de agujeros negros.

No hay garantía de que esa señal exista en los datos públicos. Lo que sí se puede asegurar es el método: cada paso se valida primero contra eventos ya confirmados.

## Términos

- **Chirp**: forma de la señal de una fusión; la frecuencia y la amplitud suben juntas hasta el choque.
- **Blanqueado**: normalizar los datos por el espectro de ruido para que ninguna frecuencia domine sobre las demás.
- ***Matched filtering***: correlacionar los datos con plantillas teóricas de la señal.
- **SNR**: relación señal-ruido; cuánto sobresale una coincidencia sobre lo que produciría el ruido solo.
- **Tasa de falsas alarmas**: con qué frecuencia el ruido, sin ninguna señal, genera un candidato igual de fuerte.

## Fases

Cada fase termina con una prueba que hay que superar antes de pasar a la siguiente.

0. **Tu primera onda.** GW150914 con gwpy: datos en bruto, espectro de ruido, blanqueado, filtrado, Q-transform y `.wav`. Prueba: la señal se ve y se oye en H1 y L1.
1. **Matemáticas de la señal.** FFT, estimación del espectro (Welch), blanqueado y filtros escritos a mano. Prueba: el blanqueado propio de GW150914 coincide con el de gwpy.
2. **Física.** Generador de chirp a orden newtoniano y estimación de la masa chirp desde el espectrograma. Prueba: masa chirp de GW150914 cercana a la del catálogo.
3. ***Matched filtering*.** Filtro propio, banco de plantillas e inyecciones. Prueba: GW150914 en H1 y L1 con el retraso correcto entre detectores, y 5 eventos más de O1/O2.
4. **Buscador completo.** Banco de plantillas amplio, test χ², calidad de datos, coincidencia entre detectores, fondo por time slides y tasa de falsas alarmas. Prueba: un mes de O3 procesado, recuperando los eventos del catálogo.
5. **Especialización y caza.** Una búsqueda de nicho sobre O4b y O4c. Prueba: candidatos significativos que no estén en ningún catálogo.
6. **Validación y publicación.**

El orden no es arbitrario: cada fase valida la herramienta que usa la siguiente.

## Estado actual

Fase 0 superada. Con los 32 s de H1 y L1 alrededor de GW150914, el notebook `01-gw150914` grafica los datos en bruto, calcula el espectro de ruido, blanquea los datos y los filtra entre 35 y 350 Hz. El chirp se ve en los dos detectores y en el Q-transform, y se oye en `datos/H1_GW150914.wav` y `datos/L1_GW150914.wav`.

Fase 1 superada. El notebook `02-fft` tiene la transformada de Fourier discreta escrita a mano, primero por la definición y después con el algoritmo de Cooley–Tukey, comparadas con `numpy.fft`. Con ella se recupera un seno de 123 Hz diez veces más débil que el ruido. `src/senal.py` reúne esa FFT, la estimación de la PSD por el método de Welch, el blanqueado y un filtro pasa banda, todo escrito a mano. En `03-welch`, la PSD coincide con la de `scipy.signal.welch` y gwpy en una parte en 10^10. En `04-blanqueado`, el blanqueado de GW150914 coincide con el de gwpy en las 131072 muestras de H1 y L1 (diferencia máxima 3e-11). Después de filtrar entre 35 y 350 Hz, la correlación con gwpy es 0.98: gwpy usa otro tipo de filtro.

Fase 2 superada. El notebook `05-chirp` genera el chirp newtoniano y estima la masa chirp desde el espectrograma: para GW150914 da 29.25 M☉ en H1 y 28.75 M☉ en L1, pero ese método era impreciso (±5.6 % en inyecciones), y según qué parte de la señal se usara la masa iba de 25 a 38 M☉, porque la fórmula newtoniana no describe el final de la fusión.

El notebook `06-masa-chirp` lo resuelve con *matched filtering* escrito a mano (`src/filtro_adaptado.py`) y plantillas IMRPhenomD generadas con ripple. La masa chirp de GW150914 con H1 y L1 combinados es **30.8 M☉ (90 %: 29.4–32.2)**, medida en el detector; LIGO da 30.2 (artículo de 2016) y ≈30.7 (catálogo GWTC-2.1). El giro efectivo sale −0.05 (GWTC-2.1: −0.04), y la señal llega a L1 7.1 ms antes que a H1. Con inyecciones en el ruido real, el sesgo es −0.2 %, la dispersión 1.2 %, y las 30 quedan a menos del 5 %.

Fase 3 superada. El notebook `07-banco` arma a mano un banco de 866 plantillas IMRPhenomD (masa chirp de 6 a 45 M☉, 5 combinaciones de razón de masas y giro), colocadas para que dos vecinas se parezcan un 90 %. Con 200 señales de otro modelo (IMRPhenomXAS) al azar, el 93 % encuentra una plantilla con un parecido de 0.95 o más (mediana 0.982).

El notebook `08-eventos-o1-o2` recorre con ese banco 18.5 s de datos de H1 y L1 alrededor de 7 eventos y exige coincidencia entre detectores (misma plantilla, ≤10 ms). En los 7, el disparo más fuerte cae a menos de 0.05 s del tiempo del catálogo:

| Evento | SNR de red (catálogo) | L1 − H1 | Masa chirp de la mejor plantilla (catálogo, en el detector) |
|---|---|---|---|
| GW150914 | 24.6 (26.0) | −7.3 ms | 33.0 (≈30.7) |
| GW151012 | 9.8 (9.3) | +1.0 ms | 17.4 (≈18.7) |
| GW151226 | 12.8 (12.7) | −1.0 ms | 9.7 (≈9.8) |
| GW170104 | 13.6 (13.8) | +2.9 ms | 24.3 (≈25.7) |
| GW170608 | 15.3 (15.3) | +7.3 ms | 8.5 (≈8.5) |
| GW170814 | 16.6 (17.7) | −8.3 ms | 25.9 (≈27.2) |
| GW170823 | 12.0 (12.2) | +1.0 ms | 37.9 (≈38.9) |

10 señales IMRPhenomXAS inyectadas en el ruido real se recuperan todas, con SNR recuperado / inyectado de 0.95 (mediana; con 10 inyecciones la mediana varía unos ±0.04 de una tanda a otra, y una tanda anterior, con las mismas señales en otros instantes, dio 1.00). Esto todavía no mide la significancia de nada: eso es la fase 4 (FAR e IFAR).

Modo difícil de la fase 3: la forma de onda TaylorF2 (la espiral post-newtoniana hasta 3.5PN) escrita a mano en `src/plantillas.py`. En el notebook `10-taylorf2` coincide con la de ripple, que sigue a LALSuite, en amplitud (2e-15) y fase (3e-11 rad). También muestra que la serie post-newtoniana converge oscilando y que, frente a IMRPhenomD, TaylorF2 solo alcanza para masas chirp menores a ~6 M☉: para agujeros negros más pesados hace falta la fusión.

En Google Colab (notebook `09-validacion-pycbc`), mi serie de SNR de GW150914 coincide con la de `pycbc.filter.matched_filter` hasta 7e-16 (el redondeo de la máquina) en H1 y L1, con el mismo pico (20.6303 y 14.1760) en el mismo instante y el mismo σ; las plantillas de ripple dan parecido 1.00000 con las de LALSuite (IMRPhenomD e IMRPhenomXAS, 5 puntos del banco), y mi TaylorF2 coincide con la de PyCBC en amplitud (3e-15) y fase (3e-11 rad).

Fase 4 en curso: test χ² de Allen, compuerta para *glitches* fuertes, segmentos de calidad de GWOSC, coincidencia y *time slides* para medir el fondo (`src/busqueda.py`, notebooks `11-chi2` y `12-fondo-gw150914`). El boss será mayo de 2019 (O3a).

En el notebook `11-chi2`, el test χ² da χ²_r ≈ 1 en ruido gaussiano, baja el *glitch* de GW170814 de SNR 13.9 a 4.1 y deja a los 7 eventos de O1/O2 con su SNR.

El notebook `12-fondo-gw150914` es la búsqueda entera en 2.2 h de datos de H1 y L1 alrededor de GW150914 (7825 s analizados, 866 plantillas). Primero aplica la calidad de datos, la compuerta y el χ². Después busca coincidencias desplazando L1 en pasos de 0.1 s, lo que da 19.4 años de fondo. GW150914 sale con SNR de red reponderado 22.60, por encima de todo ese fondo (IFAR > 19.4 años). El ruido más fuerte del fondo llega a 9.15. Los demás candidatos del primer plano son los que predice el fondo: 6 con SNR de red 7 o más, donde se esperaban 4.0 ± 2.0.

El notebook `13-mayo-2019` prepara el boss. Mayo de 2019 tiene 18.31 días con H1 y L1 aptos para la búsqueda y los 9 eventos del catálogo GWTC-2.1 caen dentro. Sus masas chirp en el detector van de 18.7 a 98.7 M☉, así que hace falta un banco que llegue más arriba que el actual. Los datos son 452 archivos por detector (~118 GB): la búsqueda irá en Kaggle, con GPU.

## Entorno

Requiere conda (Anaconda o Miniconda).

```
git clone https://github.com/santiqwertyy/cazador-ondas.git
cd cazador-ondas
conda env create -f environment.yml     # crea el entorno
conda activate cazador
python -m ipykernel install --user --name cazador --display-name "Python (cazador)"   # registra el kernel
nbstripout --install --attributes .gitattributes   # evita subir las salidas de los notebooks
```

En los notebooks, el kernel es "Python (cazador)".

El entorno usa OpenBLAS en lugar de MKL. Con MKL, el kernel se caía en Windows por un conflicto de DLL con anaconda base.

## Estructura

- `datos/`: datos descargados de GWOSC. No están en el repositorio; los notebooks los guardan aquí la primera vez.
- `notebooks/`: exploración y análisis. Se ejecutan en orden: el 01 descarga los datos de GW150914 que usan del 03 al 06, y el 07 crea el banco de plantillas que usan el 08, el 11 y el 12. El 09 es solo para Google Colab. El 10 es independiente. El 11 usa los datos de los eventos que baja el 08, y el 12 baja 2.2 h de datos alrededor de GW150914 (~500 MB). El 13 solo baja los segmentos de calidad y el catálogo de mayo de 2019.
- `src/`: código del buscador. `senal.py`: FFT, Welch, blanqueado, pasa banda y espectrograma. `filtro_adaptado.py`: *matched filtering*, parecido entre plantillas, coincidencia H1+L1 y test χ². `plantillas.py`: formas de onda con ripple y TaylorF2 escrita a mano. `datos.py`: descarga y caché de los datos, el tiempo GPS, los parámetros del catálogo y los segmentos de calidad. `busqueda.py`: segmentos de análisis, compuerta, disparos, coincidencia con *time slides*, tiempo de fondo y FAR.
- `diario.md`: registro de cada día de trabajo.
- `environment.yml`: definición del entorno de conda.
- `LICENSE`: licencia MIT.
