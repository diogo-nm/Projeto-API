from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from fastapi import FastAPI, HTTPException

#Criação de um banco de dados para armazenar um cliente 
class Cliente(BaseModel):
    id: int
    nome: str = Field(max_length=20)
    tipo_atendimento: str = Field(max_length= 1, pattern='^[NP]$')
    data_chegada: datetime
    atendido: bool = False

class ClienteCreate(BaseModel):
    nome: str = Field(max_length=20)
    tipo_atendimento: str = Field(max_length=1, pattern='^[NP]$')

app = FastAPI()

fila = []

#mostrar todos os clientes ainda não atendidos na fila
@app.get('/fila')
async def get_fila():
    fila_nao_atendida = [cliente for cliente in fila if not cliente.atendido]
    return fila_nao_atendida

#pegar um cliente em específico da fila
@app.get('/fila/{id}')
async def get_cliente(id: int):
    for cliente in fila:
        if cliente.id == id:
            return cliente
    raise HTTPException(status_code=404, detail='Cliente não encontrado na posição especifica')

#adicionar um cliente na fila
@app.post('/fila')
async def add_cliente(cliente: ClienteCreate):
    id_novo_cliente = len(fila) + 1
    novo_cliente = Cliente(
        id = id_novo_cliente,
        nome = cliente.nome,
        tipo_atendimento = cliente.tipo_atendimento,
        data_chegada = datetime.now()
    )
    
    if cliente.tipo_atendimento == "P":
        fila.insert(0, novo_cliente)
    else:
        fila.append(novo_cliente)

    for index, cliente in enumerate(fila):
        cliente.id = index + 1
    
    return novo_cliente

#sistema de atendimento do cliente, tirando-o da fila
@app.put("/fila")
async def update_fila():
    if not fila:
        raise HTTPException(status_code=404, detail="Fila está vazia")

    # Marcar o primeiro cliente como atendido
    if not fila[0].atendido:
        fila[0].atendido = True

    # Remover o primeiro cliente da fila e atualizar as posições dos restantes
    fila.pop(0)

    for index, cliente in enumerate(fila):
        cliente.id = index + 1

    return fila

#deletar um cliente específico
@app.delete("/fila/{id}")
async def delete_cliente(id: int):
    global fila
    cliente_index = None
    for index, cliente in enumerate(fila):
        if cliente.id == id:
            cliente_index = index
            break

    if cliente_index is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado na posição especificada")
    
    del fila[cliente_index]
    for i in range(cliente_index, len(fila)):
        fila[i].id -= 1
    
    # Reatribuir IDs para manter a ordem correta
    for index, cliente in enumerate(fila):
        cliente.id = index + 1
    
    return {"message": "Cliente removido com sucesso"}  
