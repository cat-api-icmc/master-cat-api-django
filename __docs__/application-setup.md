## 🚀 Setup do Aplicação

Esta aplicação é composta por dois projetos:

- **Servidor Django (Python 3.12)**: 
[https://github.com/cat-api-icmc/master-cat-api-django](https://github.com/cat-api-icmc/master-cat-api-django)
Esta parte da aplicação é responsável por fornecer uma API RESTful para o cliente. Ele lida com a lógica de negócios, manipulação de dados e comunicação com o banco de dados.
Além disso, ele também é responsável pelo gerenciamento de usuário e possui um painel administrativo para facilitar a administração do sistema.

- **Servidor Plumber (R)**: 
[https://github.com/cat-api-icmc/master-cat-api-plumber](https://github.com/cat-api-icmc/master-cat-api-plumber)
Esta parte da aplicação é responsável por fornecer uma API que realiza a manipulação de dados das avaliações além de possuir toda a lógica de **Testes adaptativos (CAT)**.

Ambos os projetos são executados em contêineres Docker, o que facilita a configuração e o gerenciamento do ambiente de desenvolvimento. Os dois projetos se comunicam entre si por uma network Docker chamada `cat-api`.

Para executar os projetos, primeiro, é necessário ter o Docker e o Docker Compose instalados na sua máquina. Você pode adquirir o Docker [**aqui**](https://www.docker.com/)

Com o Docker e o Docker Compose instalados, você pode iniciar os projetos executando o seguinte comando no terminal na raiz de cada projeto:

```bash
docker-compose up --build
```

## 🐍 Configuração do Servidor Django

Antes de poder ser executado, o servidor Django precisa ser configurado. Para isso, siga os passos abaixo:

**Ajuste o arquivo `.env`**:
Na raiz do projeto Django existe um arquivo .env. Nele, você deve definir as variáveis de ambiente necessárias para a configuração do Django, principalmente as relacionadas ao banco de dados que deve ser um MySQL ou MariaDB. 

A variável PLUMBER_API_URL deve ser ajustada para o endereço do servidor Plumber. O valor padrão é `http://plumber:8080`, que é o nome do serviço definido no docker-compose.yml. Caso você esteja executando o servidor Plumber em outra máquina, ajuste o valor para o IP ou domínio correto.

**Criação do banco de dados**:
Caso o banco de dados que você escolheu não exista, você deve criá-lo. O Django não cria o banco de dados automaticamente, apenas as tabelas. Para isso, você pode usar um cliente MySQL ou MariaDB, como o MySQL Workbench ou o DBeaver.

Para criar as tabelas, execute o seguinte comando no terminal na raiz do projeto Django:

```bash
python manage.py migrate
```
Isso irá criar todas as tabelas necessárias no banco de dados. [Veja aqui](https://docs.djangoproject.com/en/5.2/topics/migrations/) mais informações sobre as migrações do Django.
