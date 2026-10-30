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

Siguiente: fase 2, generar un chirp newtoniano y estimar la masa chirp de GW150914 a partir del espectrograma.

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
- `notebooks/`: exploración y análisis.
- `src/`: código del buscador. `senal.py`: FFT, Welch, blanqueado y pasa banda.
- `diario.md`: registro de cada día de trabajo.
- `environment.yml`: definición del entorno de conda.
- `LICENSE`: licencia MIT.
