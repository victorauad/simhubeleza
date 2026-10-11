# -*- coding: utf-8 -*-
import re
_ACC = {
 'sessao': 'sessão', 'Sessao': 'Sessão', 'posicao': 'posição', 'Posicao': 'Posição', 'Nivel': 'Nível', 'nivel': 'nível',
 'Pressao': 'Pressão', 'pressao': 'pressão', 'Combustivel': 'Combustível', 'combustivel': 'combustível', 'Distribuicao': 'Distribuição',
 'mao': 'mão', 'referencia': 'referência', 'Maximo': 'Máximo', 'maximo': 'máximo', 'Minimo': 'Mínimo', 'minimo': 'mínimo',
 'Media': 'Média', 'media': 'média', 'medio': 'médio', 'Configuracao': 'Configuração', 'configuracao': 'configuração', 'Codigo': 'Código', 'codigo': 'código',
 'Distancia': 'Distância', 'distancia': 'distância', 'Aceleracao': 'Aceleração', 'aceleracao': 'aceleração', 'variacao': 'variação',
 'Ignicao': 'Ignição', 'Angulo': 'Ângulo', 'vacuo': 'vácuo', 'instantaneo': 'instantâneo', 'Indice': 'Índice', 'padrao': 'padrão',
 'Versao': 'Versão', 'expressoes': 'expressões', 'Expressoes': 'Expressões', 'Formulas': 'Fórmulas', 'formulas': 'fórmulas',
 'notificacao': 'notificação', 'Titulo': 'Título', 'Duracao': 'Duração', 'duracao': 'duração', 'Frequencia': 'Frequência',
 'atualizacao': 'atualização', 'Ha': 'Há', 'Ultima': 'Última', 'ultima': 'última', 'ultimo': 'último', 'Ultimo': 'Último',
 'cardiaco': 'cardíaco', 'Numero': 'Número', 'numero': 'número', 'esta': 'está', 'nao': 'não', 'NAO': 'NÃO', 'so': 'só',
 'usuario': 'usuário', 'circulo': 'círculo', 'nucleo': 'núcleo', 'disponivel': 'disponível', 'fracao': 'fração', 'excluido': 'excluído',
 'comeca': 'começa', 'inicio': 'início', 'acao': 'ação', 'execucao': 'execução', 'funcoes': 'funções', 'relacao': 'relação',
 'Diferenca': 'Diferença', 'traçado': 'traçado', 'Proximo': 'Próximo', 'tracao': 'tração', 'expressao': 'expressão', 'Nao': 'Não', 'pneu': 'pneu',
}
_RX = re.compile(r'(?<![\wÀ-ÿ])(' + '|'.join(map(re.escape, sorted(_ACC, key=len, reverse=True))) + r')(?![\wÀ-ÿ])')
def acc(s):
    return _RX.sub(lambda m: _ACC[m.group(1)], s)
