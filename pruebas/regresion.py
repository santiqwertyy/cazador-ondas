import sys
import time
from pathlib import Path

import numpy as np
import scipy.signal

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))
from busqueda import agrupar, coincidencias, compuerta, dentro, disparos, far, interseccion, segmentos_de_analisis, tiempo_fondo, tiempo_virtual
from filtro_adaptado import bandas_chi2, chi2, serie_snr, snr_optimo, snr_reponderado, transformada
from plantillas import generador, taylorf2
from senal import blanquear, fft, ifft, irfft, rfft, welch

REFERENCIA = Path(__file__).with_name("referencia.npz")
GUARDAR = "--guardar" in sys.argv
SEMILLA = 0
FS = 4096
DURACION = 16
F_MIN = 20
F_MAX = 1024
BANDAS = 16
REALIZACIONES = 20
SNR_INYECTADO = 20
T_INYECCION = 9.0
T_GLITCH = 6.5
ALTURA_GLITCH = 1e-18
COMPUERTA_UMBRAL = 50
COMPUERTA_ANCHO = 0.25
COMPUERTA_TRANSICION = 0.25

reloj = time.perf_counter()
rng = np.random.default_rng(SEMILLA)
fallos = []
referencia = {}


def comprobar(nombre, diferencia, tolerancia):
    bien = diferencia <= tolerancia
    print(f"{'bien ' if bien else 'FALLA'} {nombre}: {diferencia:.1e} (tolerancia {tolerancia:.0e})")
    if not bien:
        fallos.append(nombre)


def exigir(nombre, condicion):
    print(f"{'bien ' if condicion else 'FALLA'} {nombre}")
    if not condicion:
        fallos.append(nombre)


def distancia(a, b):
    return float(np.max(np.abs(np.asarray(a) - np.asarray(b))) / np.max(np.abs(b)))


print("FFT")
x = rng.standard_normal(4096) + 1j * rng.standard_normal(4096)
comprobar("fft propia frente a numpy", distancia(fft(x), np.fft.fft(x)), 1e-10)
comprobar("ifft propia frente a numpy", distancia(ifft(x), np.fft.ifft(x)), 1e-10)
comprobar("rfft propia frente a numpy", distancia(rfft(x.real), np.fft.rfft(x.real)), 1e-10)
comprobar("irfft(rfft(x)) devuelve x", distancia(irfft(rfft(x.real)), x.real), 1e-10)
referencia["fft"] = fft(x)

print("Welch")
blanco = rng.standard_normal(64 * 256)
_, psd_media = welch(blanco, 256, 1024)
_, psd_scipy = scipy.signal.welch(blanco, 256, nperseg=1024)
comprobar("welch con media frente a scipy", distancia(psd_media, psd_scipy), 1e-9)
_, psd_mediana = welch(blanco, 256, 1024, "mediana", solapamiento=0)
_, psd_scipy = scipy.signal.welch(blanco, 256, nperseg=1024, noverlap=0, average="median")
comprobar("welch con mediana frente a scipy", distancia(psd_mediana, psd_scipy), 1e-9)
referencia["welch_media"] = psd_media
referencia["welch_mediana"] = psd_mediana

