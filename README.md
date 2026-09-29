# Cazador de ondas

Buscador de ondas gravitacionales.

## Objetivo

Este proyecto, escrito en Python, se enfoca en hacer un buscador de ondas gravitacionales desde cero, usando datos públicos de LIGO/Virgo, para intentar encontrar una señal nueva, preferiblemente de agujeros negros.

## Estado actual

Actualmente estoy en la fase 0, haciendo la estructura.

## Cómo montar el entorno

Necesitas conda (Anaconda o Miniconda).

```
git clone https://github.com/santiqwertyy/cazador-ondas.git   # descarga el repositorio
cd cazador-ondas                        # entra en el repositorio
conda env create -f environment.yml     # crea el entorno con los paquetes necesarios
conda activate cazador                  # activa el entorno
```

## Estructura

- `datos/`: datos descargados de GWOSC (no incluidos en el repo).
- `notebooks/`: exploración y análisis.
- `src/`: código fuente del buscador.
- `diario.md`: resumen de cada día que avanzo en el proyecto.
- `environment.yml`: receta del entorno de conda.
- `LICENSE`: licencia MIT.
