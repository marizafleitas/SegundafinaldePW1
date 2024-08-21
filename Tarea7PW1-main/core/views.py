import pdfplumber
from django.shortcuts import render, redirect, get_object_or_404
from .models import PDF, Carrera, Autoridades
from io import BytesIO
from unidecode import unidecode
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
import json
from django.views.decorators.csrf import csrf_exempt
import re
from django.shortcuts import render, redirect
from .models import PDF

def import_success(request):
    return render(request, 'import_success.html')

def asignar_dificultad(request):
    materias = PDF.objects.all().values_list('materia', flat=True).distinct()
    
    if request.method == 'POST':
        materia_seleccionada = request.POST.get('materia')
        nueva_dificultad = request.POST.get('dificultad')
        
        # Filtrar todos los registros que coincidan con la materia seleccionada y actualizar la dificultad
        PDF.objects.filter(materia=materia_seleccionada).update(dificultad=nueva_dificultad)

        return redirect('asignar_dificultad')  # Redirige para que la página se recargue
    
    return render(request, 'asignar_dificultad.html', {'materias': materias})


def carrera_pdf_list(request):
    carreras = Carrera.objects.all()
    pdfs = PDF.objects.none()
    selected_carrera_id = request.GET.get('id_carrera')
    selected_dificultad = request.GET.get('dificultad')

    if selected_carrera_id:
        selected_carrera = Carrera.objects.get(pk=selected_carrera_id)
        pdfs = PDF.objects.filter(id_carrera=selected_carrera)
 # Aplicar filtro por dificultad si existe******************************
        if selected_dificultad: 
         pdfs = pdfs.filter(dificultad=selected_dificultad)

    return render(request, 'carrera_pdf_list.html',
                  {'carreras': carreras, 'pdfs': pdfs, 'selected_carrera_id': selected_carrera_id})

def listar_autoridades(request):
    autoridades = Autoridades.objects.all()
    print(autoridades)
    if autoridades.exists():
        autoridades_list = list(autoridades.values())  # Serializa el QuerySet a una lista de diccionarios
        data = {'message': "Success", 'autoridades': autoridades_list}
    else:
        data = {'message': "Not Found"}
    return JsonResponse(data)

def autoridades(request):
    return render(request,'autoridades.html')

