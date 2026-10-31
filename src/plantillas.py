import jax
import jax.numpy as jnp
import numpy as np
from ripplegw.waveforms.cbc.IMRPhenomD import IMRPhenomD
from ripplegw.waveforms.cbc.IMRPhenomX import IMRPhenomXAS

jax.config.update("jax_enable_x64", True)

MODELOS = {"IMRPhenomD": IMRPhenomD.gen_IMRPhenomD, "IMRPhenomXAS": IMRPhenomXAS.gen_IMRPhenomXAS}
MASA_SOL_SEGUNDOS = 4.925490947641267e-6
MEGAPARSEC_SEGUNDOS = 3.085677581491367e22 / 299792458
GAMMA_EULER = 0.5772156649015329


def generador(frecuencias, f_min, modelo="IMRPhenomD"):
    f = jnp.array(frecuencias)
    funcion = jax.jit(lambda parametros: MODELOS[modelo](f, parametros, f_min))
    return lambda masa_chirp, eta, giro: np.asarray(funcion(jnp.array([masa_chirp, eta, giro, giro, 1.0, 0.0, 0.0])))


def fase_taylorf2(v, eta, orden=7):
    terminos = [
        np.ones_like(v),
        np.zeros_like(v),
        (3715 / 756 + 55 / 9 * eta) * v**2,
        -16 * np.pi * v**3,
        (15293365 / 508032 + 27145 / 504 * eta + 3085 / 72 * eta**2) * v**4,
        np.pi * (38645 / 756 - 65 / 9 * eta) * (1 + 3 * np.log(v)) * v**5,
        (
            11583231236531 / 4694215680
            - 640 / 3 * np.pi**2
            - 6848 / 21 * (GAMMA_EULER + np.log(4 * v))
            + (-15737765635 / 3048192 + 2255 / 12 * np.pi**2) * eta
            + 76055 / 1728 * eta**2
            - 127825 / 1296 * eta**3
        )
        * v**6,
        np.pi * (77096675 / 254016 + 378515 / 1512 * eta - 74045 / 756 * eta**2) * v**7,
    ]
    return 3 / (128 * eta * v**5) * sum(terminos[: orden + 1])


def taylorf2(frecuencias, masa_chirp, eta, orden=7):
    masa_total = masa_chirp / eta**0.6 * MASA_SOL_SEGUNDOS
    v = (np.pi * masa_total * frecuencias) ** (1 / 3)
    amplitud = np.sqrt(5 / 24) * np.pi ** (-2 / 3) * (masa_chirp * MASA_SOL_SEGUNDOS) ** (5 / 6) * frecuencias ** (-7 / 6) / MEGAPARSEC_SEGUNDOS
    h = amplitud * np.exp(-1j * (fase_taylorf2(v, eta, orden) - np.pi / 4))
    h[frecuencias > 1 / (6**1.5 * np.pi * masa_total)] = 0
    return h
