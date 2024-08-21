let materias = [];

const listarMaterias = async (codcarrera, dificultad = '') => {
    try {
        const response = await fetch(`./materiasf/${codcarrera}?dificultad=${dificultad}`);
        const data = await response.json();
        checkboxContainer.innerHTML = "";
        if (data.message === "Success") {
            //const semestres = ["Primero", "Segundo"];
            //const cursos = ["Primero", "Segundo","Tercero","Cuarto","Quinto"]
            const datamateria = {
                semestres: ["Primero", "Segundo"],
                cursos: ["Primero", "Segundo","Tercero","Cuarto","Quinto"]
            };

            datamateria.cursos.forEach(curso=> {
                const divCurso = document.createElement('div');
                divCurso.id = 'div-curso';
                const divsemestre = document.createElement('div');
                divsemestre.id = 'div-semestre';
                const hr = document.createElement('hr')
                checkboxContainer.appendChild(divCurso);
                const legendcurso = document.createElement('legend');
                legendcurso.textContent = `Curso: ${curso}`
                divCurso.appendChild(legendcurso)
                divCurso.appendChild(hr)
                divCurso.appendChild(divsemestre)
                
                
                datamateria.semestres.forEach(semestre =>{                              
                // Filtrar las materias por cada semestre
                //const materiasSemestre = data.materias.filter(materia => materia.semestre === semestre);
                const materiasCursoSemestre = data.materias.filter(materia => materia.curso === curso  && materia.semestre === semestre);
                console.log(materiasCursoSemestre);

                let checkboxes = ``;
                materiasCursoSemestre.forEach((materia) => {
                    checkboxes += `
                            <tr>
                                    <td><input class="form-check-input" type="checkbox" id="materia${materia.id}" name="pdf_id" value="${materia.id}"></td>
                                    <td>${materia.codigo}</td>
                                    <td><label class="form-check-label" for="materia${materia.id}">${materia.materia}</label></td>
                                    <!-- Añadido campo de dificultad -->
                                    <td>${materia.dificultad || 'No especificado'}</td> 
                            </tr>
                    `;
                });
                //const divcursoxd = createElement('div');
                //divcursoxd.id = 'div-curso';
                //checkboxContainer.appendChild(divcursoxd);

                const divContenedor = document.createElement('div');
                divContenedor.id = 'div-materias';

                // Agregar fieldset con leyenda correspondiente al semestre
                const hr = document.createElement('hr');
                const table = document.createElement('table');
                table.className = 'table table-hover';
                const thead = document.createElement('thead');
                const trhead = document.createElement('tr');
                const tdheadmateria = document.createElement('th');
                tdheadmateria.textContent = 'Materia';
                const tdheadcodigo = document.createElement('th');
                tdheadcodigo.textContent = 'Código';
                //dificultad
                const tdheaddificultad = document.createElement('th');
                tdheaddificultad.textContent = 'Dificultad';

                const tdheadinput = document.createElement('td');
                const checkhead = `<input class="form-check-input" type="checkbox" id="id="checkGeneral-${curso}-${semestre}" onclick="toggleCheckboxes(this,'${curso}', '${semestre}')">`;
                tdheadinput.innerHTML = checkhead;
                const tbody = document.createElement('tbody');
                tbody.className = 'table-group-divider'; 
                const fieldset = document.createElement('fieldset');
                const legendsemestre = document.createElement('legend');
                
                legendsemestre.textContent = `Semestre: ${semestre} `;
                
                fieldset.appendChild(legendsemestre);
                fieldset.appendChild(hr);
                fieldset.appendChild(table);
                table.appendChild(thead);
                thead.appendChild(trhead);
                trhead.appendChild(tdheadinput);
                trhead.appendChild(tdheadcodigo);
                trhead.appendChild(tdheadmateria);
                trhead.appendChild(tdheaddificultad);
                table.appendChild(tbody);
                tbody.innerHTML += checkboxes;
                //fieldset.innerHTML += checkboxes;
                divContenedor.appendChild(fieldset);

                // Agregar el div contenedor al contenedor principal
                divsemestre.appendChild(divContenedor);
                })
            });
        } else {
            alert("Materias no encontradas...");
        }
    } catch (error) {
        console.log(error);
    }
};
const mostrarTablaAutoridades = async () => {
    try {
        const response = await fetch("listar-autoridades/");
        const data = await response.json();
        console.log(data);

        if (data.message === "Success") {
            let opciones = ``;
            data.autoridades.forEach((autoridad) => {
                opciones += `
                    <tr>
                        <td >${autoridad.nombreApellido}</td>
                        <td >${autoridad.cargo}</td>
                        <td class="text-center">
                            <button type="button" class="btn btn-primary btn-editarAutoridad"
                                    data-autoridadEdit-id="${autoridad.id}"
                                    data-bs-toggle="modal" data-bs-target="#editarAutoridadModal">
                                <i class="bi bi-pencil-square"></i>
                            </button>
                        </td>
                    </tr>`;
            });

            document.getElementById('tableAutoridades').innerHTML = opciones;
            const botonesEditarAutoridad = document.querySelectorAll('.btn-editarAutoridad');
            botonesEditarAutoridad.forEach(boton => {
                boton.addEventListener('click', async () => {
                    const autoridadIdEdit = boton.getAttribute('data-autoridadEdit-id');
                    // Llamar a función para obtener y prellenar datos del evento en el modal
                    await obtenerYMostrarDatosAutoridad(autoridadIdEdit);
                });
            });
        } else if (data.message === "Not Found") {
            document.getElementById('tableAutoridades').innerHTML = `
                <tr>
                    <td colspan="3" class="text-center">No hay datos</td>
                </tr>`;
        } else {
            alert("Error al obtener los datos");
        }
    } catch (error) {
        console.log(error);
        //alert("Ocurrió un error al procesar la solicitud");
    }
};