def obtener_autoridad(request, autoridad_id):
    try:
        autoridad = get_object_or_404(Autoridades, id=autoridad_id)

        # Preparar los datos del evento para enviar como respuesta JSON
        data = {
            'message': 'Success',
            'autoridad': {
                'id': autoridad.id,
                'nombre_autoridad': autoridad.nombreApellido, 
            }
        }
        print(data)

        return JsonResponse(data)

    except Autoridades.DoesNotExist:
        return JsonResponse({'message': 'Evento no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=500)
    

@csrf_exempt
def editar_autoridad(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        autoridad_id = data.get('id')
        nombre_autoridad = data.get('nombreAutoridad')
        print(autoridad_id,nombre_autoridad)

        if autoridad_id and nombre_autoridad :
            try:
                autoridad = Autoridades.objects.get(id=autoridad_id)

                autoridad.nombreApellido = nombre_autoridad

                autoridad.save()

                return JsonResponse({'message': 'Success'})
            except Autoridades.DoesNotExist:
                return JsonResponse({'message': 'Autoridad no encontrado'}, status=400)
            except ValueError as e:
                return JsonResponse({'message': f'Error de formato de fecha: {str(e)}'}, status=400)
    return JsonResponse({'message': 'Método no permitido'}, status=405)

def procesar_lista(contenido):
    # Dividir el contenido en párrafos
    parrafos = contenido.split('\n\n')

    # Iniciar el contenido HTML
    html_contenido = ''

    # Recorrer los párrafos y agregarlos al contenido HTML
    for parrafo in parrafos:
        # Dividir el párrafo en elementos de la lista
        items = parrafo.split('-')

        # Si el delimitador "-" no funcionó, intentar con ""
        if len(items) == 1:
            items = parrafo.split("")
        # Iniciar la lista HTML para el párrafo
        lista_html = '<ul>'

        # Recorrer los elementos y agregarlos a la lista HTML
        for item in items:
            # Eliminar espacios en blanco al inicio y final de cada elemento
            item = item.strip()
            # Si el elemento no está vacío, agregarlo a la lista HTML
            if item:
                lista_html += f'<li>{item}</li>'

        # Cerrar la lista HTML para el párrafo
        lista_html += '</ul>'

        # Agregar la lista HTML al contenido HTML
        html_contenido += lista_html

    return html_contenido

def procesar_contenido(contenido):
    temas = []
    tema_actual = None
    subtemas = []

    lines = contenido.split('\n')
    
    # Expresiones regulares para temas y subtemas
    tema_regex = re.compile(r'^\d+\.\s*')  # Detecta temas principales
    subtema_regex = re.compile(r'^\d+\.\d+\.\s*')  # Detecta subtemas

    for linea in lines:
        linea = linea.strip()
        # Debug: imprime cada línea procesada
        #print(f"Procesando línea: {linea}")
        
        if tema_regex.match(linea) and not subtema_regex.match(linea):  # Detectar temas principales
            if tema_actual:
                temas.append({
                    'tema': tema_actual,
                    'subtemas': subtemas
                })
                subtemas = []  # Reiniciar lista de subtemas
            
            tema_actual = linea
            #print(f"Detectado tema: {tema_actual}")
        
        elif subtema_regex.match(linea):  # Detectar subtemas
            if tema_actual:
                subtemas.append(linea)
                #print(f"  Detectado subtema: {linea}")
            
    if tema_actual:
        temas.append({
            'tema': tema_actual,
            'subtemas': subtemas
        })

    # Debug: imprime los temas procesados
    #print(f"Temas procesados: {temas}")
    return temas

def pdf_to_html(request):
    pdf_ids = request.GET.getlist('pdf_id')
    autoridades = Autoridades.objects.all()
    print(pdf_ids)  # Obtener lista de IDs de PDF
    if pdf_ids:
        identificaciones = []
        for pdf_id in pdf_ids:
            try:
                # Obtener el objeto PDF correspondiente a la ID proporcionada
                pdf_instance = PDF.objects.get(id=pdf_id)
                identificacion = {
                    'nombre': pdf_instance.nombre,
                    'materia': pdf_instance.materia,
                    'codigo': pdf_instance.codigo,
                    'condicion': pdf_instance.condicion,
                    'carrera': pdf_instance.carrera,
                    'curso': pdf_instance.curso,
                    'semestre': pdf_instance.semestre,
                    'requisitos': pdf_instance.requisitos,
                    'cargaSemanal': pdf_instance.cargaSemanal,
                    'cargaSemestral': pdf_instance.cargaSemestral,
                }
                secciones = {
                    'II. FUNDAMENTACION': pdf_instance.fundamentacion,
                    'III. OBJETIVOS': procesar_lista(pdf_instance.objetivos),
                    'IV. CONTENIDO': procesar_contenido(pdf_instance.contenido),
                    'V. METODOLOGÍA': procesar_lista(pdf_instance.metodologia),
                    'VI. EVALUACIÓN': pdf_instance.evaluacion.replace('\n', '<br>'),
                    'VII. BIBLIOGRAFÍA': procesar_lista(pdf_instance.bibliografia),
                }
                identificaciones.append({'identificacion': identificacion, 'secciones': secciones})
                print("Nombre: ", pdf_instance.nombre)
                print("Materia: ", pdf_instance.materia)
            except PDF.DoesNotExist:
                pass  # Manejar la situación en la que el PDF no existe`

        identificaciones.sort(key=lambda x: x['identificacion']['codigo'])

        if identificaciones:
            html_content = render_to_string('pdf_to_html_template.html', {'identificaciones': identificaciones,'autoridades':autoridades})
            return HttpResponse(html_content)
        else:
            return HttpResponse("No se encontraron PDFs con las IDs proporcionadas.")
    else:
        return HttpResponse("No se proporcionaron IDs de PDF.")



def eliminar_encabezados_pies_pagina(page):
    # Obtener el tamaño de la página
    width, height = page.width, page.height

    # Recortar la página para eliminar los encabezados
    page = page.within_bbox((0, 0, width, height))

    # Extraer el texto de la página
    page_text = page.extract_text()

    # Eliminar cualquier texto que contenga "Página [número]"
    page_text_lines = page_text.split('\n')
    page_text_filtered = []

    for line in page_text_lines:
        if not line.startswith("Página "):
            # Si la línea no comienza con "Página ", la agregamos sin modificaciones
            page_text_filtered.append(line)
        else:
            # Si la línea comienza con "Página ", la ignoramos
            continue

    # Eliminar la frase "Carrera de Ingeniería en Informática Facultad de Ciencias Tecnológicas – UNC@" si aparece como una frase completa
    page_text_filtered = [
        line.replace("Carrera de Ingeniería en Informática Facultad de Ciencias Tecnológicas – UNC@", "") for line in
        page_text_filtered]

    # Unir las líneas con saltos de línea
    page_text_filtered = '\n'.join(page_text_filtered)

    return page_text_filtered


def importar_pdf(request):
    if request.method == 'POST' and request.FILES.getlist('pdf_files'):
        pdf_files = request.FILES.getlist('pdf_files')

        for pdf_file in pdf_files:
            file_data = BytesIO(pdf_file.read())
            pdf_document = pdfplumber.open(file_data)

            text = ""
            for page_number in range(len(pdf_document.pages)):
                page = pdf_document.pages[page_number]

                # Eliminar encabezados y pies de página
                page_text = eliminar_encabezados_pies_pagina(page)

                text += page_text
            if not text:
                continue  # Si el texto está vacío, se pasa al siguiente archivo

            # Utilizar pdfplumber para obtener los títulos del PDF
            titles = []
            for page in pdf_document.pages:
                title_parts = []
                title = ""
                upper_count = 0
                for obj in page.chars:
                    if "Bold" in obj["fontname"]:
                        title += obj["text"]
                        if obj["text"].isupper():
                            upper_count += 1
                    elif title:
                        title_parts.extend(title.split('.')) if '.' in title else title_parts.append(title.strip())
                        title = ""
                for part in title_parts:
                    if part and len(part.strip()) > 8 and sum(1 for c in part if c.isupper()) >= 5:
                        titles.append(part.strip())

            nombre_archivo = pdf_file.name
            del titles[:2]

            # print(titles)
            # Identificar las secciones basadas en los títulos y sus ubicaciones en el texto
            secciones = {}
            patrones_secciones = titles

            for i in range(len(patrones_secciones)):
                start_idx = text.find(patrones_secciones[i])
                end_idx = text.find(patrones_secciones[i + 1]) if i + 1 < len(patrones_secciones) else len(text)
                secciones[patrones_secciones[i]] = text[start_idx:end_idx].strip()

            # Crear una nueva instancia
            pdf_instance = PDF(nombre=nombre_archivo)

            for titulo, texto in secciones.items():
                titulo_normalized = unidecode(titulo)  # Normalizar los caracteres
                if 'IDENTIFICACION' in titulo_normalized:
                    extraer_datos_identificacion(pdf_instance, texto)
                elif 'FUNDAMENTACION' in titulo_normalized:
                    partes_texto = texto.split('.')
                    if len(partes_texto) > 1:
                        texto_fundamentacion = '.'.join(partes_texto[1:-2]).strip()
                    else:
                        texto_fundamentacion = ''
                    pdf_instance.fundamentacion = texto_fundamentacion
                elif 'OBJETIVOS' in titulo_normalized:
                    partes_texto = texto.split('.')
                    if len(partes_texto) > 1:
                        texto_objetivos = '.'.join(partes_texto[1:-2]).strip()
                        if not texto_objetivos:
                            partes_texto = texto.split('\n')
                            print(partes_texto)
                            texto_objetivos = '\n'.join(partes_texto[1:-2]).strip()
                    else:
                        texto_objetivos = ''
                    pdf_instance.objetivos = texto_objetivos
                elif 'CONTENIDO' in titulo_normalized:
                    partes_texto = texto.split('.')
                    if len(partes_texto) > 1:
                        texto_contenido = '.'.join(partes_texto[1:-2]).strip()
                    else:
                        texto_contenido = ''
                    pdf_instance.contenido = texto_contenido
                elif 'METODOLOGIA' in titulo_normalized:
                    partes_texto = texto.split('.')
                    if len(partes_texto) > 1:
                        texto_metodologia = '.'.join(partes_texto[1:-2]).strip()
                    else:
                        texto_metodologia = ''
                    pdf_instance.metodologia = texto_metodologia
                elif 'EVALUACION' in titulo_normalized:
                    partes_texto = texto.split('.')
                    if len(partes_texto) > 1:
                        texto_evaluacion = '.'.join(partes_texto[1:-2]).strip()
                    else:
                        texto_evaluacion = ''
                    pdf_instance.evaluacion = texto_evaluacion
                elif 'BIBLIOGRAFIA' in titulo_normalized:
                    partes_texto = texto.split('\n')
                    print(partes_texto)
                    if len(partes_texto) > 1:
                        texto_bibliografia = '\n'.join(partes_texto[1:]).strip()
                    else:
                        texto_bibliografia = ''
                    pdf_instance.bibliografia = texto_bibliografia
            # Guardar la instancia en la base de datos
            pdf_instance.save()

        return redirect('import_success')
    return render(request, 'import_pdf.html')


def extraer_datos_identificacion(pdf_instance, texto):
    lines = texto.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        if 'nombre de la materia' in line.lower():
            pdf_instance.materia = extraer_valor(line, lines[i + 1])
        elif 'código' in line.lower():
            pdf_instance.codigo = extraer_valor(line, lines[i + 1])
        elif 'condición' in line.lower():
            pdf_instance.condicion = extraer_valor(line, lines[i + 1])
        elif 'carrera' in line.lower():
            pdf_instance.carrera = extraer_valor(line, lines[i + 1])
        elif 'curso' in line.lower():
            pdf_instance.curso = extraer_valor(line, lines[i + 1])
        elif 'semestre' in line.lower():
            pdf_instance.semestre = extraer_valor(line, lines[i + 1])
        elif 'requisitos' in line.lower():
            pdf_instance.requisitos = extraer_valor(line, lines[i + 1])
        elif 'semanal' in line.lower():
            pdf_instance.cargaSemanal = extraer_valor(line, lines[i + 1])
        elif 'semestral' in line.lower():
            pdf_instance.cargaSemestral = extraer_valor(line, lines[i + 1])


def extraer_valor(linea_actual, linea_siguiente):
    # Si la línea actual contiene un ':', lo dividimos y tomamos el segundo elemento
    if ':' in linea_actual:
        valor = linea_actual.split(':', 1)[1].strip()
        valor = valor.replace(':', '').strip()
        # Si el valor de la línea actual no está vacío después de eliminar los dos puntos, lo retornamos
        if valor:
            return valor

    # Si la línea siguiente no está vacía, la retornamos como valor
    if linea_siguiente.strip():
        valor_siguiente = linea_siguiente.replace(':', '').strip()
        if valor_siguiente:
            return valor_siguiente

    return None
def get_materiasf(request, codcarrera):
    # Obtener el parámetro de dificultad desde la solicitud GET
    dificultad = request.GET.get('dificultad', '')  # Valor por defecto es una cadena vacía
    
    # Filtrar las materias por carrera y, si se proporciona, por dificultad
    if dificultad:
        materias = list(PDF.objects.filter(codigo__icontains=codcarrera, dificultad=dificultad).values())
    else:
        materias = list(PDF.objects.filter(codigo__icontains=codcarrera).values())
    
    if len(materias) > 0:
        data = {'message': "Success", 'materias': materias}
    else:
        data = {'message': "Not Found"}

    return JsonResponse(data)

def menu(request):
    return render(request, 'menu.html')

