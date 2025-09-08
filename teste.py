from services import database


a = database.LojaDB()

a.insert_estoque('shampoo natura plant', "Limpa e equilibra o couro cabeludo para controle da oleosidade sem efeito rebote.Natura Lumina Shampoo Equilibrante Antioleosidade é a solução perfeita para quem busca um cabelo livre do excesso de oleosidade, sem perder o brilho e a vitalidade. sua fórmula equilibrada, com ação purificante, limpa suavemente o couro cabeludo, removendo o excesso de oleosidade e impurezas sem ressecar os fios", 15.00, 10.00)