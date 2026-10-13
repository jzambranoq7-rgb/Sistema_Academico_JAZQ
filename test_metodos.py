import os
from models import Estudiante, Materia, Matricula
from views import EstudianteController, MateriaController, MatriculaController


def limpiar_archivos_prueba():
    for ruta in ("data/estudiantes.json", "data/materias.json", "data/matriculas.json"):
        if os.path.exists(ruta):
            os.remove(ruta)


def ejecutar_pruebas():
    limpiar_archivos_prueba()

    # 1. Modelos, herencia y polimorfismo
    est_modelo = Estudiante(1, "Carlos", "Vera", "carlos@u.edu", "EST001", "Software")
    mat_modelo = Materia(1, "Estructuras de Datos", "EDD101", 4, 30)
    ins_modelo = Matricula(1, 1, 1, "2026-1", 16.5)

    assert hasattr(est_modelo, "id") and hasattr(est_modelo, "nombre")
    assert est_modelo.nombre_completo() == "Carlos Vera"
    assert "EST001" in est_modelo.etiqueta()
    assert "EDD101" in mat_modelo.etiqueta()
    assert ins_modelo.esta_aprobada() is True
    assert ins_modelo.estado() == "Aprobado"

    # 2. Métodos estáticos y de clase
    assert Materia.es_nota_valida(18) is True
    assert Materia.es_nota_valida(25) is False
    assert Materia.es_nota_valida("abc") is False

    datos_dic = {"id": 2, "nombre": "Física I", "codigo": "FIS101", "creditos": 3, "cupos": 25}
    obj_materia = Materia.desde_diccionario(datos_dic)
    assert isinstance(obj_materia, Materia)
    assert obj_materia.codigo == "FIS101"

    # 3. EstudianteController
    ctrl_estudiantes = EstudianteController("data/estudiantes.json")

    ok, msg = ctrl_estudiantes.crear({
        "nombre": "Ana",
        "apellido": "Rios",
        "email": "ana@u.edu",
        "carnet": "EST001",
        "carrera": "Software"
    })
    assert ok is True

    ok_dup, _ = ctrl_estudiantes.crear({
        "nombre": "Luis",
        "apellido": "Mora",
        "email": "luis@u.edu",
        "carnet": "EST001",
        "carrera": "Redes"
    })
    assert ok_dup is False

    ok_email, _ = ctrl_estudiantes.crear({
        "nombre": "Luis",
        "apellido": "Mora",
        "email": "ana@u.edu",
        "carnet": "EST002",
        "carrera": "Redes"
    })
    assert ok_email is False

    ctrl_estudiantes.crear({
        "nombre": "Luis",
        "apellido": "Mora",
        "email": "luis@u.edu",
        "carnet": "EST002",
        "carrera": "Redes"
    })

    assert len(ctrl_estudiantes.leer()) == 2
    assert ctrl_estudiantes.obtener(1).nombre == "Ana"
    assert len(ctrl_estudiantes.buscar("software")) == 1
    assert "Software" in ctrl_estudiantes.carreras()

    # 4. MateriaController
    ctrl_materias = MateriaController("data/materias.json")

    ok_mat, _ = ctrl_materias.crear({
        "nombre": "Algoritmos",
        "codigo": "ALG101",
        "creditos": 4,
        "cupos": 1
    })
    assert ok_mat is True

    ok_mat_dup, _ = ctrl_materias.crear({
        "nombre": "Algoritmos Avanzados",
        "codigo": "ALG101",
        "creditos": 3,
        "cupos": 10
    })
    assert ok_mat_dup is False

    materia_creada = ctrl_materias.obtener(1)
    assert materia_creada.cupos == 1
    assert materia_creada.hay_cupo() is True

    # 5. MatriculaController
    ctrl_matriculas = MatriculaController(ctrl_estudiantes, ctrl_materias, "data/matriculas.json")

    ok_ins, _ = ctrl_matriculas.crear({
        "estudiante_id": 1,
        "materia_id": 1,
        "periodo": "2026-1"
    })
    assert ok_ins is True

    assert ctrl_materias.obtener(1).cupos == 0
    assert len(ctrl_materias.materias_sin_cupo()) == 1

    ok_sin_cupo, msg_sin_cupo = ctrl_matriculas.crear({
        "estudiante_id": 2,
        "materia_id": 1,
        "periodo": "2026-1"
    })
    assert ok_sin_cupo is False
    assert "cupo" in msg_sin_cupo.lower()

    ctrl_materias.obtener(1).cupos = 5
    ok_doble, _ = ctrl_matriculas.crear({
        "estudiante_id": 1,
        "materia_id": 1,
        "periodo": "2026-1"
    })
    assert ok_doble is False

    ctrl_matriculas.registrar_nota(1, 15.5)
    matricula = ctrl_matriculas.obtener(1)
    assert matricula.nota == 15.5
    assert matricula.esta_aprobada() is True
    assert ctrl_matriculas.total_aprobadas() == 1

    texto_cert = ctrl_matriculas.certificado(1)
    assert "Ana Rios" in texto_cert
    assert "ALG101" in texto_cert
    assert "Aprobado" in texto_cert

    ok_ret, _ = ctrl_matriculas.eliminar(1)
    assert ok_ret is True
    assert len(ctrl_matriculas.leer()) == 0

    print("TODAS LAS PRUEBAS PASARON EXITOSAMENTE")


if __name__ == "__main__":
    ejecutar_pruebas()