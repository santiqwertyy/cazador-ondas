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


def serie_snr(datos_f, plantillas, psd, df, n, indices, inversa=ifft):
    peso = datos_f[indices] / psd[indices]
    producto = np.zeros((len(plantillas), n), dtype=complex)
    producto[:, indices] = np.conj(plantillas) * peso
    z = 4 * inversa(producto) * n * df
    sigma = np.sqrt(4 * np.sum(np.abs(plantillas) ** 2 / psd[indices], axis=1) * df)
    return np.abs(z) / sigma[:, None]


def snr_optimo(plantilla, psd, df, indices):
    return np.sqrt(4 * np.sum(np.abs(plantilla) ** 2 / psd[indices]) * df)


def parecido(plantillas, b, psd, df, n, indices):
    espectro_b = np.zeros(n // 2 + 1, dtype=complex)
    espectro_b[indices] = b
    return serie_snr(espectro_b, plantillas, psd, df, n, indices).max(axis=1) / snr_optimo(b, psd, df, indices)


def bandas_chi2(plantilla, psd, indices, bandas):
    potencia = np.cumsum(np.abs(plantilla) ** 2 / psd[indices])
    return np.searchsorted(potencia, potencia[-1] * np.arange(1, bandas) / bandas)


def chi2(datos_f, plantilla, psd, df, n, indices, muestras, bandas):
    producto = np.conj(plantilla) * datos_f[indices] / psd[indices]
    inicios = np.concatenate([[0], bandas_chi2(plantilla, psd, indices, bandas)])
    sigma = snr_optimo(plantilla, psd, df, indices)
    valores = []
    for m in muestras:
        z_bandas = 4 * df * np.add.reduceat(producto * np.exp(2j * np.pi * (indices * m % n) / n), inicios)
        z = z_bandas.sum()
        valores.append(bandas * np.sum(np.abs(z_bandas - z / bandas) ** 2) / sigma**2)
    return np.array(valores)


def snr_reponderado(rho, valores_chi2, bandas):
    chi2_reducido = valores_chi2 / (2 * bandas - 2)
    return np.where(chi2_reducido > 1, rho / ((1 + chi2_reducido**3) / 2) ** (1 / 6), rho)


def snr_red(serie_h1, serie_l1, retraso_maximo):
    mejor_l1 = np.zeros_like(serie_l1)
    desplazamiento = np.zeros(serie_l1.shape, dtype=int)
    for k in range(-retraso_maximo, retraso_maximo + 1):
        corrida = np.roll(serie_l1, -k, axis=-1)
        mayor = corrida > mejor_l1
        mejor_l1[mayor] = corrida[mayor]
        desplazamiento[mayor] = k
    return np.sqrt(serie_h1**2 + mejor_l1**2), desplazamiento
