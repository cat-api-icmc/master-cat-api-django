## 🚀 Painel Administrativo

Logo depois de acessar o painel administrativo, você verá uma tela com uma listagem de todos os modelos disponíveis no sistema. Você pode clicar em cada modelo para visualizar, editar ou excluir os dados.

Os modelos estão organizados em grupos, facilitando a navegação. Os grupos são os seguintes:

**1. Aprendizado**:
- Onde você pode gerenciar os dados relacionados ao aprendizado, como questões, provas e respostas.

**2. Autenticação e Autorização**:
- Este app é criado pelo próprio Django e contém os modelos relacionados à autenticação e autorização de usuários. Você pode gerenciar os dados relacionados aos usuários, grupos e permissões.

**3. Configurações do Sistema**:
- Onde você pode realizar ações administrativas, como processos em massa

**4. Usuários**:
- Onde você pode gerenciar os dados relacionados aos usuários, como informações pessoais, permissões e turmas.

## 📚 Aprendizado

### Avaliações

Neste modelo, você pode gerenciar as avaliações disponíveis no sistema. Você pode criar, editar e excluir avaliações, além de visualizar os detalhes de cada uma delas.

Você pode adicionar uma nova avaliação clicando no botão "Adicionar Avaliação" e preenchendo os campos obrigatórios.

Muitos campos são auto explicativos, mas aqui estão alguns detalhes adicionais:

- Ativo, Inicio e Fim são campos que indicam a disponibilidade daquela avaliação.

- Pool: Você pode selecionar um pool de questões para a avaliação. O pool de questões é um conjunto de questões que podem ser utilizadas na avaliação. Você pode criar pools de questões no modelo "Banco de Questões".

- Na seção Configurações estão presentes os campos de configuração do Teste Adaptativo. Todos esses campos serão enviados para a API do MIRT quando um usuário for iniciar uma avaliação. Você pode configurar o número de questões, o número de tentativas, o tempo máximo para a avaliação e outras opções.


### Bancos de Questões

Neste modelo, você pode gerenciar os bancos de questões disponíveis no sistema. Você pode criar, editar e excluir bancos de questões, além de visualizar os detalhes de cada um deles.

Um Banco de Questões é um conjunto de questões que podem ser utilizadas em avaliações. Você pode adicionar questões a um banco de questões clicando no botão "Adicionar Questão" e preenchendo os campos obrigatórios.

- É um Super Pool?: Essa é uma opção que simplesmente indica se o banco de questões é um super pool. Um super pool é um banco de questões que contém inúmeras questões e é criado quando questões são importadas por um processo em massa.

### Dados de Design MIRT

Este modelo contém uma visualização simples do desempenho dos alunos em cada avaliação. Não é possível editar ou excluir os dados desse modelo, pois eles são gerados automaticamente pelo sistema assim que um usuário finaliza uma avaliação.

### Questões

Neste modelo, você pode gerenciar as questões disponíveis no sistema. Você pode criar, editar e excluir questões, além de visualizar os detalhes de cada uma delas.

Muitos campos são auto explicativos, mas aqui estão alguns detalhes adicionais:

- Parâmetros IRT: Esses parâmetros são utilizados pelo MIRT para calcular as próximas questões com base em TRI.

### Super Bancos de Questões

É apenas um filtro para visualizar os super pools criados no sistema. Funciona exatamente como o modelo "Banco de Questões", mas apenas exibe os super pools.

## ⚙️ Configurações do Sistema

### Processos em Massa

Este modelo serve para executar ações administrativas em massa. Ao clicar no botão "Adicionar Processo em Massa", você pode escolher a ação que deseja executar e enviar os dados necessários para a execução do processo através de um arquivo. Todos os processos em massa que necessitam de arquivo, possuem um exemplo.

### Uploads Questões

Este modelo também serve para executar ações administrativas em massa, porém somente cadastro de questões. Ao clicar no botão "Adicionar Upload de Questões", você pode escolher o arquivo que deseja enviar e o sistema irá processar o arquivo e cadastrar as questões automaticamente.

O sistema possui exemplo de arquivos para cada tipo de upload. Você pode baixar os exemplos clicando neles.

Após o processo ser executado, um super pool de questões é criado e as questões são cadastradas nesse super pool.

## 👤 Usuários

### Alunos

Alunos e Usuários são o mesmo modelo, mas com filtros diferentes. O modelo "Alunos" possui um filtro para visualizar apenas os alunos do sistema. Os alunos são usuários que não possuem permissões administrativas e não podem acessar o painel administrativo.

### Turmas

Turmas são grupos de alunos que podem ser utilizados para organizar os alunos em grupos. Você pode criar, editar e excluir turmas, além de visualizar os detalhes de cada uma delas.

Dentro de cada turma, você pode adicionar alunos e gerenciar os dados dos alunos.

Além disso, você pode adicionar provas para cada turma. As provas adicionadas para cada turma são as provas que os alunos daquela turma podem realizar.

### Usuários

São todos os usuários do sistema. Você pode criar, editar e excluir usuários, além de visualizar os detalhes de cada um deles.

Os campos de usuário são auto explicativos, e criados pelo próprio Django, mas aqui estão alguns detalhes adicionais:

- Na aba permissões, o que define se um usuário possui acesso ou não ao painel administrativo é a permissão "Membro da equipe". Se o usuário não possuir essa permissão, ele não terá acesso ao painel administrativo.
