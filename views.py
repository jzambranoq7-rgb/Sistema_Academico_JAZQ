from abc import ABC, abstractmethod

from models import Estudiante, Materia, Matricula
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido


class CrudBase(ABC):
    @abstractmethod
    def leer(self):
        pass

    @abstractmethod
    def obtener(self, id_registro):
        pass

    @abstractmethod
    def buscar(self, texto):
        pass

    @abstractmethod
    def siguiente(self):
        pass

    @abstractmethod
    def crear(self, datos):
        pass

    @abstractmethod
    def actualizar(self, id_registro, datos):
        pass

    @abstractmethod
    def eliminar(self, id_registro):
        pass


class EstudianteController(CrudBase):
    def __init__(self, archivo="data/estudiantes.json"):
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Estudiante.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for est in self.lista:
            datos.append(est.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            for campo in ("nombre", "apellido", "email", "carnet"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            if not es_email_valido(email):
                return f"Email inválido: '{email}'"
            usados = {e.email for e in self.lista if e.id != id_actual}
            if email in usados:
                return "Ese email ya está registrado"

        if "carnet" in datos:
            carnet = str(datos["carnet"]).strip().upper()
            carnets = {e.carnet for e in self.lista if e.id != id_actual}
            if carnet in carnets:
                return f"El carnet '{carnet}' ya está registrado"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_estudiante):
        for est in self.lista:
            if est.id == id_estudiante:
                return est
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for est in self.lista:
            if (texto in est.nombre.lower()
                    or texto in est.apellido.lower()
                    or texto in est.email.lower()
                    or texto in est.carnet.lower()
                    or texto in est.carrera.lower()):
                encontrados.append(est)
        return encontrados

    def siguiente(self):
        mayor = 0
        for est in self.lista:
            if est.id > mayor:
                mayor = est.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        est = Estudiante(
            self.siguiente(),
            str(datos["nombre"]).strip().title(),
            str(datos["apellido"]).strip().title(),
            str(datos["email"]).strip().lower(),
            str(datos["carnet"]).strip().upper(),
            str(datos.get("carrera", "")).strip().title()
        )
        self.lista.append(est)
        self.guardar()
        return True, f"Estudiante creado: {est.etiqueta()}"

    def actualizar(self, id_estudiante, datos):
        est = self.obtener(id_estudiante)
        if est is None:
            return False, f"No existe un estudiante con id {id_estudiante}"
        if not datos:
            return False, "No se indicó ningún cambio"

        permitidos = {"nombre", "apellido", "email", "carnet", "carrera"}
        desconocidos = set(datos) - permitidos
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_estudiante)
        if error:
            return False, error

        for campo, valor in datos.items():
            valor = str(valor).strip()
            if campo in ("nombre", "apellido", "carrera"):
                valor = valor.title()
            elif campo == "email":
                valor = valor.lower()
            elif campo == "carnet":
                valor = valor.upper()
            setattr(est, campo, valor)

        self.guardar()
        return True, f"Estudiante {id_estudiante} actualizado"

    def eliminar(self, id_estudiante):
        est = self.obtener(id_estudiante)
        if est is None:
            return False, f"No existe un estudiante con id {id_estudiante}"
        self.lista.remove(est)
        self.guardar()
        return True, f"Estudiante {id_estudiante} eliminado"

    def carreras(self):
        return sorted({e.carrera for e in self.lista if e.carrera != ""})


class MateriaController(CrudBase):
    def __init__(self, archivo="data/materias.json"):
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Materia.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for mat in self.lista:
            datos.append(mat.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            for campo in ("nombre", "codigo", "creditos"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "codigo" in datos:
            codigo = str(datos["codigo"]).strip().upper()
            codigos = {m.codigo for m in self.lista if m.id != id_actual}
            if codigo in codigos:
                return f"El código '{codigo}' ya existe"

        if "creditos" in datos:
            try:
                cred = int(datos["creditos"])
                if not (1 <= cred <= 10):
                    return "Los créditos deben estar entre 1 y 10"
            except (ValueError, TypeError):
                return "Los créditos deben ser un número entero"

        if "cupos" in datos:
            try:
                cupos = int(datos["cupos"])
                if not (0 <= cupos <= Materia.CUPOS_MAXIMOS):
                    return f"Los cupos deben estar entre 0 y {Materia.CUPOS_MAXIMOS}"
            except (ValueError, TypeError):
                return "Los cupos deben ser un número entero"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_materia):
        for mat in self.lista:
            if mat.id == id_materia:
                return mat
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for mat in self.lista:
            if texto in mat.nombre.lower() or texto in mat.codigo.lower():
                encontrados.append(mat)
        return encontrados

    def siguiente(self):
        mayor = 0
        for mat in self.lista:
            if mat.id > mayor:
                mayor = mat.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        cupos = str(datos.get("cupos", "")).strip()
        materia = Materia(
            self.siguiente(),
            str(datos["nombre"]).strip().title(),
            str(datos["codigo"]).strip().upper(),
            int(datos["creditos"]),
            int(cupos) if cupos != "" else Materia.CUPOS_MAXIMOS
        )
        self.lista.append(materia)
        self.guardar()
        return True, f"Materia creada: {materia.etiqueta()}"

    def actualizar(self, id_materia, datos):
        mat = self.obtener(id_materia)
        if mat is None:
            return False, f"No existe una materia con id {id_materia}"
        if not datos:
            return False, "No se indicó ningún cambio"

        desconocidos = set(datos) - {"nombre", "codigo", "creditos", "cupos"}
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_materia)
        if error:
            return False, error

        if "nombre" in datos:
            mat.nombre = str(datos["nombre"]).strip().title()
        if "codigo" in datos:
            mat.codigo = str(datos["codigo"]).strip().upper()
        if "creditos" in datos:
            mat.creditos = int(datos["creditos"])
        if "cupos" in datos:
            mat.cupos = int(datos["cupos"])

        self.guardar()
        return True, f"Materia {id_materia} actualizada"

    def eliminar(self, id_materia):
        mat = self.obtener(id_materia)
        if mat is None:
            return False, f"No existe una materia con id {id_materia}"
        self.lista.remove(mat)
        self.guardar()
        return True, f"Materia {id_materia} eliminada"

    def materias_sin_cupo(self):
        return [m for m in self.lista if not m.hay_cupo()]


