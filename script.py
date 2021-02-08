import re
import requests as rq
import bs4
import time
import json

# url das paginas que serão coletados os dados
URL = "https://www.amigonaosecompra.com.br/?pet_query%5Bspecie_eq%5D=&pet_query%5Bsize_eq%5D=&pet_query%5Bstate_id_eq%5D=&pet_query%5Bcity_id_eq%5D=&pet_query%5Badopted_eq%5D=&pet_query%5Bname_like%5D=&page={page}"

# loop download 

for page in range(1,800):
    url = URL.format(page=page)
    response = rq.get(url)
    
    parsed = bs4.BeautifulSoup(response.text)
    
    listagem = parsed.find('ul', id="pet-list-search")
            
    links = listagem.findAll('a')
    
    for link in links:
        response = rq.get("https://www.amigonaosecompra.com.br" + link['href'])
        pagina = bs4.BeautifulSoup(response.text)
        try:
            nome_do_bichinho = pagina.find('h2', class_='pull-left').get_text()
            local = pagina.find(text=re.compile("Está em"))
            cidade = re.search(r'Está em (.*?) /', local).group(1)
            estado = local.split('/')[1]
            data_publicacao = pagina.find(text=re.compile("Essa fofurinha foi publicada em"))
            data = data_publicacao.split('em')[1]

            dados = pagina.find('ul', class_='pet-check')
            for dado in dados.findAll('li'):
                if 'Sexo' in dado.get_text():
                    sexo = dado.get_text().split(':')[1]
                elif 'Porte' in dado.get_text():
                    porte = dado.get_text().split(':')[1]
                else:
                    especie = dado.get_text()

            visitas = pagina.find('span', class_="highlight-text").get_text()
            
            adotado = 0
            
            if pagina.find('div', class_="ribbon").get_text() == "Adotado":
                adotado = 1
                
            with open("animais_scrap.json", "a+") as output:
                data = {"nome":nome_do_bichinho,"cidade":cidade,"estado":estado,
                        "data":data,"especie":especie,"sexo":sexo,"porte":porte,
                        "qtd_visitas":visitas, "adotado": adotado}
                output.write("{}\n".format(json.dumps(data)))
        except AttributeError:
            pass
    print("Página: " + str(page) + " de 800")
    time.sleep(1)