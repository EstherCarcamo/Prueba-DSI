from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class PruebasDeLogin(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Configura el servicio de Microsoft Edge con la ruta a msedgedriver
        service = Service(executable_path='D:/U/dsi/SIGEA/msedgedriver.exe')
        cls.driver = webdriver.Edge(service=service)
        cls.driver.implicitly_wait(10)  # Tiempo máximo para encontrar un elemento
        print("Setup completado: Driver de Edge iniciado.")

    def test_carga_pagina_login(self):
        """
        Verifica que la página de login carga correctamente.
        """
        print("Iniciando test: test_carga_pagina_login.")
        self.driver.get('http://127.0.0.1:8000/login/')
        print("Página de login cargada.")
        
        self.assertIn("SIGEA - LOGIN", self.driver.title)
        print("Título de la página verificado.")

        # Verifica que el formulario de login se muestra correctamente
        email_field = self.driver.find_element(By.ID, "email")
        password_field = self.driver.find_element(By.ID, "password")
        submit_button = self.driver.find_element(By.TAG_NAME, "button")

        # Comprueba que los elementos existen
        self.assertIsNotNone(email_field)
        self.assertIsNotNone(password_field)
        self.assertIsNotNone(submit_button)
        print("Elementos del formulario verificados.")
        print("Test completado: test_carga_pagina_login.\n")

    def test_login_con_credenciales_invalidas(self):
        """
        Verifica el comportamiento al intentar iniciar sesión con credenciales incorrectas.
        """
        print("Iniciando test: test_login_con_credenciales_invalidas.")
        self.driver.get('http://127.0.0.1:8000/login/')
        print("Página de login cargada.")

        # Introduce datos incorrectos en el formulario de login
        email_field = self.driver.find_element(By.ID, "email")
        password_field = self.driver.find_element(By.ID, "password")
        submit_button = self.driver.find_element(By.TAG_NAME, "button")

        email_field.send_keys("incorrecto@correo.com")
        password_field.send_keys("contraseña_incorrecta")
        submit_button.click()
        print("Datos incorrectos ingresados, intentando iniciar sesión.")

        # Espera hasta que el mensaje de error esté presente
        error_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//p[contains(text(), 'Datos Incorrectos')]"))
        )

        # Verifica que el mensaje de error aparezca
        self.assertIsNotNone(error_message)
        print("Mensaje de error verificado.")
        print("Test completado: test_login_con_credenciales_invalidas.\n")

    def test_login_exitoso(self):
        """
        Simula un inicio de sesión exitoso y verifica la redirección a la página principal.
        """
        print("Iniciando test: test_login_exitoso.")
        self.driver.get('http://127.0.0.1:8000/login/')
        print("Página de login cargada.")

        # Llenamos los campos del formulario con credenciales válidas
        email_input = self.driver.find_element(By.ID, 'email')
        password_input = self.driver.find_element(By.ID, 'password')
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')

        # Usa las credenciales válidas
        email_input.send_keys("lex@lex.com")
        password_input.send_keys("lex")
        submit_button.click()
        print("Datos correctos ingresados, intentando iniciar sesión.")

        # Verificamos que redirige a la página principal
        WebDriverWait(self.driver, 10).until(
            EC.url_to_be('http://127.0.0.1:8000/')
        )
        self.assertEqual(self.driver.current_url, 'http://127.0.0.1:8000/')
        print("Redirección verificada a la página principal.")
        print("Test completado: test_login_exitoso.\n")

    def test_acceso_a_pagina_admin(self):
        """
        Verifica que después del inicio de sesión se redirige a la página principal.
        """
        print("Iniciando test: test_acceso_a_pagina_admin.")
        self.driver.get('http://127.0.0.1:8000/login/')
        
        # Realiza el inicio de sesión
        email_input = self.driver.find_element(By.ID, 'email')
        password_input = self.driver.find_element(By.ID, 'password')
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')

        email_input.send_keys("lex@lex.com")  # Credenciales válidas
        password_input.send_keys("lex")
        submit_button.click()
        
        # Verifica que la redirección es correcta (a la página principal)
        WebDriverWait(self.driver, 10).until(EC.url_to_be('http://127.0.0.1:8000/'))
        self.assertEqual(self.driver.current_url, 'http://127.0.0.1:8000/')
        print("Redirección verificada a la página principal.")
        print("Test completado: test_acceso_a_pagina_admin.\n")

    def test_tipo_usuario_es_admin(self):
        """
        Verifica que el tipo de usuario se muestra como 'Administrador' en el valor oculto.
        """
        print("Iniciando test: test_tipo_usuario_es_admin.")
        self.driver.get('http://127.0.0.1:8000/login/')
        
        # Realiza el inicio de sesión
        email_input = self.driver.find_element(By.ID, 'email')
        password_input = self.driver.find_element(By.ID, 'password')
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')

        email_input.send_keys("lex@lex.com")
        password_input.send_keys("lex")
        submit_button.click()
        
        # Espera a que la página se cargue y verifica el valor del input oculto
        pruebita_value = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'pruebita'))
        )
        self.assertEqual(pruebita_value.get_attribute('value'), 'admin')  # Verificamos que es tipo Administrador
        print("Tipo de usuario verificado como Administrador.")
        print("Test completado: test_tipo_usuario_es_admin.\n")

    def test_elementos_topbar_visibles(self):
        """
        Verifica que los elementos del topbar (nombre, foto de perfil, menú de usuario) se muestran correctamente.
        """
        print("Iniciando test: test_elementos_topbar_visibles.")
        self.driver.get('http://127.0.0.1:8000/login/')
        
        # Realiza el inicio de sesión
        email_input = self.driver.find_element(By.ID, 'email')
        password_input = self.driver.find_element(By.ID, 'password')
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')

        email_input.send_keys("lex@lex.com")
        password_input.send_keys("lex")
        submit_button.click()
        
        # Verifica que el nombre del usuario y la imagen de perfil están presentes
        user_name = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.text-gray-600.small'))
        )
        user_profile_img = self.driver.find_element(By.CSS_SELECTOR, '.img-profile')
        
        self.assertIn("Daniel Alexis", user_name.text)  # Verifica que el nombre coincide
        self.assertIsNotNone(user_profile_img)  # Verifica que la imagen de perfil está presente
        print("Elementos del topbar verificados.")
        print("Test completado: test_elementos_topbar_visibles.\n")

    def test_funcionalidad_logout(self):
        """
        Verifica que el usuario puede cerrar sesión correctamente.
        """
        print("Iniciando test: test_funcionalidad_logout.")
        self.driver.get('http://127.0.0.1:8000/login/')
        
        # Realiza el inicio de sesión
        email_input = self.driver.find_element(By.ID, 'email')
        password_input = self.driver.find_element(By.ID, 'password')
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')

        email_input.send_keys("lex@lex.com")
        password_input.send_keys("lex")
        submit_button.click()

        # Abre el menú de usuario
        user_dropdown = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.ID, 'userDropdown'))
        )
        user_dropdown.click()
        print("Menú de usuario abierto.")

        # Espera a que el menú desplegable sea visible
        WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".dropdown-menu.show"))
        )

        # Haz clic en el enlace de Logout que abre el modal
        logout_link = self.driver.find_element(By.CSS_SELECTOR, "a.dropdown-item[data-target='#logoutModal']")
        logout_link.click()
        print("Botón de Logout en el menú desplegable clicado.")

        # Verifica si el modal de logout está presente
        logout_modal = WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located((By.ID, 'logoutModal'))
        )
        print("Modal de logout visible.")

        # Haz clic en el botón de confirmación dentro del modal para cerrar sesión
        confirm_logout_button = self.driver.find_element(By.CSS_SELECTOR, "a.btn-primary[href='/logout/']")
        confirm_logout_button.click()
        print("Botón de confirmación de Logout clicado.")

        # Verifica que redirige a la página de login después de cerrar sesión
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, 'email'))  # Verifica que el campo de email esté presente
            )
            print("Redirección a la página de login verificada.")
        except TimeoutException:
            print("No se redirigió a la página de login.")
            self.fail("La redirección a la página de login falló.")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()
        print("TearDown completado: Driver de Edge cerrado.")



