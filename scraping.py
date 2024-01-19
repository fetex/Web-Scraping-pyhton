from bs4 import BeautifulSoup as bs
import pandas as pd
import time 
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Lee el archivo CSV
df_csv = pd.read_csv('WebScrapping_Enlaces.csv')

# Obtén todos los valores de la columna "url"
# enlaces_vacantes = df_csv['Url'].tolist()


enlaces_vacantes = ['https://co.computrabajo.com/trabajo-de-mesa-de-ayuda-en-remoto?pubdate=7',
                    'https://co.computrabajo.com/trabajo-de-mesa-de-ayuda?pubdate=7',
                    'https://co.computrabajo.com/trabajo-de-tester-qa-en-remoto?pubdate=7',
                    'https://co.computrabajo.com/trabajo-de-tester-qa?pubdate=7',
                    'https://co.computrabajo.com/trabajo-de-sistemas-en-remoto?pubdate=7',
                    'https://co.computrabajo.com/trabajo-de-tecnico-en-sistemas-en-remoto?pubdate=99',
                    'https://co.computrabajo.com/trabajo-de-frontend?pubdate=1',
                    'https://co.computrabajo.com/trabajo-de-desarrollador-sql?pubdate=1']


# Guardar el tiempo de inicio
inicio = time.time()

# Inicializar el navegador
driver = webdriver.Chrome()


# Inicializar dataframe para cada portal
df_computrabajo = pd.DataFrame()
df_magneto = pd.DataFrame()
df_elemplo = pd.DataFrame()

# Función para datos del elemplo
def dataElEmpleo(vacantes):

    lista_vacantes_elempleo = []

    for vacante in vacantes:
        driver.get(vacante)
        html = driver.page_source
        soup = bs(html, 'lxml')

        # Intenta encontrar los elementos necesarios, si no los encuentra, asigna valores predeterminados
        titulo = soup.find('span', {'class': 'js-jobOffer-title'})
        empresa_element = soup.find('div', class_='col-xs-12 col-lg-7 ee-header-company')
        ciudad_element = soup.find('span', {'class': 'js-joboffer-city'})
        
        if titulo and empresa_element and ciudad_element:
            titulo_text = titulo.text.strip()
            empresa = empresa_element.strong.get_text(strip=True)
            ciudad = ciudad_element.text.strip()
            modalidad = "Presencial" if ciudad != "Remoto" else "Remoto"

            span_elements = soup.select('.offer-data-additional span')
            condiciones = [span.get_text(strip=True) for span in span_elements]
            condiciones = condiciones[1:-1]

            keywords_element = soup.find('div', class_='requirements-content ee-keywords')
            li = keywords_element.find_all('li')
            keywords = [keyword.get_text(strip=True) for keyword in li]
            skills = ['Conocimientos:'] + keywords
            skills = ', '.join(skills)
            condiciones.append(skills)

            lista_vacantes_elempleo.append({
                'titulo': titulo_text,
                'empresa': empresa,
                'portal': 'El empleo',
                'ciudad': ciudad,
                'modalidad': modalidad,
                'requisitos': condiciones
            })

    # Crear el DataFrame a partir de la lista de diccionarios
    df_vacantes_elempleo = pd.DataFrame(lista_vacantes_elempleo)

    return df_vacantes_elempleo


#Funcion para datos de magneto
# def dataMagneto(url_vacante):
#     # driver.get(url)
#     html = driver.page_source
#     soup = bs(html, 'lxml')
#     titulo = soup.find('h2',{'class':'mg_job_header_magneto-ui-job-header_title_1an3d'}).text

#     empresa = soup.find('h3',{'class':'mg_job_header_magneto-ui-job-header_subtitle_1an3d'}).text


#     condiciones= soup.find('div',{'class': 'mg_job_details_magneto-ui-job-details_wrapper_nkmig'})
#     condiciones_text = condiciones.find_all('p')
#     detalle_requisitos = [ req.get_text(strip=True) for req in condiciones_text]

#     modalidad = detalle_requisitos[4].split(sep=':')[0].replace(' / ','-').split(' ')[0]

#     ciudad = detalle_requisitos[4].split(sep=':')[1]

#     elementos_div = soup.find_all('div', class_='mg_job_apply_card_magneto-ui-job-apply-card_requirements_1h1q3')
#     resultados = [f"{div.find('h3').text.strip()} {div.find('p').text.strip()}" for div in elementos_div]

#     element_skill = soup.find_all('div', class_='mg_skill_magneto-ui-skill_wrapper_1cgh2')
#     skills = [div.find('h3').text.strip() for div in element_skill]
#     skills = ['Conocimientos:'] + skills
#     skills = ', '.join(skills)
#     detalle_requisitos.append(skills)

#     vacantes_magneto = pd.Series()

