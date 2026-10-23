# Projeto de Auditoria de Timeline

## Sobre o projeto

Este projeto foi desenvolvido no escopo de uma pesquisa acadêmica voltada à **auditoria de mecanismos de recomendação utilizados na construção da timeline de usuários do TikTok**.

O código permite configurar ambientes experimentais associados a diferentes usuários controlados (*sockpuppets*) e realizar a coleta automatizada de informações relacionadas à timeline apresentada pela plataforma.

O projeto tem finalidade exclusivamente **acadêmica e de pesquisa**, envolvendo estudos relacionados a:

* mecanismos de recomendação;
* auditoria de sistemas de inteligência artificial;
* segurança;
* ética em IA;
* programação;
* tecnologias Web;
* mecanismos de detecção de automação;
* análise de sistemas de recomendação.

O código não tem como finalidade produzir conteúdo ou propagar conteúdo de terceiros.

## Autoria

**Autores do projeto:**

* Tiago Cruz de França
* Jonice Oliveira
* Daniel Sadoc
* Eduardo Hargreaves

**Programador:** Tiago Cruz de França

## Condições de uso

Este código é **privado** e seu uso depende de autorização dos autores.

A disponibilização ou utilização do código não implica autorização automática para sua utilização em outros projetos, pesquisas ou finalidades.

O código constitui uma ferramenta para pesquisa acadêmica. Sua utilização depende de procedimentos e configurações realizados pelo usuário responsável pela execução, incluindo a criação e configuração das contas, dispositivos e ambientes experimentais.

O usuário que executar o código é responsável por sua utilização, pelas contas utilizadas, pelos dados coletados e pela observância da legislação aplicável, das políticas institucionais e dos termos de uso dos serviços envolvidos.

---

# 1. Estrutura do projeto

O projeto foi desenvolvido para permitir a execução de **múltiplos sockpuppets de forma independente**.

Recomenda-se criar uma estrutura semelhante à seguinte:

```text
./projeto-audit-timeline/
│
├── tiktok/
│   │
│   ├── sock_bob/
│   │   └── todos os scripts e arquivos relacionados ao sockpuppet Bob
│   │
│   └── sock_ana/
│       └── todos os scripts e arquivos relacionados ao sockpuppet Ana
│
└── instagram/
    │
    ├── sock_bob/
    │   └── todos os arquivos relacionados ao sockpuppet Bob
    │
    └── sock_ana/
        └── todos os arquivos relacionados ao sockpuppet Ana
```

Cada sockpuppet deve possuir um **diretório exclusivo**, evitando o compartilhamento de arquivos de sessão, dados do navegador e dados de coleta entre diferentes usuários experimentais.

O nome do diretório pode seguir o padrão:

```text
sock_[NOME_SOCKPUPPET]
```

Por exemplo:

```text
sock_ana
sock_bob
sock_sergio
```

A estrutura foi concebida para permitir a existência de **N sockpuppets independentes** dentro do projeto.

---

# 2. Preparação do ambiente

Crie a pasta destinada ao projeto e coloque todos os arquivos fornecidos dentro dela.

Assegure que o usuário responsável pela execução possua **permissão de leitura e escrita** nas pastas utilizadas pelo projeto.

Recomenda-se verificar também se existe espaço suficiente em disco, pois o projeto pode produzir arquivos de sessão e dados de coleta ao longo de sua execução.

---

# 3. Dependências

O projeto utiliza Python 3 (compatível do Python 3.8 ao 3.12+), Playwright e suporte a TOML multi-versão[cite: 11, 12].

O arquivo `requirements.txt` do projeto contém as seguintes dependências:

```text
playwright>=1.40.0
playwright-stealth>=1.0.6
tomli>=1.1.0; python_version < "3.14"
```


Instale as dependências a partir do diretório principal do projeto:

```bash
python -m pip install -r requirements.txt
```

Em seguida, instale o navegador Chromium utilizado pelo Playwright:

```bash
python -m playwright install chromium
python -m playwright install-deps
```

Por fim, instale as dependências necessárias para execução do Chromium:

```
sudo apt update
sudo apt install -y chromium-browser libgbm-dev libnss3 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libasound2
```
```bash
playwright install-deps
```

Execute os três comandos sequencialmente.

---

# 4. Preparação da conta

Para configurar um sockpuppet no TikTok, será necessário possuir:

