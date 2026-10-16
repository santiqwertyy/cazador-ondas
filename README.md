# Cazador de ondas

Buscador de ondas gravitacionales.

## Objetivo

Este proyecto, escrito en Python, se enfoca en hacer un buscador de ondas gravitacionales desde cero, usando datos públicos de LIGO/Virgo, para intentar encontrar una señal nueva, preferiblemente de agujeros negros.

## Fases

0. Estructura del proyecto y entorno.
1. Explorar GW150914: descargar, graficar, espectro de ruido, blanqueado y filtrado hasta ver el "chirp".
2. Recuperar GW150914 con *matched filtering* y obtener un SNR parecido al publicado.
3. Repetirlo con otros eventos conocidos (GW151226, GW170104...).
4. Estimar el fondo de ruido y la tasa de falsas alarmas.
5. Recorrer tramos largos de datos buscando candidatos.

## Estado actual

Fase 1: ya descargo y grafico los 32 s de H1 y L1 alrededor de GW150914.

## Cómo montar el entorno

Necesitas conda (Anaconda o Miniconda).

```
git clone https://github.com/santiqwertyy/cazador-ondas.git   # descarga el repositorio
cd cazador-ondas                        # entra en el repositorio
conda env create -f environment.yml     # crea el entorno con los paquetes necesarios
conda activate cazador                  # activa el entorno
python -m ipykernel install --user --name cazador --display-name "Python (cazador)"   # registra el kernel para Jupyter
nbstripout --install --attributes .gitattributes   # no subir las salidas de los notebooks a git
```

En los notebooks, elige el kernel "Python (cazador)".

## Estructura

- `datos/`: datos descargados de GWOSC (no incluidos en el repo; los notebooks los guardan aquí la primera vez).
- `notebooks/`: exploración y análisis.
- `src/`: código fuente del buscador.
- `diario.md`: resumen de cada día que avanzo en el proyecto.
- `environment.yml`: receta del entorno de conda.
- `LICENSE`: licencia MIT.
