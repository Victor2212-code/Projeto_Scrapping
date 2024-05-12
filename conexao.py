from flask import Flask, render_template, request
from index import get_product_data, configs  # Importando a função e configurações necessárias

app = Flask(__name__)

# Lista de supermercados e suas configurações
supermarkets = [
    {
        'url': 'https://www.sitemercado.com.br/supermercadolavilla/ourinhos-loja-ourinhos-jardim-matilde-r-do-expedicionario/',
        'config': configs['supermercadoC']
    },
    {
        'url': 'https://loja.supermercadosavenida.com.br',
        'config': configs['supermercadoA']  # As configurações devem estar definidas em 'configs'
    }
]

@app.route('/', methods=['GET', 'POST'])
def index():
    search_term = None  # Inicializa sem termo de busca
    all_products = []  # Lista vazia para produtos

    if request.method == 'POST':
        search_term = request.form['search_term']
    elif request.method == 'GET' and 'search_term' in request.args:
        search_term = request.args.get('search_term')

    # Executar a busca somente se um termo de busca foi fornecido
    if search_term:
        for market in supermarkets:
            products = get_product_data(market['url'], search_term, market['config'])
            all_products.extend(products)  # Agrega os produtos de cada URL na lista total
    
    # Renderiza a página com os produtos ou vazia se nenhum termo foi buscado ainda
    return render_template('index.html', products=all_products, search_term=search_term or "")

if __name__ == "__main__":
    app.run(debug=True,  port=8080)