n = DURACION * FS
df = FS / n
frecuencias = np.arange(n // 2 + 1) * df
f_suave = np.maximum(frecuencias, 10)
psd = 1e-46 * ((60 / f_suave) ** 4 + 2 + 2 * (f_suave / 200) ** 2)


def ruido():
    return np.fft.irfft(np.fft.rfft(rng.standard_normal(n)) * np.sqrt(psd * FS / 2), n)


print("Blanqueado y compuerta")
x = ruido()
blanqueado = blanquear(x, FS, 4)
comprobar("blanquear: FFT propia frente a numpy", distancia(blanquear(x, FS, 4, directa=np.fft.fft), blanqueado), 1e-8)
referencia["blanqueado"] = blanqueado[::64]
muestra_glitch = int(T_GLITCH * FS)
con_glitch = x.copy()
con_glitch[muestra_glitch] += ALTURA_GLITCH
salida, centros = compuerta(con_glitch, FS, COMPUERTA_UMBRAL, COMPUERTA_ANCHO, COMPUERTA_TRANSICION)
exigir("compuerta: un solo glitch, en su sitio", len(centros) == 1 and abs(centros[0] - T_GLITCH) < 0.01)
exigir("compuerta: cero en el glitch", salida[muestra_glitch] == 0)
exigir("compuerta: lejos del glitch no toca nada", np.array_equal(salida[:FS], x[:FS]))
exigir("compuerta: sin glitch no hay centros", len(compuerta(x, FS, COMPUERTA_UMBRAL, COMPUERTA_ANCHO, COMPUERTA_TRANSICION)[1]) == 0)
referencia["compuerta"] = salida[::64]

print("Filtro adaptado y chi2")
n_salida = n // 2
fs_salida = n_salida // DURACION
indices = np.arange(int(F_MIN / df), int(F_MAX / df) + 1)
plantilla = generador(indices * df, F_MIN)(30.0, 0.25, 0.0)
sigma = snr_optimo(plantilla, psd, df, indices)
validas = np.arange(3 * fs_salida, 15 * fs_salida, 41)
rho2 = []
chi2_reducido = []
for _ in range(REALIZACIONES):
    datos_f = transformada(ruido(), FS, FS // 2, np.fft.fft)
    rho = serie_snr(datos_f, plantilla[None, :], psd, df, n_salida, indices, np.fft.ifft)[0]
    rho2.append(rho[3 * fs_salida : 15 * fs_salida] ** 2)
    valores_chi2 = chi2(datos_f, plantilla, psd, df, n_salida, indices, validas, BANDAS)
    chi2_reducido.append(valores_chi2 / (2 * BANDAS - 2))
comprobar("rho^2 medio en ruido gaussiano, esperado 2", abs(np.mean(rho2) - 2), 0.05)
comprobar("chi2 reducido medio, esperado 1", abs(np.mean(chi2_reducido) - 1), 0.03)
comprobar("varianza del chi2 reducido, esperada 2/(2B-2)", abs(np.var(chi2_reducido) - 2 / (2 * BANDAS - 2)), 0.01)
propia = serie_snr(datos_f, plantilla[None, :], psd, df, n_salida, indices)[0]
comprobar("serie_snr: FFT propia frente a numpy", distancia(propia, rho), 1e-9)
comprobar("transformada: FFT propia frente a numpy", distancia(transformada(x, FS, FS // 2), transformada(x, FS, FS // 2, np.fft.fft)), 1e-9)
producto = np.conj(plantilla) * datos_f[indices] / psd[indices]
suma_directa = [abs(4 * df * np.sum(producto * np.exp(2j * np.pi * (indices * m % n_salida) / n_salida))) / sigma for m in validas[:5]]
comprobar("serie_snr frente a la suma directa", distancia(suma_directa, rho[validas[:5]]), 1e-9)
inicios = np.concatenate([[0], bandas_chi2(plantilla, psd, indices, BANDAS)])
potencia = np.add.reduceat(np.abs(plantilla) ** 2 / psd[indices], inicios)
comprobar("bandas del chi2 con la misma potencia", distancia(potencia, np.full(BANDAS, potencia.mean())), 0.05)
referencia["plantilla"] = plantilla[::16]
referencia["rho"] = rho[::16]
referencia["chi2"] = valores_chi2

print("Inyeccion")
muestra_inyeccion = int(T_INYECCION * fs_salida)
senal_f = np.zeros(n // 2 + 1, dtype=complex)
senal_f[indices] = SNR_INYECTADO / sigma * plantilla * np.exp(-2j * np.pi * indices * df * T_INYECCION)
rho_limpia = serie_snr(senal_f, plantilla[None, :], psd, df, n_salida, indices, np.fft.ifft)[0]
exigir("sin ruido, el pico cae en la muestra inyectada", int(rho_limpia.argmax()) == muestra_inyeccion)
comprobar("sin ruido, el pico vale el SNR inyectado", abs(rho_limpia.max() - SNR_INYECTADO), 1e-9)
datos_f = transformada(ruido(), FS, FS // 2, np.fft.fft) + senal_f
rho_inyeccion = serie_snr(datos_f, plantilla[None, :], psd, df, n_salida, indices, np.fft.ifft)[0]
pico = int(rho_inyeccion.argmax())
exigir("con ruido, el pico cae a 2 muestras o menos", abs(pico - muestra_inyeccion) <= 2)
comprobar("con ruido, el pico se parece al SNR inyectado", abs(rho_inyeccion[pico] - SNR_INYECTADO), 3)
chi2_pico = chi2(datos_f, plantilla, psd, df, n_salida, indices, np.array([pico]), BANDAS)
exigir("la senal inyectada pasa el chi2 (reducido < 2)", chi2_pico[0] / (2 * BANDAS - 2) < 2)
reponderado = snr_reponderado(np.array([10.0, 10.0]), np.array([30.0, 60.0]), BANDAS)
comprobar("snr_reponderado", distancia(reponderado, np.array([10, 10 / 4.5 ** (1 / 6)])), 1e-12)
referencia["rho_inyeccion"] = rho_inyeccion[::16]
referencia["chi2_pico"] = chi2_pico
referencia["taylorf2"] = taylorf2(indices * df, 1.2, 0.25)[::16]

print("Busqueda")
exigir("interseccion", interseccion([(0, 10), (20, 30)], [(5, 25), (28, 40)]) == [(5, 10), (20, 25), (28, 30)])
validos = [(v0, v1) for s, v0, v1 in segmentos_de_analisis(0, 1000, 256, 16, 4)]
sin_huecos = all(validos[k][1] == validos[k + 1][0] for k in range(len(validos) - 1))
exigir("segmentos_de_analisis cubre de 16 a 996 sin huecos", sin_huecos and validos[0][0] == 16 and validos[-1][1] == 996)
tiempos = np.array([4.0, 5.0, 9.99, 10.0, 15.0, 22.0, 41.0])
exigir("dentro", np.array_equal(dentro(tiempos, [(5, 10), (20, 25)]), [False, True, True, False, False, True, False]))
exigir("tiempo_virtual", np.array_equal(tiempo_virtual(np.array([5.0, 9.5, 20.0, 24.0]), [(5, 10), (20, 25)]), [0, 4.5, 5, 9]))
rho = np.zeros((3, 50))
rho[0, 7] = 6
rho[0, 8] = 5.5
rho[1, 23] = 4.9
rho[2, 48] = 7
rho[2, 41] = 5.2
cual, muestra, valor = disparos(rho, 10, 5.0)
exigir("disparos", np.array_equal(cual, [0, 2]) and np.array_equal(muestra, [7, 48]) and np.array_equal(valor, [6, 7]))
exigir("far", np.array_equal(far(np.array([1.0, 2.0, 3.0, 4.0]), 2.0, np.array([0.5, 2.0, 3.5, 5.0])), [2, 1.5, 0.5, 0]))
T = 20000.0
tasa = 0.05
ventana = 0.012
paso = 0.1
plantillas = 4
comprobar("tiempo_fondo, esperado T^2/paso - T", abs(tiempo_fondo(T, paso) / (T**2 / paso - T) - 1), 1e-9)
t_h1 = np.sort(rng.uniform(0, T, rng.poisson(tasa * T * plantillas)))
t_l1 = np.sort(rng.uniform(0, T, rng.poisson(tasa * T * plantillas)))
p_h1 = rng.integers(0, plantillas, len(t_h1))
p_l1 = rng.integers(0, plantillas, len(t_l1))
i, j, k = coincidencias(t_h1, p_h1, t_l1, p_l1, ventana, paso)
pares = sum(np.sum(p_h1 == p) * np.sum(p_l1 == p) for p in range(plantillas))
esperadas = pares * 2 * ventana / paso
comprobar("coincidencias frente a las esperadas (pares * 2 * ventana / paso), en sigmas", abs(len(i) - esperadas) / np.sqrt(esperadas), 5)
exigir("coincidencias dentro de la ventana y con la misma plantilla", bool(np.all(np.abs(t_h1[i] - t_l1[j] - k * paso) <= ventana) and np.all(p_h1[i] == p_l1[j])))
valor = rng.uniform(0, 10, len(i))
grupos = agrupar(k, t_h1[i], valor, 1.0)
clave = np.stack([k, np.floor(t_h1[i])], axis=1)
maximos = all(valor[g] == valor[np.all(clave == clave[g], axis=1)].max() for g in grupos[:300])
exigir("agrupar elige el maximo de cada grupo y no repite grupos", maximos and len(np.unique(clave[grupos], axis=0)) == len(grupos))
referencia["coincidencias"] = np.array([len(i), np.sum(k != 0), len(grupos)])

print("Referencia guardada (0.0e+00 es igual bit a bit)")
if GUARDAR or not REFERENCIA.exists():
    np.savez(REFERENCIA, **referencia)
    print(f"referencia nueva escrita en {REFERENCIA.name}")
else:
    guardada = np.load(REFERENCIA)
    for nombre, valor in referencia.items():
        comprobar(f"referencia: {nombre}", distancia(valor, guardada[nombre]), 1e-10)

print(f"{len(fallos)} fallos en {time.perf_counter() - reloj:.0f} s" + "".join(f"\n  {nombre}" for nombre in fallos))
sys.exit(1 if fallos else 0)
