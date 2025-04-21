## 🚀 Primeiros Passos

Com os dois projetos executando, podemos começar a utilizar a aplicação. A Aplicação possui duas funcionalidades principais:

1. **Painel Administrativo**: Permite gerenciar os dados do sistema, como usuários, configuração de provas, cadastros de questões e etc.

2. **API REST**: Permite a comunicação com o sistema, permitindo que outras aplicações possam se conectar e realizar operações como autenticação e realização de provas.

### 1. Painel Administrativo
O painel administrativo é acessado através do endereço `http://localhost:3000/admin`. Para acessar o painel, utilize as credenciais de um usuário administrador. Caso não tenha um usuário administrador, você pode criar um diretamente no banco de dados ou utilizar o comando `python manage.py createsuperuser` para criar um superusuário. O superusuário tem acesso total ao sistema e pode gerenciar todos os dados. [Veja aqui](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/) a documentação do painel administrativo do Django.
Detalhes sobre cada funcionalidade do painel administrativo podem ser encontrados no arquivo admin-panel.md.

### 2. API REST
A API REST é acessada através do endereço `http://localhost:8000/api`.
Detalhes sobre cada endpoint podem ser encontrados no arquivo api-rest.md