* um número de telefone;
* um dispositivo móvel com WhatsApp;
* um endereço de e-mail;
* uma conta no TikTok criada para o ambiente experimental.

A conta deve ser criada utilizando o dispositivo móvel.

Associe à conta o endereço de e-mail e o número de telefone utilizados no experimento.

Antes da execução do processo de configuração, mantenha o aplicativo do TikTok **logado no dispositivo móvel**.

O perfil experimental deve ser configurado de acordo com os parâmetros definidos para o experimento, incluindo as informações de perfil pertinentes ao desenho experimental.

> **Importante:** os dados utilizados na configuração de cada sockpuppet devem ser mantidos separados dos demais sockpuppets.

---

# 5. Configuração inicial do sockpuppet

Utilizando Python 3, execute:

```bash
python sockpuppetRun.py
```

Na primeira execução, o programa iniciará o processo de configuração do sockpuppet.

Será solicitado um nome para o sockpuppet.

Recomenda-se utilizar o mesmo nome associado ao perfil experimental do TikTok e manter os nomes **únicos dentro do projeto**.

Exemplos:

```text
ana
joao
sergio
patati
patata
```

Os nomes devem:

* começar com uma letra;
* utilizar letras e números;
* não utilizar caracteres especiais;
* ser únicos dentro do projeto;
* ser suficientemente significativos para permitir sua identificação posteriormente.

Por exemplo:

```text
ana01
joao02
sergio01
```

é preferível a nomes arbitrários ou difíceis de identificar.

---

# 6. Autenticação no TikTok

Durante a primeira configuração, o navegador do TikTok será aberto.

## 6.1 Login utilizando QR Code

Quando apresentada a opção de autenticação, escolha:

**Ler QR Code no navegador**

Utilize a câmera do dispositivo móvel para ler o QR Code apresentado pelo navegador.

Após a leitura, o TikTok poderá solicitar uma confirmação adicional de identidade.

---

## 6.2 Confirmação pelo dispositivo móvel

Uma janela de confirmação de login será apresentada.

Escolha a opção para confirmar o acesso utilizando o celular.

O TikTok poderá enviar um código de confirmação de **6 dígitos** por:

* WhatsApp;
* SMS.

Durante os testes realizados neste projeto, o recebimento por WhatsApp foi o comportamento mais frequente, enquanto o recebimento por SMS ocorreu ocasionalmente.

A mensagem de confirmação pode ser enviada por uma conta do WhatsApp cujo nome contenha `Infinity`, como, por exemplo:

```text
InfinityAuth
```

### Atenção ao tempo de expiração

O código possui tempo limitado para utilização.

Assim que o código de 6 dígitos for recebido, insira-o no navegador.

Caso o código expire, será necessário reiniciar o processo de autenticação.

---

# 7. Configuração do sockpuppet

Depois que o login for confirmado, siga as instruções apresentadas pelo arquivo de configuração do sockpuppet.

Configure o ambiente de acordo com as condições definidas para o experimento.

Quando aplicável, siga os perfis/contas determinados pelo protocolo experimental.

É importante que as configurações realizadas sejam registradas de acordo com o protocolo da pesquisa, permitindo posteriormente relacionar cada coleta ao respectivo sockpuppet e às suas condições experimentais.

---

# 8. Início da coleta

Após concluir a configuração do sockpuppet, retorne ao terminal e pressione:

```text
Enter
```

Essa ação encerrará o navegador utilizado durante a etapa de configuração.

Em seguida, o programa iniciará uma nova instância do navegador destinada à coleta.

A primeira coleta da timeline será iniciada automaticamente.

Os arquivos e diretórios necessários para a execução serão criados seguindo a estrutura padrão do projeto e utilizando o nome atribuído ao sockpuppet.

---

# 9. Periodicidade da coleta

Após a configuração inicial, o sistema realizará novas coletas da timeline periodicamente.

A periodicidade atualmente configurada é de:

```text
1 hora
```

Esse intervalo é um **parâmetro do sistema** e pode ser alterado conforme o protocolo experimental.

---

# 10. Reinicialização após interrupção

Caso o processo seja interrompido por:

* queda de energia;
* encerramento inesperado do programa;
* reinicialização do computador;
* outro problema durante a execução;

basta executar novamente:

```bash
python sockpuppetRun.py
```

O programa verificará a existência da sessão previamente configurada.