#     vacantes_magneto['titulo'] = titulo
#     vacantes_magneto['empresa'] = empresa
#     vacantes_magneto['ciudad'] = ciudad
#     vacantes_magneto['modalidad'] = modalidad
#     vacantes_magneto['requisitos'] = detalle_requisitos

#     df_vacantes_magneto = pd.DataFrame(vacantes_magneto)
#     return(df_vacantes_magneto.T)

#Funcion para datos de computrabajo
def dataVacanteComputrabajo(url_vacante):

    # # print("URL de la vacante:", url_vacante)
    # url_vacante_completa = 'https://co.computrabajo.com' + url_vacante

    driver.get(url_vacante)
    html = driver.page_source
    soup = bs(html, 'lxml')

    # Validacion si hay vacantes 
    sinvacantes = soup.find('p', class_='tc pAll30 mAuto w50 w100_m fs16')
    resultado = "Sin vacantes" if sinvacantes else "Hay vacantes"

    if resultado == "Sin vacantes":
        print("No hay vacantes")
        return pd.DataFrame()
    
    else:

        # Verificar si se encuentra el elemento del título
        titulo_element = soup.find('h1', {'class': 'fwB fs24 mb5 box_detail w100_m'})
        if titulo_element:
            titulo = titulo_element.text
        else:
            titulo = "No se encontró el título"

        ubicación = soup.find( 'p',{'class':'fs16'}).text

        empresa = ubicación.split(',')[0].split('-')[0].strip()
        ciudad =  ubicación.split(',')[1].strip()


        requisitos = soup.find('ul',{'class': 'disc mbB'})
        li = requisitos.find_all('li')
        detalle_requisitos = [ li.get_text(strip=True) for li in li]

        # Seleccionar los elementos span dentro del div con class="mbB"
        span_oferta = soup.select('div.mbB span.tag.base')

        # Obtener el texto de cada span
        texto_oferta = [span.get_text(strip=True) for span in span_oferta]

        if len(texto_oferta) < 4:
            modalidad = "Sin especificar"
        else:
            modalidad = texto_oferta[-1]


        vacantes_computrabajo = pd.Series()

        vacantes_computrabajo['titulo'] = titulo
        vacantes_computrabajo['empresa'] = empresa
        vacantes_computrabajo['portal'] = 'Computrabajo'
        vacantes_computrabajo['ciudad'] = ciudad
        vacantes_computrabajo['modalidad'] = modalidad
        vacantes_computrabajo['requisitos'] = detalle_requisitos

        df_vacantes_computrabajo = pd.DataFrame(vacantes_computrabajo)

    return(df_vacantes_computrabajo.T)

# print(dataVacanteComputrabajo('https://co.computrabajo.com/trabajo-de-mesa-de-ayuda?iex=7&pubdate=7'))

# Función para realizar scraping en Computrabajo
def vacantesComputrabajo(url):

    df_vacantes_computrabajo = pd.DataFrame()  # Inicializar el DataFrame antes del bucle
    driver.get(url)
    dominio_base = "https://co.computrabajo.com"

# Ciclo para iterar a través de las páginas
    while True:
        # Esperar a que la página cargue antes de continuar (ajusta el tiempo según sea necesario)
        driver.implicitly_wait(5)

        # Esperar a que desaparezca el elemento emergente
        try:
            WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.ID, 'pop-up-webpush-background')))
        except:
            pass

        # Obtener el HTML de la página actual
        html = driver.page_source

        # Crear objeto BeautifulSoup
        soup = bs(html, 'lxml')

        # Obtener enlaces de las vacantes en la página actual
        enlaces_vacantes = [enlace['href'] for enlace in soup.select('article a.js-o-link.fc_base[href]')]

        # Puedes hacer lo que necesites con los enlaces de esta página

        url_actual = driver.current_url

        # Agregar impresiones para diagnóstico
        # print(f"URL actual: {url_actual}")
        # print(f"Número de vacantes en la página: {len(vacantes)}")

        for vacante in enlaces_vacantes:
            url_vacante = dominio_base + vacante
            nueva_vacante = dataVacanteComputrabajo(url_vacante)
            df_vacantes_computrabajo = pd.concat([df_vacantes_computrabajo,nueva_vacante], ignore_index=True)
            driver.get(url_actual)

        # Buscar el botón "Siguiente"
        try:
            siguiente_button = driver.find_element(By.XPATH, '//span[@class="b_primary w48 buildLink cp" and text()="Siguiente"]')
        except NoSuchElementException:
            print("No se encontró el botón 'Siguiente'. Fin del ciclo.")
            driver.quit()

            df_vacantes_computrabajo.to_csv('Vacantes.csv', index=False)
            return df_vacantes_computrabajo
            break

        # Verificar si el botón está deshabilitado
        if "disabled" in siguiente_button.get_attribute("class"):
            print("El botón 'Siguiente' está deshabilitado. Fin del ciclo.")
            driver.quit()

            # df_vacantes_computrabajo.to_csv('Vacantes.csv', index=False)
            return df_vacantes_computrabajo
            break

        # Intentar hacer clic en el botón "Siguiente"
        try:
            driver.execute_script("arguments[0].click();", siguiente_button)
        except ElementClickInterceptedException:
            print("Error al hacer clic en el botón 'Siguiente'.")
            driver.quit()
            break

    
    return df_vacantes_computrabajo

