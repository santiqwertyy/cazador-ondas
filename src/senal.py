import numpy as np


def fft(x):
    n = x.shape[-1]
    if n == 1:
        return np.array(x, dtype=complex)
    if n % 2 != 0:
        raise ValueError("la longitud tiene que ser una potencia de 2")
    mitades = fft(np.stack([x[..., 0::2], x[..., 1::2]]))
    pares = mitades[0]
    impares = mitades[1] * np.exp(-2j * np.pi * np.arange(n // 2) / n)
    return np.concatenate([pares + impares, pares - impares], axis=-1)


def ifft(espectro):
    return np.conj(fft(np.conj(espectro))) / espectro.shape[-1]


def rfft(x):
    return fft(x)[..., : x.shape[-1] // 2 + 1]


def irfft(espectro):
    completo = np.concatenate([espectro, np.conj(espectro[..., -2:0:-1])], axis=-1)
    return ifft(completo).real


def potencia_de_2(n):
    return 2 ** int(np.ceil(np.log2(n)))


def hann(n):
    return 0.5 - 0.5 * np.cos(2 * np.pi * np.arange(n) / n)


def hann_simetrica(n):
    return 0.5 - 0.5 * np.cos(2 * np.pi * np.arange(n) / (n - 1))


def sesgo_mediana(k):
    impares = 1 / np.arange(3, k + 1, 2)
    pares = 1 / np.arange(2, k, 2)
    return 1 + impares.sum() - pares.sum()


def welch(x, fs, n_segmento, promedio="media", solapamiento=0.5):
    paso = int(n_segmento * (1 - solapamiento))
    ventana = hann(n_segmento)
    normalizacion = fs * np.sum(ventana**2)
    periodogramas = []
    for inicio in range(0, len(x) - n_segmento + 1, paso):
        segmento = x[inicio : inicio + n_segmento]
        segmento = (segmento - segmento.mean()) * ventana
        periodogramas.append(np.abs(rfft(segmento)) ** 2 / normalizacion)
    periodogramas = np.array(periodogramas)
    periodogramas[:, 1:-1] *= 2
    if promedio == "mediana":
        psd = np.median(periodogramas, axis=0) / sesgo_mediana(len(periodogramas))
    else:
        psd = periodogramas.mean(axis=0)
    frecuencias = np.arange(n_segmento // 2 + 1) * fs / n_segmento
    return frecuencias, psd


def convolucionar(x, filtro):
    n_total = len(x) + len(filtro) - 1
    n_fft = potencia_de_2(n_total)
    x_relleno = np.concatenate([x, np.zeros(n_fft - len(x))])
    filtro_relleno = np.concatenate([filtro, np.zeros(n_fft - len(filtro))])
    completa = ifft(fft(x_relleno) * fft(filtro_relleno)).real[:n_total]
    inicio = (len(filtro) - 1) // 2
    return completa[inicio : inicio + len(x)]


def filtro_blanqueador(asd, n_coeficientes):
    transferencia = 1 / asd
    borde = hann_simetrica(10)
    transferencia[:5] *= borde[:5]
    transferencia[-5:] *= borde[-5:]
    respuesta = irfft(transferencia)
    mitad = n_coeficientes // 2
    ventana = hann(n_coeficientes)
    respuesta[:mitad] *= ventana[mitad:]
    respuesta[-mitad:] *= ventana[:mitad]
    respuesta[mitad:-mitad] = 0
    return np.roll(respuesta, mitad - 1)[:n_coeficientes]


def asd_interpolada(x, fs, duracion_fft):
    frecuencias, psd = welch(x, fs, duracion_fft * fs, "mediana", solapamiento=0)
    frecuencias_x = np.arange(len(x) // 2 + 1) * fs / len(x)
    return np.interp(frecuencias_x, frecuencias, np.sqrt(psd))


def blanquear(x, fs, duracion_fft, duracion_filtro=2):
    filtro = filtro_blanqueador(asd_interpolada(x, fs, duracion_fft), duracion_filtro * fs)
    mitad = len(filtro) // 2
    ventana = hann(len(filtro))
    y = x - x.mean()
    y[:mitad] *= ventana[:mitad]
    y[-mitad:] *= ventana[-mitad:]
    return convolucionar(y, filtro) * np.sqrt(2 / fs)


def ganancia_pasa_banda(frecuencias, banda, corte):
    ganancia = np.zeros(len(frecuencias))
    ganancia[(frecuencias >= banda[0]) & (frecuencias <= banda[1])] = 1
    subida = (frecuencias > corte[0]) & (frecuencias < banda[0])
    ganancia[subida] = 0.5 - 0.5 * np.cos(np.pi * (frecuencias[subida] - corte[0]) / (banda[0] - corte[0]))
    bajada = (frecuencias > banda[1]) & (frecuencias < corte[1])
    ganancia[bajada] = 0.5 + 0.5 * np.cos(np.pi * (frecuencias[bajada] - banda[1]) / (corte[1] - banda[1]))
    return ganancia


def pasa_banda(x, fs, banda, corte):
    frecuencias = np.arange(len(x) // 2 + 1) * fs / len(x)
    return irfft(rfft(x) * ganancia_pasa_banda(frecuencias, banda, corte))


def espectrograma(x, fs, n_segmento, paso, n_fft):
    inicios = np.arange(0, len(x) - n_segmento + 1, paso)
    segmentos = np.array([x[i : i + n_segmento] for i in inicios]) * hann(n_segmento)
    relleno = np.zeros((len(inicios), n_fft - n_segmento))
    potencia = np.abs(rfft(np.concatenate([segmentos, relleno], axis=1))) ** 2
    tiempos = (inicios + n_segmento / 2) / fs
    frecuencias = np.arange(n_fft // 2 + 1) * fs / n_fft
    return tiempos, frecuencias, potencia.T
