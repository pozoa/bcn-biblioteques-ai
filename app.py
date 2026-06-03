from __future__ import annotations

import csv
import json
import re
import unicodedata
import webbrowser
from collections import defaultdict
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "2024_dades_biblioteques.csv"
HOST = "127.0.0.1"
PORT = 8000


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9_ ]+", " ", text).strip()


def to_number(value: str) -> float:
    clean = value.strip().replace(".", "").replace(",", ".")
    try:
        return float(clean)
    except ValueError:
        return 0.0


class LibraryData:
    def __init__(self, csv_path: Path) -> None:
        self.csv_path = csv_path
        self.rows = self._load_rows()
        self.indicators = sorted({row["Indicador"] for row in self.rows})
        self.libraries = sorted({row["Nom_Equipament"] for row in self.rows})
        self.columns = list(self.rows[0].keys()) if self.rows else []
        self.by_indicator = defaultdict(list)
        self.by_library = defaultdict(dict)

        for row in self.rows:
            indicator = row["Indicador"]
            library = row["Nom_Equipament"]
            value = to_number(row["Valor"])
            self.by_indicator[indicator].append((library, value, row))
            self.by_library[library][indicator] = value

    def _load_rows(self) -> list[dict[str, str]]:
        if not self.csv_path.exists():
            raise FileNotFoundError(f"No s'ha trobat el fitxer: {self.csv_path}")
        with self.csv_path.open(newline="", encoding="utf-8") as file:
            return list(csv.DictReader(file))

    def indicator_from_question(self, question: str) -> str | None:
        normalized_question = normalize(question)
        aliases = {
            "visites": "Visites",
            "visitas": "Visites",
            "prestamos presenciales": "Prestecs_presencials",
            "prestecs presencials": "Prestecs_presencials",
            "prestecs presencial": "Prestecs_presencials",
            "prestecs presencials": "Prestecs_presencials",
            "prestecs_presencials": "Prestecs_presencials",
            "prestamos virtuales": "Prestecs_virtuals",
            "prestecs virtuals": "Prestecs_virtuals",
            "prestecs virtual": "Prestecs_virtuals",
            "prestecs virtuals": "Prestecs_virtuals",
            "prestecs_virtuals": "Prestecs_virtuals",
            "metros cuadrados": "Metres_Quadrats",
            "metres quadrats": "Metres_Quadrats",
            "metres_quadrats": "Metres_Quadrats",
            "actividades": "Nombre_Activitats",
            "activitats": "Nombre_Activitats",
            "asistentes actividades": "Assistents_Activitats",
            "fondo documental": "Fons_Documentals",
            "fons documentals": "Fons_Documentals",
            "ordenadores": "Usos_Ordinadors",
            "ordinadors": "Usos_Ordinadors",
            "visitas escolares": "Nombre_Visites_Escolars",
            "visites escolars": "Nombre_Visites_Escolars",
        }

        for alias, indicator in aliases.items():
            if alias in normalized_question:
                return indicator

        for indicator in self.indicators:
            if normalize(indicator) in normalized_question:
                return indicator
        return None

    def column_from_question(self, question: str) -> str | None:
        normalized_question = normalize(question)
        aliases = {
            "any": "Any",
            "ano": "Any",
            "indicador": "Indicador",
            "indicadores": "Indicador",
            "biblioteca": "Nom_Equipament",
            "bibliotecas": "Nom_Equipament",
            "biblioteques": "Nom_Equipament",
            "equipament": "Nom_Equipament",
            "valor": "Valor",
            "valores": "Valor",
            "notes dades": "Notes_Dades",
            "notes_dades": "Notes_Dades",
            "notes equipament": "Notes_Equipament",
            "notes_equipament": "Notes_Equipament",
            "codi districte": "Codi_Districte",
            "codi_districte": "Codi_Districte",
            "codigo distrito": "Codi_Districte",
            "codigos distrito": "Codi_Districte",
            "codis districtes": "Codi_Districte",
            "districte": "Nom_Districte",
            "districtes": "Nom_Districte",
            "distrito": "Nom_Districte",
            "distritos": "Nom_Districte",
            "codi barri": "Codi_Barri",
            "codi_barrri": "Codi_Barri",
            "codi_barri": "Codi_Barri",
            "codigo barrio": "Codi_Barri",
            "codigo de barrio": "Codi_Barri",
            "codigos barrio": "Codi_Barri",
            "codigos de barrio": "Codi_Barri",
            "codis barris": "Codi_Barri",
            "codis de barris": "Codi_Barri",
            "barri": "Nom_Barri",
            "barris": "Nom_Barri",
            "barrio": "Nom_Barri",
            "barrios": "Nom_Barri",
            "titularidad": "Titularitat",
            "titularitat": "Titularitat",
            "tipus us": "Tipus_Us",
            "tipus_us": "Tipus_Us",
            "tipus equipament": "Tipus_Equipament",
            "tipus_equipament": "Tipus_Equipament",
            "ambit": "Ambit",
            "latitud": "Latitud",
            "longitud": "Longitud",
            "coordenadas": "Latitud",
            "coordenades": "Latitud",
        }

        for alias, column in sorted(aliases.items(), key=lambda item: len(item[0]), reverse=True):
            if alias in normalized_question:
                return column

        for column in self.columns:
            if normalize(column) in normalized_question:
                return column
        return None

    def mentioned_library(self, question: str) -> str | None:
        normalized_question = normalize(question)
        matches = [
            library
            for library in self.libraries
            if normalize(library) in normalized_question
        ]
        if not matches:
            return None
        return max(matches, key=len)

    def group_column_from_question(self, question: str) -> str | None:
        normalized_question = normalize(question)
        group_aliases = {
            "por distrito": "Nom_Districte",
            "por distritos": "Nom_Districte",
            "segun distrito": "Nom_Districte",
            "segun distritos": "Nom_Districte",
            "per districte": "Nom_Districte",
            "per districtes": "Nom_Districte",
            "segons districte": "Nom_Districte",
            "segons districtes": "Nom_Districte",
            "por barrio": "Nom_Barri",
            "por barrios": "Nom_Barri",
            "segun barrio": "Nom_Barri",
            "segun barrios": "Nom_Barri",
            "per barri": "Nom_Barri",
            "per barris": "Nom_Barri",
            "segons barri": "Nom_Barri",
            "segons barris": "Nom_Barri",
            "por codigo de barrio": "Codi_Barri",
            "por codi de barri": "Codi_Barri",
            "por codigo de distrito": "Codi_Districte",
            "por codi de districte": "Codi_Districte",
            "por titularidad": "Titularitat",
            "segun titularidad": "Titularitat",
            "por ambit": "Ambit",
            "por ambito": "Ambit",
        }
        for alias, column in sorted(group_aliases.items(), key=lambda item: len(item[0]), reverse=True):
            if alias in normalized_question:
                return column
        return None

    def format_number(self, value: float) -> str:
        if value.is_integer():
            return f"{int(value):,}".replace(",", ".")
        return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def column_label(self, column: str) -> str:
        labels = {
            "Any": "any",
            "Indicador": "indicador",
            "Nom_Equipament": "biblioteca",
            "Valor": "valor",
            "Notes_Dades": "notes de dades",
            "Notes_Equipament": "notes d'equipament",
            "Codi_Districte": "codi de districte",
            "Nom_Districte": "districte",
            "Codi_Barri": "codi de barri",
            "Nom_Barri": "barri",
            "Titularitat": "titularitat",
            "Tipus_Us": "tipus d'ús",
            "Tipus_Equipament": "tipus d'equipament",
            "Ambit": "àmbit",
            "Latitud": "latitud",
            "Longitud": "longitud",
        }
        return labels.get(column, column.replace("_", " "))

    def sum_indicator(self, indicator: str) -> str:
        total = sum(value for _, value, _ in self.by_indicator[indicator])
        return f"El total acumulat de {indicator} durant el 2024 és {self.format_number(total)}."

    def average_indicator(self, indicator: str) -> str:
        values = [value for _, value, _ in self.by_indicator[indicator]]
        average = sum(values) / len(values)
        return (
            f"La mitjana de {indicator} entre les {len(values)} biblioteques "
            f"analitzades és {self.format_number(average)}."
        )

    def max_indicator(self, indicator: str) -> str:
        library, value, row = max(self.by_indicator[indicator], key=lambda item: item[1])
        district = row.get("Nom_Districte", "districte no indicat")
        return (
            f"La biblioteca amb el valor més alt en {indicator} és {library}, "
            f"al districte de {district}, amb {self.format_number(value)}."
        )

    def min_indicator(self, indicator: str) -> str:
        library, value, row = min(self.by_indicator[indicator], key=lambda item: item[1])
        district = row.get("Nom_Districte", "districte no indicat")
        return (
            f"La biblioteca amb el valor més baix en {indicator} és {library}, "
            f"al districte de {district}, amb {self.format_number(value)}."
        )

    def top_indicator(self, indicator: str, limit: int = 5, reverse: bool = True) -> str:
        ordered = sorted(self.by_indicator[indicator], key=lambda item: item[1], reverse=reverse)
        selected = ordered[:limit]
        direction = "més alts" if reverse else "més baixos"
        lines = [
            f"{index}. {library}: {self.format_number(value)}"
            for index, (library, value, _) in enumerate(selected, start=1)
        ]
        return f"Top {len(selected)} amb valors {direction} en {indicator}:\n" + "\n".join(lines)

    def compare_loans(self) -> str:
        best = None
        for library, values in self.by_library.items():
            presencial = values.get("Prestecs_presencials", 0.0)
            virtual = values.get("Prestecs_virtuals", 0.0)
            difference = presencial - virtual
            if best is None or difference > best["difference"]:
                best = {
                    "library": library,
                    "presencial": presencial,
                    "virtual": virtual,
                    "difference": difference,
                }

        if best is None:
            return "No hi ha dades suficients per comparar préstecs presencials i virtuals."

        return (
            f"La diferència més gran de préstecs presencials respecte dels virtuals la té "
            f"{best['library']}: {self.format_number(best['presencial'])} presencials "
            f"i {self.format_number(best['virtual'])} virtuals "
            f"(diferència de {self.format_number(best['difference'])})."
        )

    def unique_column_values(self, column: str) -> str:
        values = sorted({row[column] for row in self.rows if row.get(column)})
        label = self.column_label(column)
        if not values:
            return f"No hi ha valors disponibles per a {label}."

        if column == "Codi_Barri":
            pairs = sorted({
                (row["Codi_Barri"], row["Nom_Barri"])
                for row in self.rows
                if row.get("Codi_Barri") and row.get("Nom_Barri")
            })
            rendered = ", ".join(f"{code} - {name}" for code, name in pairs)
            return f"Hi ha {len(pairs)} codis de barri únics: {rendered}."

        if column == "Codi_Districte":
            pairs = sorted({
                (row["Codi_Districte"], row["Nom_Districte"])
                for row in self.rows
                if row.get("Codi_Districte") and row.get("Nom_Districte")
            })
            rendered = ", ".join(f"{code} - {name}" for code, name in pairs)
            return f"Hi ha {len(pairs)} codis de districte únics: {rendered}."

        preview = ", ".join(values[:30])
        if len(values) > 30:
            preview += f" ... i {len(values) - 30} més"
        return f"Hi ha {len(values)} valors únics a {label}: {preview}."

    def count_libraries_by_column(self, column: str) -> str:
        groups = defaultdict(set)
        for row in self.rows:
            group = row.get(column) or "Sense dada"
            groups[group].add(row["Nom_Equipament"])

        ordered = sorted(groups.items(), key=lambda item: (-len(item[1]), item[0]))
        label = self.column_label(column)
        lines = [
            f"{group}: {len(libraries)}"
            for group, libraries in ordered
        ]
        return f"Quantitat de biblioteques úniques per {label}:\n" + "\n".join(lines)

    def aggregate_indicator_by_column(self, indicator: str, column: str, operation: str) -> str:
        groups = defaultdict(list)
        for library, value, row in self.by_indicator[indicator]:
            group = row.get(column) or "Sense dada"
            groups[group].append(value)

        results = []
        for group, values in groups.items():
            if operation == "promedio":
                result = sum(values) / len(values)
            else:
                result = sum(values)
            results.append((group, result))

        results.sort(key=lambda item: item[1], reverse=True)
        label = self.column_label(column)
        title = "Mitjana" if operation == "promedio" else "Total"
        lines = [
            f"{group}: {self.format_number(value)}"
            for group, value in results
        ]
        return f"{title} de {indicator} per {label}:\n" + "\n".join(lines)

    def library_profile(self, library: str) -> str:
        base_row = next(row for row in self.rows if row["Nom_Equipament"] == library)
        values = self.by_library[library]
        metrics = [
            f"{indicator}: {self.format_number(value)}"
            for indicator, value in sorted(values.items())
        ]
        return (
            f"{library} és al districte de {base_row['Nom_Districte']}, barri {base_row['Nom_Barri']} "
            f"(codi {base_row['Codi_Barri']}). Indicadors 2024:\n"
            + "\n".join(metrics)
        )

    def extract_limit(self, question: str, default: int = 5) -> int:
        match = re.search(r"\btop\s+(\d+)\b|\b(\d+)\s+(primer|mejor|mayor|menor)", normalize(question))
        if not match:
            return default
        number = match.group(1) or match.group(2)
        return max(1, min(int(number), 20))

    def is_count_question(self, normalized_question: str) -> bool:
        count_words = [
            "cantidad", "cuantas", "cuantos", "numero", "nombre", "conteo", "contar", "hay",
            "quantitat", "quantes", "quants", "recompte", "comptar", "hi ha",
        ]
        subject_words = ["biblioteca", "bibliotecas", "biblioteques", "equipamientos", "equipaments"]
        return any(word in normalized_question for word in count_words) and any(
            word in normalized_question for word in subject_words
        )

    def dataset_summary(self) -> str:
        return (
            f"El fitxer conté {len(self.rows)} registres, "
            f"{len(self.libraries)} biblioteques úniques i {len(self.indicators)} indicadors: "
            f"{', '.join(self.indicators)}."
        )

    def narrative_report(self) -> str:
        visits = sum(value for _, value, _ in self.by_indicator["Visites"])
        meters = [value for _, value, _ in self.by_indicator["Metres_Quadrats"]]
        top_visits_library, top_visits, _ = max(self.by_indicator["Visites"], key=lambda item: item[1])
        return (
            "Informe breu: durant el 2024, les biblioteques analitzades de Barcelona "
            f"van acumular {self.format_number(visits)} visites. El conjunt inclou "
            f"{len(self.libraries)} biblioteques úniques i una superfície mitjana de "
            f"{self.format_number(sum(meters) / len(meters))} metres quadrats. "
            f"La biblioteca amb més visites va ser {top_visits_library}, amb "
            f"{self.format_number(top_visits)} visites registrades."
        )

    def help_text(self) -> str:
        examples = [
            "Quin és el total de Visites?",
            "Quina és la mitjana de Metres_Quadrats?",
            "Quantes biblioteques hi ha per districte?",
            "Total de visites per districte.",
            "Top 5 biblioteques per préstecs presencials.",
            "Dona'm les dades de Biblioteca Jaume Fuster.",
            "Quina biblioteca té més Prestecs_presencials?",
            "Compara Prestecs_presencials amb Prestecs_virtuals.",
        ]
        return (
            "Em pots preguntar per totals, mitjanes, màxims, mínims, rànquings, "
            "recomptes per districte o barri i fitxes de biblioteques. Exemples: "
            + " ".join(examples)
        )

    def answer(self, question: str) -> dict[str, str]:
        clean_question = question.strip()
        normalized_question = normalize(clean_question)

        if not clean_question:
            return {"answer": "Escriu una pregunta sobre les dades de biblioteques de Barcelona 2024."}

        if any(word in normalized_question for word in ["ayuda", "help", "ejemplos", "que puedes", "ajuda", "exemples", "que pots"]):
            return {"answer": self.help_text()}

        if any(word in normalized_question for word in ["genera", "redacta", "informe", "texto", "text"]):
            return {"answer": self.narrative_report()}

        if any(word in normalized_question for word in ["resumen", "describe", "descripcion", "base de datos", "resum", "descripcio", "base de dades"]):
            return {"answer": self.dataset_summary()}

        if any(word in normalized_question for word in ["columnas", "campos", "variables", "columnes", "camps"]):
            return {"answer": f"Les columnes del CSV són: {', '.join(self.columns)}."}

        if "bibliotecas unicas" in normalized_question or "biblioteques uniques" in normalized_question:
            return {"answer": f"Hi ha {len(self.libraries)} biblioteques úniques registrades al fitxer."}

        if "prestecs_presencials" in normalized_question and "prestecs_virtuals" in normalized_question:
            return {"answer": self.compare_loans()}
        if "presencial" in normalized_question and "virtual" in normalized_question:
            return {"answer": self.compare_loans()}

        group_column = self.group_column_from_question(clean_question)
        if group_column and self.is_count_question(normalized_question):
            return {"answer": self.count_libraries_by_column(group_column)}

        library = self.mentioned_library(clean_question)
        if library and any(word in normalized_question for word in ["datos", "info", "informacion", "ficha", "perfil", "dades", "fitxa"]):
            return {"answer": self.library_profile(library)}

        indicator = self.indicator_from_question(clean_question)
        if indicator:
            if group_column:
                operation = "promedio" if any(
                    word in normalized_question for word in ["promedio", "media", "mitjana", "average"]
                ) else "total"
                return {"answer": self.aggregate_indicator_by_column(indicator, group_column, operation)}
            if "top" in normalized_question or re.search(r"\b\d+\s+(primer|mejor|mayor|menor)", normalized_question):
                reverse = not any(word in normalized_question for word in ["menor", "minimo", "minima", "menos", "baix", "baixa", "menys"])
                return {"answer": self.top_indicator(indicator, self.extract_limit(clean_question), reverse)}
            if any(word in normalized_question for word in ["promedio", "media", "mitjana", "average"]):
                return {"answer": self.average_indicator(indicator)}
            if any(word in normalized_question for word in ["mayor", "maximo", "maxima", "mas", "top", "mes", "maxim", "maxima", "alt", "alta"]):
                return {"answer": self.max_indicator(indicator)}
            if any(word in normalized_question for word in ["menor", "minimo", "minima", "menos", "minim", "minima", "baix", "baixa", "menys"]):
                return {"answer": self.min_indicator(indicator)}
            if any(word in normalized_question for word in ["total", "suma", "acumulad", "acumulat"]):
                return {"answer": self.sum_indicator(indicator)}
            return {
                "answer": (
                    f"He trobat l'indicador {indicator}. Em pots demanar el total, "
                    "la mitjana, el màxim o el mínim."
                )
            }

        column = self.column_from_question(clean_question)
        if column:
            return {"answer": self.unique_column_values(column)}

        return {
            "answer": (
                "No he pogut identificar quina dada del CSV vols consultar. "
                f"Indicadors disponibles: {', '.join(self.indicators)}. "
                f"Columnes disponibles: {', '.join(self.columns)}."
            )
        }


DATA = LibraryData(CSV_PATH)


class AssistantHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def do_POST(self) -> None:
        parsed_path = urlparse(self.path)
        if parsed_path.path != "/api/ask":
            self.send_error(404, "Ruta no trobada")
            return

        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length)

        try:
            payload = json.loads(raw_body.decode("utf-8"))
            question = payload.get("question", "")
            response = DATA.answer(question)
            self._send_json(response)
        except json.JSONDecodeError:
            self._send_json({"answer": "La petició no té un JSON vàlid."}, status=400)

    def _send_json(self, payload: dict[str, str], status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run() -> None:
    server = None
    port = PORT
    for candidate_port in range(PORT, PORT + 20):
        try:
            server = ThreadingHTTPServer((HOST, candidate_port), AssistantHandler)
            port = candidate_port
            break
        except OSError:
            continue

    if server is None:
        raise OSError("No s'ha trobat cap port lliure entre 8000 i 8019.")

    url = f"http://{HOST}:{port}"
    print(f"Assistent iniciat a {url}")
    print("Prem Ctrl+C per aturar el servidor.")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor aturat.")
    finally:
        server.server_close()


if __name__ == "__main__":
    run()