# Función scraping magneto      
def vacantesMagneto(url):
    driver.get (url)
    lista_vacantes = []

    # df_magneto = pd.DataFrame(columns=['titulo', 'empresa', 'ciudad', 'modalidad', 'requisitos'])

    # Obtener el HTML de la página actual
    html = driver.page_source
    # Crear objeto BeautifulSoup
    soup = bs(html, 'lxml')
    # Validacion si hay vacantes 
    sinvacantes = soup.find('main', class_='mg_empty_results_magneto-ui-empty-result_12ku4')
    resultado = "Sin vacantes" if sinvacantes else "Hay vacantes"

    if resultado == "Sin vacantes":
        return pd.DataFrame()
    else:
        # Encuentra todos los elementos article
        articulos = soup.select('#magneto-ui-jobs-page .mg_jobs_page_magneto-ui-jobs-page--center-row_91y07 .mg_jobs_page_magneto-ui-jobs-page--center-row_jobs-result_91y07 article')

        # Itera sobre cada artículo
        for articulo in articulos:
            # Encuentra los elementos h3 y p dentro de cada artículo
            titulo = articulo.find('h2').text
            empresa = articulo.find('h3').text
            parrafo = [p.text.strip() for p in articulo.find_all('p')]
            ciudad = parrafo[1]
            modalidad = ''
            requisitos = parrafo[2]

            lista_vacantes.append({'titulo': titulo, 'empresa': empresa, 'portal':'magneto', 'ciudad': ciudad, 'modalidad': modalidad, 'requisitos': requisitos})

            # df_magneto = df_magneto.append({'titulo': titulo, 'empresa': empresa, 'ciudad': ciudad, 'modalidad': modalidad, 'requisitos': requisitos}, ignore_index=True)

        # Crear el DataFrame a partir de la lista de diccionarios
        df_magneto = pd.DataFrame(lista_vacantes)

        # Guardar el DataFrame en un archivo CSV
        df_magneto.to_csv('VacantesMagneto.csv', index=False)

    return df_magneto


#Funcion scraping el empleo
def vacantesElempleo(url):
    driver.get(url)
    html = driver.page_source
    soup = bs(html, 'lxml')

    enlaces_elempleo = []

    dominio_base = "https://www.elempleo.com"

    # vacantes = [enlace['href'] for enlace in soup.select('.row.result-list js-result-list js-results-container .result-item[data-url]')]
    result_items = soup.find_all(class_='result-item')

    for result_item in result_items:
        # Encontrar el div anidado dentro de "result-item" que tiene el atributo data-url
        valor_data_url = result_item.find('div', class_='js-area-bind').get('data-url')
        url_vacante = dominio_base+valor_data_url
        enlaces_elempleo.append(url_vacante)

    df_elemplo = dataElEmpleo(enlaces_elempleo)

    return df_elemplo
     


#Identificar portal de empleo
def idenPortal(enlace):
    portal = enlace.split('//')[1].split('.')[1]

    if portal == "computrabajo":
        return vacantesComputrabajo(enlace)

    elif portal == "magneto365":
        return vacantesMagneto(enlace)

    elif portal == "elempleo":
        return vacantesElempleo(enlace)


# Iterar sobre los enlaces y realizar scraping
for e in enlaces_vacantes:
    print(e)
    df_portal = idenPortal(e)

    # Concatenar el DataFrame del portal actual al DataFrame general
    if 'computrabajo' in e:
        df_computrabajo = pd.concat([df_computrabajo, df_portal], ignore_index=True)
    elif 'magneto365' in e:
        df_magneto = pd.concat([df_magneto, df_portal], ignore_index=True)
    elif 'elempleo' in e:
        df_elemplo = pd.concat([df_elemplo, df_portal], ignore_index=True)

    # Pausar la ejecución para revisar el HTML del navegador
    # input("Presiona Enter para continuar y revisar el HTML del navegador...")



# Concatenar todos los DataFrames
dfs = [df_computrabajo, df_magneto, df_elemplo]
df_final = pd.concat(dfs, ignore_index=True)

df_final.to_csv('WEB_SCRAPING.csv', index=False)


# Guardar el tiempo de finalización
fin = time.time()

# Calcular la diferencia de tiempo
tiempo_total = fin - inicio
tiempo_minutos = tiempo_total/60

print(f"Tiempo de ejecución: {tiempo_minutos:.2f} minutos")