Caso a sessão ainda exista, o sistema deverá identificar que o ambiente já foi configurado e iniciar novamente o processo de coleta **sem solicitar um novo login**.

---

# 11. Reconfiguração completa do ambiente

**Evite realizar este procedimento sem necessidade.**

Caso seja necessário forçar a reconfiguração completa da sessão, deverão ser removidos os arquivos e diretórios associados à sessão do sockpuppet.

Entre eles:

```text
navegador_dados_[nome_sockpuppet]
tiktok_session_[nome_sockpuppet]
```

Por exemplo:

```text
navegador_dados_ana
tiktok_session_ana
```

A remoção desses elementos fará com que o ambiente seja tratado como uma nova configuração.

Depois disso, execute novamente:

```bash
python sockpuppetRun.py
```

e repita o processo de autenticação descrito anteriormente.

> **ATENÇÃO:** esses arquivos podem conter informações persistentes de sessão. Não os remova ou compartilhe sem verificar primeiro o impacto sobre o ambiente experimental.

---

# 12. Arquivos de sessão e dados experimentais

Os arquivos criados durante a execução podem conter informações relacionadas à sessão do navegador, configuração do ambiente experimental e dados coletados.

Por esse motivo:

* não compartilhe arquivos de sessão;
* não publique credenciais;
* não inclua dados pessoais desnecessários em repositórios;
* não envie diretórios de perfil do navegador para repositórios públicos;
* mantenha os dados experimentais armazenados de acordo com as regras do projeto de pesquisa.

---

# 13. `.gitignore`

Recomenda-se utilizar um `.gitignore` para impedir que arquivos de sessão, dados coletados, caches e arquivos temporários sejam adicionados acidentalmente ao controle de versão.

Uma configuração inicial pode ser:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class

# Ambientes virtuais
.venv/
venv/
env/

# IDEs
.vscode/
.idea/

# Sistema operacional
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Dados de coleta
snapshots/
data/
dados/
output/
outputs/

# Sessões e dados persistentes do navegador
navegador_dados_*/
tiktok_session_*/

# Perfis/dados locais dos sockpuppets
sockpuppets/*/navegador_dados_*/
sockpuppets/*/tiktok_session_*/

# Arquivos temporários
*.tmp
*.temp

# Arquivos locais de configuração
.env
.env.*
```

Caso os diretórios de dados sejam necessários para documentação, resultados experimentais ou reprodução de uma análise, eles podem ser versionados seletivamente em vez de ignorados integralmente.

**Nunca coloque no repositório arquivos contendo credenciais, tokens, cookies ou sessões autenticadas.**

---

# 14. Execução

Após a instalação e configuração inicial, a execução pode ser iniciada com:

```bash
python sockpuppetRun.py
```

Na primeira execução, o sistema realizará a configuração e autenticação do sockpuppet.

Nas execuções seguintes, desde que a sessão persistente esteja disponível, o sistema poderá reutilizar o ambiente previamente configurado.

---

# 15. Finalidade acadêmica

Este software integra um projeto de pesquisa dedicado à investigação de mecanismos de recomendação e à auditoria de sistemas utilizados na composição de timelines personalizadas.

O objetivo é possibilitar a realização de experimentos controlados nos quais diferentes configurações de usuários experimentais possam ser utilizadas para observar e analisar o comportamento do sistema de recomendação.

O software não possui como finalidade:

* produzir conteúdo;
* publicar conteúdo de terceiros;
* promover conteúdo de terceiros;
* realizar atividades de interação não previstas no protocolo experimental;
* substituir a análise científica dos dados coletados.

A utilização do software deve estar vinculada ao protocolo e às finalidades da pesquisa para a qual foi desenvolvido.

---

# 16. Licença e autorização

Este código é de uso privado.

A utilização, reprodução, modificação ou redistribuição do código depende de autorização dos autores:

* **Tiago Cruz de França**
* **Jonice Oliveira**
* **Daniel Sadoc**
* **Eduardo Hargreaves**

A autorização para utilização do código não constitui, por si só, autorização para utilização das contas, dados, credenciais ou ambientes experimentais utilizados pelos autores.

---

# 17. Contato e desenvolvimento

**Projeto:** Auditoria de mecanismos de recomendação em timelines

**Programador:** Tiago Cruz de França

**Autores:** Tiago Cruz de França, Jonice Oliveira, Daniel Sadoc e Eduardo Hargreaves

---

