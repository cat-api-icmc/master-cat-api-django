## 🌐 API REST

A API REST é acessada através do endereço `http://localhost:8000/api`. A API é baseada em REST e utiliza o padrão JSON para troca de dados. A autenticação é feita através de tokens de usuários, que podem ser gerados através do endpoint `/api/auth/`.

### /api/hc/
- **GET**: Retorna o status do sistema.

### /api/hc/db/
- **GET**: Retorna o status de conexão com o banco de dados.

### /api/hc/plumber/
- **GET**: Retorna o status de conexão com o Plumber.

### /api/hc/all/
- **GET**: Retorna o status de todos os serviços.

### /api/assessment/
- **GET**: Retorna a lista de todas as avaliações disponíveis para o usuário autenticado.
As avaliações disponíveis são filtradas por ativas e dentro do período de validade.

### /api/assessment/{uuid}/
- **GET**: Retorna os detalhes de uma avaliação específica.

### /api/user-assessment/
- **POST**: Cria uma nova avaliação para o usuário autenticado.
    - Body: 
    ```json
    {
        "assessment": "UUID4 da Avaliação"
    }
    ```

### /api/user-assessment/{uuid}/
- **PATCH**: Atualiza uma avaliação existente para o usuário autenticado.
    - Body: 
    ```json
    {
        "alternative": "UUID4 da Alternativa Respondida pelo Usuário",
    }
    ```

### /api/auth/login/
- **POST**: Realiza o login do usuário e retorna um token de autenticação.
    - Body: 
    ```json
    {
        "email": "Email do Usuário",
        "password": "Senha do Usuário"
    }
    ```

### /api/me/
- **GET**: Retorna os detalhes do usuário autenticado.