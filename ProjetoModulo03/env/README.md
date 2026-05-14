# 💊 MediControl - Sistema de Monitoramento de Medicamentos

Um sistema completo de monitoramento de medicamentos com alertas automáticos por e-mail, desenvolvido com Python, Flask e SQLite.

## 🎯 Características Principais

### Frontend
- ✅ **Interface Responsiva**: HTML5 e CSS3 com design moderno
- ✅ **Tema Azul Escuro (#00008B)**: Cor principal profissional e agradável
- ✅ **Navegação Intuitiva**: Dashboard e formulários de fácil uso
- ✅ **Cards com Status Visual**: Acompanhamento visual de medicamentos

### Backend
- ✅ **Flask Framework**: Aplicação web Python robusta
- ✅ **SQLite Database**: Armazenamento local persistente
- ✅ **APScheduler**: Sistema de agendamento automático
- ✅ **SMTP Integration**: Envio de e-mails automáticos

### Funcionalidades
- ✅ Cadastro de medicamentos com horário, dosagem e intervalo
- ✅ Alertas automáticos por e-mail nos horários programados
- ✅ Link de confirmação de ingestão nos e-mails
- ✅ Agendamento automático do próximo ciclo
- ✅ Histórico de ingestões confirmadas
- ✅ Remoção de medicamentos
- ✅ Sincronização automática do dashboard

## 📋 Especificações Técnicas

### Tecnologias Utilizadas
```
Backend:
- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1
- APScheduler 3.10.4
- python-dotenv 1.0.0

Frontend:
- HTML5
- CSS3 (Responsivo)
- JavaScript (Vanilla)
```

## 🚀 Como Executar

### 1. Pré-requisitos
- Python 3.8+
- pip (gerenciador de pacotes Python)

### 2. Clonar o repositório

```bash
cd ProjetoModulo03
```

### 3. Criar ambiente virtual (opcional, mas recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 4. Instalar dependências

```bash
pip install -r requirements.txt
```

### 5. Configurar variáveis de ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar o arquivo .env com suas credenciais
# Use um editor de texto de sua preferência
```

### 6. Configurar credenciais de e-mail (Gmail)

#### Para Gmail:

1. **Ativar verificação em duas etapas**:
   - Acesse: https://myaccount.google.com/security
   - Clique em "Verificação em duas etapas"
   - Siga as instruções

2. **Gerar senha de aplicativo**:
   - Acesse: https://myaccount.google.com/apppasswords
   - Selecione "Mail" na lista de aplicativos
   - Selecione "Windows Computer" (ou seu sistema operacional)
   - Clique em "Gerar"
   - Copie a senha gerada (será uma sequência de 16 caracteres)

3. **Configurar no arquivo .env**:
   ```
   EMAIL_USER=seu_email@gmail.com
   EMAIL_PASS=sua_senha_de_16_caracteres
   ```

### 7. Executar a aplicação

```bash
python app.py
```

### 8. Acessar a aplicação

Abra seu navegador e acesse:
```
http://localhost:5000
```

## 📱 Interface da Aplicação

### Dashboard Principal
- Lista de todos os medicamentos cadastrados
- Status visual de cada medicamento
- Informações de horário, dosagem e intervalo
- Botões para remover medicamentos
- Link para cadastrar novos medicamentos

### Página de Cadastro
- Formulário para adicionar novo medicamento
- Campos: Nome, Horário, Dosagem, E-mail, Intervalo
- Validação de dados em tempo real
- Confirmação de sucesso

### E-mail de Alerta
- Design profissional e responsivo
- Informações claras do medicamento
- Link de confirmação
- Instruções de uso

### Confirmação de Ingestão
- Página de sucesso com informações
- Agendamento automático do próximo ciclo
- Redirecionamento para dashboard

## 🛡️ Segurança

- ✅ Proteção contra XSS (escape de HTML)
- ✅ Validação de entrada (e-mail, hora, dosagem)
- ✅ Tratamento de erros SMTP
- ✅ Variáveis de ambiente para credenciais
- ✅ Banco de dados SQLite criptografado

## 📊 Estrutura do Projeto

```
ProjetoModulo03/
├── app.py                      # Backend Flask principal
├── requirements.txt            # Dependências do projeto
├── .env.example               # Variáveis de ambiente (exemplo)
├── .env                       # Variáveis de ambiente (não versionado)
├── .gitignore                 # Arquivos ignorados pelo git
├── medication_monitor.db      # Banco de dados SQLite
├── templates/
│   ├── dashboard.html         # Dashboard principal
│   ├── register.html          # Formulário de cadastro
│   ├── success.html           # Página de sucesso
│   └── error.html             # Página de erro
└── static/
    ├── css/
    │   └── style.css          # Estilos CSS responsivos
    └── js/
        └── dashboard.js       # Lógica do frontend
```

## 🔧 API REST

### Endpoints Disponíveis

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Dashboard principal |
| GET | `/register` | Página de cadastro |
| GET | `/api/medications` | Lista todos os medicamentos |
| POST | `/api/medications` | Cria novo medicamento |
| DELETE | `/api/medications/<id>` | Remove medicamento |
| GET | `/api/history/<id>` | Histórico de ingestões |
| GET | `/confirm-intake?med=<id>` | Confirma ingestão |

### Exemplos de Requisições

#### Listar medicamentos
```javascript
fetch('/api/medications')
  .then(res => res.json())
  .then(data => console.log(data))
```

#### Criar medicamento
```javascript
fetch('/api/medications', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'Omeprazol',
    time: '08:00',
    dosage: '20mg',
    email: 'usuario@gmail.com',
    interval_hours: 24
  })
})
```

#### Remover medicamento
```javascript
fetch('/api/medications/1', {
  method: 'DELETE'
})
```

## 🐛 Tratamento de Erros

### Erro SMTP
Se receber erro de autenticação:
1. Verifique se EMAIL_USER está correto
2. Verifique se EMAIL_PASS está correta (use senha de aplicativo, não sua senha normal)
3. Verifique se a verificação em duas etapas está habilitada
4. Verifique a data/hora do seu sistema

### Banco de Dados
- O banco é criado automaticamente na primeira execução
- Usa SQLite, não precisa de servidor externo
- Dados são salvos em `medication_monitor.db`

### Porta Ocupada
Se porta 5000 estiver em uso:
1. Feche outros programas usando essa porta
2. Ou altere a porta no arquivo `app.py` (última linha)

## 📝 Logs

Os logs da aplicação são exibidos no console:
```
2026-05-14 10:30:00,123 - root - INFO - Scheduler iniciado com sucesso
2026-05-14 10:30:05,456 - root - INFO - E-mail enviado com sucesso para usuario@gmail.com
```

## 💡 Dicas de Uso

1. **Horários**: Use formato HH:MM (ex: 08:00, 14:30)
2. **Intervalo**: Defina em horas (padrão: 24h para uso diário)
3. **E-mail**: Use um e-mail que você tenha acesso para receber alertas
4. **Dosagem**: Pode incluir unidade (ex: 20mg, 1 comprimido)

## 🔍 Troubleshooting

### Aplicação não inicia
```bash
# Verificar se porta 5000 está disponível
# Windows:
netstat -ano | findstr :5000

