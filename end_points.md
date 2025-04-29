# GitHub API: Endpoints Clave para el Proyecto "Open Source"

### **1. Repositorios**
- **Listar repositorios populares**  
  `GET /search/repositories?q=stars:>1000&sort=stars&order=desc`  
  (Filtra por estrellas, lenguaje, licencia, etc.)

- **Detalles de un repositorio**  
  `GET /repos/{owner}/{repo}`  
  (Obtiene métricas como `stargazers_count`, `forks`, `open_issues`, `license`, `languages_url`)

- **Contribuyentes**  
  `GET /repos/{owner}/{repo}/contributors`  
  (Lista de desarrolladores y sus contribuciones)

### **2. Usuarios**
- **Información de perfil**  
  `GET /users/{username}`  
  (Datos como `public_repos`, `followers`, `company`, `location`)

- **Repositorios de un usuario**  
  `GET /users/{username}/repos`  
  (Filtro por tipo: `all`, `owner`, `member`)

### **3. Búsquedas Avanzadas**
- **Buscar repositorios por lenguaje**  
  `GET /search/repositories?q=language:python+stars:>500`  

- **Buscar temas (topics)**  
  `GET /search/repositories?q=topic:machine-learning`  

### **4. Actividad**
- **Commits de un repositorio**  
  `GET /repos/{owner}/{repo}/commits`  
  (Filtro por fecha: `since` y `until`)

- **Issues y Pull Requests**  
  `GET /repos/{owner}/{repo}/issues`  
  `GET /repos/{owner}/{repo}/pulls`  

### **5. Licencias**
- **Listar licencias disponibles**  
  `GET /licenses`  
  (Detalles de licencias como `MIT`, `GPL-3.0`, `Apache-2.0`)

- **Licencia de un repositorio**  
  `GET /repos/{owner}/{repo}/license`  

### **6. Estadísticas**
- **Tráfico de visitas**  
  `GET /repos/{owner}/{repo}/traffic/views`  
  (Requiere permisos de administrador)

- **Clones del repositorio**  
  `GET /repos/{owner}/{repo}/traffic/clones`  

### **7. Organizaciones**
- **Repositorios de una organización**  
  `GET /orgs/{org}/repos`  
  (Ejemplo: `GET /orgs/google/repos`)

---

### **Parámetros Útiles**
- `per_page`: Número de resultados por página (máx. 100).  
- `page`: Número de página para paginación.  
- `sort`: Ordenar por `stars`, `forks`, `updated`, etc.  

### **Ejemplo de Uso con Python**
```python
import requests

headers = {"Authorization": "token TU_TOKEN"}
response = requests.get("https://api.github.com/search/repositories?q=stars:>1000", headers=headers)
data = response.json()