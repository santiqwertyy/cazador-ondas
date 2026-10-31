import json

from gwosc.api import fetch_event_json
from gwosc.datasets import event_gps
from gwpy.timeseries import TimeSeries


def gps_evento(evento, carpeta):
    archivo = carpeta / f"{evento}_gps.txt"
    if archivo.exists():
        return float(archivo.read_text())
    t0 = event_gps(evento)
    archivo.write_text(repr(t0))
    return t0


def cargar(ifo, evento, duracion, carpeta):
    archivo = carpeta / f"{ifo}_{evento}_{duracion}s.hdf5"
    if archivo.exists():
        return TimeSeries.read(archivo)
    t0 = gps_evento(evento, carpeta)
    serie = TimeSeries.fetch_open_data(ifo, t0 - duracion / 2, t0 + duracion / 2)
    temporal = archivo.with_suffix(".tmp.hdf5")
    serie.write(temporal, overwrite=True)
    temporal.replace(archivo)
    return serie


def catalogo(evento, carpeta):
    archivo = carpeta / f"{evento}_catalogo.json"
    if archivo.exists():
        return json.loads(archivo.read_text())
    parametros = list(fetch_event_json(evento)["events"].values())[0]
    archivo.write_text(json.dumps(parametros, indent=1))
    return parametros