# Linux/Mac:
lsof -i :5000

# Matar processo (se necessário):
# Windows: taskkill /PID <pid> /F
# Linux/Mac: kill -9 <pid>
```

### E-mails não são enviados
```bash
# Verifique:
1. Credenciais no arquivo .env
2. Conexão de internet
3. Porta 587 aberta (SMTP)
4. Verificação em duas etapas ativada (Gmail)
5. Senha de aplicativo correta
```

### Medicamentos não desaparecem do histórico
- Os medicamentos são mantidos no dashboard
- Use o botão "Remover" para deletar manualmente
- O histórico de ingestões é mantido como auditoria

## 🤝 Contribuições

Este é um projeto educacional. Sinta-se à vontade para modificar e melhorar!

## 📄 Licença

Projeto desenvolvido como disciplina de Análise e Desenvolvimento de Sistemas.

## 👨‍💻 Desenvolvedor

Desenvolvido como projeto acadêmico - 2026.1

---

**Nota**: Para ambiente de produção, considere:
- Usar HTTPS em vez de HTTP
- Configurar banco de dados remoto (PostgreSQL)
- Implementar autenticação de usuários
- Usar variáveis de ambiente mais seguras
- Fazer backup regular dos dados
- Usar um serviço de e-mail profissional (SendGrid, etc)