#-----------------------------------------------------------------
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class PruebasDepartamentos(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Configura el servicio de Microsoft Edge con la ruta a msedgedriver
        service = Service(executable_path='D:/U/dsi/SIGEA/msedgedriver.exe')
        cls.driver = webdriver.Edge(service=service)
        cls.driver.implicitly_wait(10)
        print("Setup completado: Driver de Edge iniciado.")

    def iniciar_sesion(self):
        """
        Método auxiliar para iniciar sesión en el sistema.
        """
        self.driver.get('http://127.0.0.1:8000/login/')
        email_input = self.driver.find_element(By.ID, 'email')
        password_input = self.driver.find_element(By.ID, 'password')
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')

        email_input.send_keys("lex@lex.com")
        password_input.send_keys("lex")
        submit_button.click()

        WebDriverWait(self.driver, 10).until(
            EC.url_to_be('http://127.0.0.1:8000/')
        )

    def test_acceso_a_departamentos(self):
        """
        Verifica que el usuario puede acceder al módulo de departamentos desde el menú lateral.
        """
        print("Iniciando test: test_acceso_a_departamentos.")
        self.iniciar_sesion()

        # Acceso a la página de departamentos
        try:
            departamentos_link = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "li.nav-item a.nav-link[href='/departamento/']"))
            )
            departamentos_link.click()
        except TimeoutException:
            print("Error: No se pudo acceder a la página de departamentos.")
            return

        # Verifica que la página de departamentos cargue correctamente
        titulo = self.driver.title
        self.assertEqual(titulo, 'Departamentos', "No se cargó la página de Departamentos correctamente")
        print("Acceso al módulo de departamentos desde el menú lateral verificado.")

    def test_creacion_departamento(self):
        """
        Verifica que el usuario puede crear un departamento correctamente.
        """
        print("Iniciando test: test_creacion_departamento.")
        self.iniciar_sesion()

        # Acceso a la página de departamentos
        try:
            departamentos_link = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "li.nav-item a.nav-link[href='/departamento/']"))
            )
            departamentos_link.click()
        except TimeoutException:
            print("Error: No se pudo acceder a la página de departamentos.")
            return

        # Clic en el botón de "Crear Departamento"
        try:
            crear_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-primary[data-target='#createModal']"))
            )
            crear_button.click()
        except TimeoutException:
            print("Error: No se pudo hacer clic en el botón de 'Crear Departamento'.")
            return

        # Espera a que el formulario se cargue dentro del modal
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, 'createForm'))
            )
            print("Formulario de creación de departamento cargado.")
        except TimeoutException:
            print("Error: El formulario de creación no se cargó.")
            return

        # Llenar el formulario del nuevo departamento
        try:
            division_input = self.driver.find_element(By.ID, 'id_divisiondepartamento')
            responsable_select = self.driver.find_element(By.ID, 'id_responsabledepartamento')

            # Llenar el campo de texto de la división
            division_input.send_keys("División Prueba")

            # Capturar todas las opciones disponibles en el select
            opciones_responsable = responsable_select.find_elements(By.TAG_NAME, 'option')
            if len(opciones_responsable) > 1:
                opciones_responsable[1].click()  # Selecciona la primera opción disponible, distinta de 'Sin responsable'
            else:
                print("Error: No se encontraron opciones válidas en el select de responsable.")
                return

            # Clic en el botón de guardar usando JavaScript
            guardar_button = self.driver.find_element(By.CSS_SELECTOR, "button.btn-primary[onclick='submitCreateForm()']")
            self.driver.execute_script("arguments[0].click();", guardar_button)
        except TimeoutException:
            print("Error: No se pudo llenar el formulario o hacer clic en 'Guardar'.")
            return

        # Espera a que aparezca el mensaje de éxito
        try:
            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "button.swal2-confirm"))
            ).click()
            print("Departamento creado correctamente.")
        except TimeoutException:
            print("Error: El mensaje de éxito no apareció.")
            return

    def obtener_ultimo_departamento(self):
        """
        Método auxiliar para obtener el ID del último departamento creado.
        """
        try:
            tabla = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody"))
            )
            filas = tabla.find_elements(By.TAG_NAME, 'tr')
            ultima_fila = filas[-1]
            id_departamento = ultima_fila.find_element(By.TAG_NAME, 'td').text  # El primer <td> es el ID
            return id_departamento
        except TimeoutException:
            print("Error: No se pudo obtener el último departamento.")
            return None

