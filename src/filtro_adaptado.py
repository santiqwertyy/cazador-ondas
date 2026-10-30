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