const obtenerYMostrarDatosAutoridad = async (autoridadIdEdit) => {
    try {
        const response = await fetch(`obtener-autoridad/${autoridadIdEdit}/`);
        const data = await response.json();
        console.log(data)

        if (data.message === 'Success') {
            const autoridad = data.autoridad;

            // Preencher el modal de editar con los datos obtenidos
            document.getElementById('autoridad-id-editar').value = autoridad.id
            document.getElementById('inputAutoridadEdit').value = autoridad.nombre_autoridad;
            // Aquí puedes añadir más campos del formulario según sea necesario
        } else {
            alert('Error al obtener datos del evento');
        }
    } catch (error) {
        console.error('Error al obtener datos del evento:', error);
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Busca la cookie con el nombre 'csrftoken'
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

document.addEventListener('DOMContentLoaded', function() {
    const btnEditar = document.getElementById('btn-editarAutoridad');
    if (btnEditar) {
        btnEditar.addEventListener('click', async function () {
            const autoridadId = document.getElementById('autoridad-id-editar').value;
            const nombreAutoridad = document.getElementById('inputAutoridadEdit').value;

            const data = {
                id: autoridadId,
                nombreAutoridad: nombreAutoridad,
            };
            if (nombreAutoridad.trim() === '') {
                const toastEl = document.getElementById('liveToast');
                const toast = new bootstrap.Toast(toastEl);
                toast.show();
                return; // Detiene el envío si el campo está vacío
            }
            //console.log(data); // Verifica que los datos sean correctos

            try {
                const response = await fetch('editar-autoridad/', {
                    method: 'POST',
                    body: JSON.stringify(data),
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken 
                    }
                });

                if (response.ok) {
                    const result = await response.json();
                    if (result.message === 'Success') {
                        await mostrarTablaAutoridades(); // Asegúrate de que esta función esté definida
                        $('#editarAutoridadModal').modal('hide');
                    } else {
                        console.log("Error al modificar");
                    }
                } else {
                    throw new Error('Error al actualizar la autoridad');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error al actualizar la autoridad');
            }
        });
    } else {
        console.error('No se encontró el botón de edición');
    }
});
const cargaInicial = async () => {
    await mostrarTablaAutoridades();

    const cboCarrera = document.getElementById('cboCarrera');
    if (cboCarrera) {
        listarMaterias('KTII');
        cboCarrera.addEventListener("change", (event) => {
            listarMaterias(event.target.value);
        });
    } else {
        console.log('No se encontró el elemento cboCarrera');
    }

};
window.addEventListener("load", cargaInicial);