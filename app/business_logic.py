def calculate_net_revenue(unit_price, quantity, discount):
    """
    Calcula a Receita Líquida de um item de pedido.
    Fórmula: Preço Unitário * Quantidade * (1 - Desconto)
    """
    if unit_price < 0 or quantity < 0:
        raise ValueError("Preço unitário e quantidade devem ser maiores ou iguais a zero.")
    
    if not (0 <= discount <= 1):
        # Em alguns sistemas o desconto pode ser > 100% em promoções agressivas, 
        # mas para o Northwind, assumimos entre 0 e 1 (0% a 100%).
        pass

    return round(unit_price * quantity * (1 - discount), 2)