from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class PruebasDepartamentos(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Configura el servicio de Microsoft Edge con la ruta a msedgedriver
        service = Service(executable_path='D:/U/dsi/SIGEA/msedgedriver.exe')
        cls.driver = webdriver.Edge(service=service)
        cls.driver.implicitly_wait(10)
        print("Setup completado: Driver de Edge iniciado.")

    def iniciar_sesion(self):
        """
        Método auxiliar para iniciar sesión en el sistema.
        """
        self.driver.get('http://127.0.0.1:8000/login/')
        email_input = self.driver.find_element(By.ID, 'email')
        password_input = self.driver.find_element(By.ID, 'password')
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')

        email_input.send_keys("lex@lex.com")
        password_input.send_keys("lex")
        submit_button.click()

        WebDriverWait(self.driver, 10).until(
            EC.url_to_be('http://127.0.0.1:8000/')
        )

    def test_acceso_a_departamentos(self):
        """
        Verifica que el usuario puede acceder al módulo de departamentos desde el menú lateral.
        """
        print("Iniciando test: test_acceso_a_departamentos.")
        self.iniciar_sesion()

        # Acceso a la página de departamentos
        try:
            departamentos_link = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "li.nav-item a.nav-link[href='/departamento/']"))
            )
            departamentos_link.click()
        except TimeoutException:
            print("Error: No se pudo acceder a la página de departamentos.")
            return

        # Verifica que la página de departamentos cargue correctamente
        titulo = self.driver.title
        self.assertEqual(titulo, 'Departamento', "No se cargó la página de Departamentos correctamente")
        print("Acceso al módulo de departamentos desde el menú lateral verificado.")

    def test_creacion_departamento(self):
        """
        Verifica que el usuario puede crear un departamento correctamente.
        """
        print("Iniciando test: test_creacion_departamento.")
        self.iniciar_sesion()

        # Acceso a la página de departamentos
        try:
            departamentos_link = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "li.nav-item a.nav-link[href='/departamento/']"))
            )
            departamentos_link.click()
        except TimeoutException:
            print("Error: No se pudo acceder a la página de departamentos.")
            return

        # Clic en el botón de "Crear Departamento"
        try:
            crear_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-primary[data-target='#createModal']"))
            )
            crear_button.click()
        except TimeoutException:
            print("Error: No se pudo hacer clic en el botón de 'Crear Departamento'.")
            return

        # Espera a que el formulario se cargue dentro del modal
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, 'createForm'))
            )
            print("Formulario de creación de departamento cargado.")
        except TimeoutException:
            print("Error: El formulario de creación no se cargó.")
            return

        # Llenar el formulario del nuevo departamento
        try:
            division_input = self.driver.find_element(By.ID, 'id_divisiondepartamento')
            responsable_select = self.driver.find_element(By.ID, 'id_responsabledepartamento')

            # Llenar el campo de texto de la división
            division_input.send_keys("División Prueba")

            # Capturar todas las opciones disponibles en el select
            opciones_responsable = responsable_select.find_elements(By.TAG_NAME, 'option')
            if len(opciones_responsable) > 1:
                opciones_responsable[1].click()  # Selecciona la primera opción disponible, distinta de 'Sin responsable'
            else:
                print("Error: No se encontraron opciones válidas en el select de responsable.")
                return

            # Clic en el botón de guardar usando JavaScript
            guardar_button = self.driver.find_element(By.CSS_SELECTOR, "button.btn-primary[onclick='submitCreateForm()']")
            self.driver.execute_script("arguments[0].click();", guardar_button)
        except TimeoutException:
            print("Error: No se pudo llenar el formulario o hacer clic en 'Guardar'.")
            return

        # Espera a que aparezca el mensaje de éxito
        try:
            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "button.swal2-confirm"))
            ).click()
            print("Departamento creado correctamente.")
        except TimeoutException:
            print("Error: El mensaje de éxito no apareció.")
            return

    def obtener_ultimo_departamento(self):
        """
        Método auxiliar para obtener el ID del último departamento creado.
        """
        try:
            tabla = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody"))
            )
            filas = tabla.find_elements(By.TAG_NAME, 'tr')
            ultima_fila = filas[-1]
            id_departamento = ultima_fila.find_element(By.TAG_NAME, 'td').text  # El primer <td> es el ID
            return id_departamento
        except TimeoutException:
            print("Error: No se pudo obtener el último departamento.")
            return None

    def test_edicion_departamento(self):
        """
        Verifica que el usuario puede editar un departamento existente.
        """
        print("Iniciando test: test_edicion_departamento.")
        self.iniciar_sesion()

        # Acceso a la página de departamentos
        try:
            departamentos_link = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "li.nav-item a.nav-link[href='/departamento/']"))
            )
            departamentos_link.click()
        except TimeoutException:
            print("Error: No se pudo acceder a la página de departamentos.")
            return

        # Obtener el ID del último departamento creado
        id_departamento = self.obtener_ultimo_departamento()
        if not id_departamento:
            return

        # Clic en el botón de "Editar Departamento"
        try:
            editar_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f"button.btn-warning[onclick='loadUpdateForm({id_departamento})']"))
            )
            editar_button.click()
        except TimeoutException:
            print(f"Error: No se pudo hacer clic en el botón de 'Editar Departamento' para el ID {id_departamento}.")
            return

        # Espera a que el formulario se cargue dentro del modal
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, f'updateForm{id_departamento}'))
            )
            print("Formulario de edición de departamento cargado.")
        except TimeoutException:
            print("Error: El formulario de edición no se cargó.")
            return

        # Llenar el formulario con nuevos datos
        try:
            division_input = self.driver.find_element(By.ID, 'id_divisiondepartamento')
            division_input.clear()
            division_input.send_keys("División Editada")

            # Clic en el botón de guardar cambios usando JavaScript
            guardar_button = self.driver.find_element(By.CSS_SELECTOR, f"button.btn-primary[onclick='submitUpdateForm({id_departamento})']")
            self.driver.execute_script("arguments[0].click();", guardar_button)
        except TimeoutException:
            print("Error: No se pudo editar el departamento o hacer clic en 'Guardar Cambios'.")
            return

        # Espera a que aparezca el mensaje de éxito
        try:
            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "button.swal2-confirm"))
            ).click()
            print("Departamento editado correctamente.")
        except TimeoutException:
            print("Error: El mensaje de éxito no apareció.")
            return

    def test_eliminacion_departamento(self):
        """
        Verifica que el usuario puede eliminar un departamento existente.
        """
        print("Iniciando test: test_eliminacion_departamento.")
        self.iniciar_sesion()

        # Acceso a la página de departamentos
        try:
            departamentos_link = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "li.nav-item a.nav-link[href='/departamento/']"))
            )
            departamentos_link.click()
        except TimeoutException:
            print("Error: No se pudo acceder a la página de departamentos.")
            return

        # Obtener el ID del último departamento creado
        id_departamento = self.obtener_ultimo_departamento()
        if not id_departamento:
            return

        # Asegurarse de que el botón está en la vista
        try:
            eliminar_button = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f"button#eliminar-departamento-{id_departamento}"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", eliminar_button)

            # Intentar clic con JavaScript
            self.driver.execute_script("arguments[0].click();", eliminar_button)
        except TimeoutException:
            print(f"Error: No se pudo hacer clic en el botón de 'Eliminar Departamento' para el ID {id_departamento}.")
            return

        # Confirmar la eliminación
        try:
            confirmar_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.swal2-confirm"))
            )
            self.driver.execute_script("arguments[0].click();", confirmar_button)
            print("Departamento eliminado correctamente.")
        except TimeoutException:
            print("Error: No se pudo confirmar la eliminación.")
            return

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()
        print("TearDown completado: Driver de Edge cerrado.")
