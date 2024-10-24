# Usar a imagem base do Python 3.9 (você pode ajustar a versão conforme necessário)
FROM python:3.9-slim

# Atualizar pacotes e instalar dependências necessárias para o Java
RUN apt-get update && apt-get install -y \
    default-jre \
    curl \
    && apt-get clean

# Definir o diretório de trabalho
WORKDIR /app

# Atualiza o pip para evitar problemas
RUN pip install --upgrade pip


# Instalar as bibliotecas Python necessárias
RUN  pip install \ 
	tabula-py \ 
	pandas \
	pdfplumber


#Comando para iniciar um shell interativo quando o container for executado
CMD ["tail", "-f", "/dev/null"]

