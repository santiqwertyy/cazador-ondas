import numpy as np

from senal import hann, ifft, rfft, welch


def psd_en(frecuencias_destino, x, fs, duracion_fft):
    frecuencias, psd = welch(x, fs, duracion_fft * fs, "mediana", solapamiento=0)
    return np.interp(frecuencias_destino, frecuencias, psd)


def ventana_tukey(n, borde):
    ventana = np.ones(n)
    subida = hann(2 * borde)
    ventana[:borde] = subida[:borde]
    ventana[-borde:] = subida[borde:]
    return ventana


def transformada(x, fs, borde):
    return rfft(x * ventana_tukey(len(x), borde)) / fs


def serie_snr(datos_f, plantillas, psd, df, n, indices):
    peso = datos_f[indices] / psd[indices]
    producto = np.zeros((len(plantillas), n), dtype=complex)
    producto[:, indices] = np.conj(plantillas) * peso
    z = 4 * ifft(producto) * n * df
    sigma = np.sqrt(4 * np.sum(np.abs(plantillas) ** 2 / psd[indices], axis=1) * df)
    return np.abs(z) / sigma[:, None]


def snr_optimo(plantilla, psd, df, indices):
    return np.sqrt(4 * np.sum(np.abs(plantilla) ** 2 / psd[indices]) * df)


def parecido(plantillas, b, psd, df, n, indices):
    espectro_b = np.zeros(n // 2 + 1, dtype=complex)
    espectro_b[indices] = b
    return serie_snr(espectro_b, plantillas, psd, df, n, indices).max(axis=1) / snr_optimo(b, psd, df, indices)


def snr_red(serie_h1, serie_l1, retraso_maximo):
    mejor_l1 = np.zeros_like(serie_l1)
    desplazamiento = np.zeros(serie_l1.shape, dtype=int)
    for k in range(-retraso_maximo, retraso_maximo + 1):
        corrida = np.roll(serie_l1, -k, axis=-1)
        mayor = corrida > mejor_l1
        mejor_l1[mayor] = corrida[mayor]
        desplazamiento[mayor] = k
    return np.sqrt(serie_h1**2 + mejor_l1**2), desplazamiento
