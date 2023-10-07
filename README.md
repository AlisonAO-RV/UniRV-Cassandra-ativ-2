# UniRV-Cassandra-ativ-2

## Aluno: Alison Alain de Oliveira

# Como executar o projeto

## Pré-requisitos

- BANCO DE DADOS CASSANDRA
- DOCKER ou CASSANDRA LOCAL
- PYTHON 3.11

## Instalação do Cassandra no Docker

docker run --name cassandra -p 9042:9042 -d cassandra:latest

## Acessando o Cassandra no Docker

docker exec -it cassandra bash

## Acessando o cqlsh no Docker

docker exec -it cassandra cqlsh

# PYTHON 3.11

## Instalação do Python

local ou maquina virtual ( venve, pyenv, anaconda, etc)

## Instalação das dependências

pip install -r requirements.txt

# Atividade:

Objetivo: Criar uma lista básica de tarefas usando Cassandra ou outro banco de dados do tipo colunar.

Indivudual
Linguagem de programação: Python ou outra.
Banco de dados do tipo colunar: Cassandra ou outro

Configuração Inicial

Instale e configure o banco para execução local.
Crie um novo projeto em Python e instale a biblioteca que permite acessar o banco.
Modelagem de Dados

Cada tarefa terá um ID único.
Armazene ao título e descrção da tarefa.
Funcionalidades

Adicionar Tarefa: Permita que o usuário adicione uma tarefa fornecendo o título e sua descrição.
Listar Tarefas: Exiba todas as tarefas armazenadas, mostrando seus IDs e títulos.
Visualiar Descrição da Tarefa: Após listar as tarefas pelo título, mostre uma opção que permita visualizar a descrição da tarefa.
Remover Tarefa: Permita que o usuário remova uma tarefa pelo ID.

## Print do projeto

![print](/images/tela_01.png)
![print](/images/tela_02.png)
