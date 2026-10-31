import numpy as np

from senal import blanquear


def interseccion(a, b):
    resultado = []
    i = j = 0
    while i < len(a) and j < len(b):
        inicio = max(a[i][0], b[j][0])
        fin = min(a[i][1], b[j][1])
        if inicio < fin:
            resultado.append((inicio, fin))
        if a[i][1] < b[j][1]:
            i += 1
        else:
            j += 1
    return resultado


def duracion(segmentos):
    return sum(fin - inicio for inicio, fin in segmentos)


def dentro(t, segmentos):
    inicios = np.array([inicio for inicio, fin in segmentos])
    fines = np.array([fin for inicio, fin in segmentos])
    cual = np.searchsorted(inicios, t, side="right") - 1
    return (cual >= 0) & (t < fines[np.maximum(cual, 0)])


def tiempo_virtual(t, segmentos):
    inicios = np.array([inicio for inicio, fin in segmentos])
    antes = np.cumsum([0] + [fin - inicio for inicio, fin in segmentos[:-1]])
    cual = np.searchsorted(inicios, t, side="right") - 1
    return antes[cual] + t - inicios[cual]


def segmentos_de_analisis(inicio, fin, duracion_segmento, borde_inicial, borde_final):
    paso = duracion_segmento - borde_inicial - borde_final
    inicios = list(range(inicio, fin - duracion_segmento, paso)) + [fin - duracion_segmento]
    resultado = []
    inicio_valido = inicio + borde_inicial
    for s in inicios:
        fin_valido = s + duracion_segmento - borde_final
        resultado.append((s, inicio_valido, fin_valido))
        inicio_valido = fin_valido
    return resultado


def compuerta(x, fs, umbral, ancho, transicion):
    blanqueado = blanquear(x, fs, 4)
    blanqueado[: 2 * fs] = 0
    blanqueado[-2 * fs :] = 0
    fuertes = np.flatnonzero(np.abs(blanqueado) > umbral)
    mitad = ancho * fs
    centros = []
    for i in fuertes:
        if not centros or i - centros[-1] > mitad:
            centros.append(i)
    distancia = np.full(len(x), np.inf)
    for c in centros:
        distancia = np.minimum(distancia, np.abs(np.arange(len(x)) - c))
    rampa = np.clip((distancia - mitad) / (transicion * fs), 0, 1)
    return x * (0.5 - 0.5 * np.cos(np.pi * rampa)), [c / fs for c in centros]


def disparos(rho, ventana, umbral):
    relleno = -rho.shape[1] % ventana
    bloques = np.pad(rho, ((0, 0), (0, relleno))).reshape(len(rho), -1, ventana)
    maximos = bloques.max(axis=2)
    plantilla, bloque = np.nonzero(maximos >= umbral)
    muestra = bloque * ventana + bloques[plantilla, bloque].argmax(axis=1)
    return plantilla, muestra, maximos[plantilla, bloque]


def coincidencias(tau_h1, plantilla_h1, tau_l1, plantilla_l1, ventana, paso):
    pares_h1, pares_l1, desplazamientos = [], [], []
    for p in np.intersect1d(plantilla_h1, plantilla_l1):
        i = np.flatnonzero(plantilla_h1 == p)
        j = np.flatnonzero(plantilla_l1 == p)
        diferencia = tau_h1[i][:, None] - tau_l1[j][None, :]
        k = np.round(diferencia / paso)
        a, b = np.nonzero(np.abs(diferencia - k * paso) <= ventana)
        pares_h1.append(i[a])
        pares_l1.append(j[b])
        desplazamientos.append(k[a, b].astype(int))
    return np.concatenate(pares_h1), np.concatenate(pares_l1), np.concatenate(desplazamientos)


def agrupar(desplazamiento, tiempo, valor, ventana):
    orden = np.argsort(-valor)
    clave = np.stack([desplazamiento[orden], np.floor(tiempo[orden] / ventana)], axis=1)
    _, primeros = np.unique(clave, axis=0, return_index=True)
    return orden[primeros]


def tiempo_fondo(duracion_total, paso):
    k = np.arange(1, int(duracion_total / paso) + 1)
    return 2 * np.sum(duracion_total - k * paso)


def far(fondo, tiempo, valores):
    ordenado = np.sort(fondo)
    return (len(ordenado) - np.searchsorted(ordenado, valores)) / tiempo