class MatriculaController(CrudBase):
    def __init__(self, estudiantes, materias, archivo="data/matriculas.json"):
        self.estudiantes = estudiantes
        self.materias = materias
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Matricula.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for m in self.lista:
            datos.append(m.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos):
        try:
            est_id = int(datos.get("estudiante_id", 0))
            mat_id = int(datos.get("materia_id", 0))
            periodo = str(datos.get("periodo", "")).strip()
        except (TypeError, ValueError):
            return "estudiante_id y materia_id deben ser números enteros"

        if not periodo:
            return "El periodo es obligatorio"

        if self.estudiantes.obtener(est_id) is None:
            return f"No existe un estudiante con id {est_id}"

        materia = self.materias.obtener(mat_id)
        if materia is None:
            return f"No existe una materia con id {mat_id}"
        if not materia.hay_cupo():
            return f"No hay cupos disponibles en {materia.nombre}"

        for reg in self.lista:
            if reg.estudiante_id == est_id and reg.materia_id == mat_id and reg.periodo == periodo:
                return f"El estudiante ya está matriculado en esta materia en el periodo {periodo}"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_matricula):
        for m in self.lista:
            if m.id == id_matricula:
                return m
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontradas = []
        if texto == "":
            return encontradas

        for m in self.lista:
            if texto in m.periodo.lower() or texto in m.fecha:
                encontradas.append(m)
        return encontradas

    def siguiente(self):
        mayor = 0
        for m in self.lista:
            if m.id > mayor:
                mayor = m.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        materia = self.materias.obtener(int(datos["materia_id"]))
        matricula = Matricula(
            self.siguiente(),
            int(datos["estudiante_id"]),
            materia.id,
            str(datos["periodo"]).strip(),
            nota=0.0
        )
        materia.ocupar_cupo()
        self.materias.guardar()
        self.lista.append(matricula)
        self.guardar()
        return True, f"Matrícula {matricula.id} registrada con éxito"

    def actualizar(self, id_matricula, datos):
        return False, "La matrícula no se puede editar directamente: retírela o registre su nota"

    def registrar_nota(self, id_matricula, nota):
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return False, f"No existe la matrícula {id_matricula}"

        if not Materia.es_nota_valida(nota):
            return False, "La nota debe ser un número entre 0 y 20"

        matricula.nota = float(nota)
        self.guardar()
        return True, f"Nota {nota} asignada a la matrícula {id_matricula} ({matricula.estado()})"

    def eliminar(self, id_matricula):
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return False, f"No existe la matrícula {id_matricula}"

        materia = self.materias.obtener(matricula.materia_id)
        if materia is not None:
            materia.liberar_cupo()
            self.materias.guardar()

        self.lista.remove(matricula)
        self.guardar()
        return True, f"Matrícula {id_matricula} retirada y cupo liberado"

    def certificado(self, id_matricula):
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return None

        estudiante = self.estudiantes.obtener(matricula.estudiante_id)
        materia = self.materias.obtener(matricula.materia_id)

        texto = f"CERTIFICADO #{matricula.id}   periodo: {matricula.periodo}\n"
        texto += f"Estudiante: {estudiante.nombre_completo() if estudiante else 'eliminado'} ({estudiante.carnet if estudiante else '-'})\n"
        texto += f"Materia   : {materia.nombre if materia else 'eliminada'} ({materia.codigo if materia else '-'}) · {materia.creditos if materia else 0} créditos\n"
        texto += "-" * 42 + "\n"
        texto += f"Nota      : {matricula.nota}\n"
        texto += f"Estado    : {matricula.estado()}"
        return texto

    def matriculas_por_estudiante(self):
        agrupadas = {}
        for m in self.lista:
            agrupadas.setdefault(m.estudiante_id, []).append(m)
        return agrupadas

    def total_aprobadas(self):
        return sum(1 for m in self.lista if m.esta_aprobada())