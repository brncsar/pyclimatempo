import requests
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from datetime import datetime
import tkinter as tk

# Função para obter a resolução da tela
def get_screen_resolution():
    root = tk.Tk()
    root.withdraw()  # Esconde a janela principal do tkinter
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.destroy()
    return width, height

# Função para obter a previsão diária
def get_daily_forecast(iTOKEN):
    url = f"http://apiadvisor.climatempo.com.br/api/v1/forecast/locale/7564/days/15?token={iTOKEN}"  # Novo endpoint
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Erro na requisição: {response.status_code} - {response.text}")
        return []

    forecast_data = response.json()

    # Verifica se a resposta contém dados esperados
    if 'data' in forecast_data:
        return forecast_data['data']  # Retorna apenas os dados diários
    else:
        print("Erro ao buscar a previsão diária:", forecast_data.get('detail', 'Erro desconhecido'))
        return []

# Função para gerar a imagem com os dados do clima
def generate_weather_image(data, daily_forecast):
    screen_width, screen_height = get_screen_resolution()

    # Carregar a imagem e redimensiona para a resolução da tela
    background = Image.open("assets/backnight.jpg")
    background = background.resize((screen_width, screen_height))
    
    img = Image.new('RGB', (screen_width, screen_height))
    img.paste(background, (0, 0))
    d = ImageDraw.Draw(img)

    # Carrega fontes para diferentes tamanhos de texto
    try:
        font_large = ImageFont.truetype("arial.ttf", 70)
        font_medium = ImageFont.truetype("arial.ttf", 40)
        font_small = ImageFont.truetype("arial.ttf", 25)
    except IOError:
        font_large = font_medium = font_small = ImageFont.load_default()

    # Exibe a temperatura principal
    temperature = f"{data['data']['temperature']}°C"
    temp_bbox = d.textbbox((0, 0), temperature, font=font_large)
    d.text(((screen_width - (temp_bbox[2] - temp_bbox[0])) / 2, 70), temperature, fill="lightblue", font=font_large)

    # Carrega o ícone de temperatura
    try:
        temp_icon = Image.open("assets/icon_moon.png").resize((70, 70), Image.Resampling.LANCZOS)
    except IOError:
        temp_icon = Image.new('RGBA', (70, 70), (0, 0, 0, 0))  # Ícone vazio se não encontrado

    # Posição do ícone e texto da temperatura
    icon_x = 800  # Centraliza o ícone e o texto
    icon_y = 50

    # Desenha o ícone e a temperatura
    img.paste(temp_icon, (int(icon_x), icon_y), temp_icon)
    

    # Exibe o nome da cidade e estado
    city_name = f"{data['name']}, {data['state']}"
    city_bbox = d.textbbox((0, 0), city_name, font=font_medium)
    d.text(((screen_width - (city_bbox[2] - city_bbox[0])) / 2, 180), city_name, fill="white", font=font_medium)

    # Exibe a condição climática
    condition = data['data']['condition']
    cond_bbox = d.textbbox((0, 0), condition, font=font_small)
    d.text(((screen_width - (cond_bbox[2] - cond_bbox[0])) / 2, 230), condition, fill="lightgray", font=font_small)

    # Dados adicionais formatados
    additional_info = [
        {"text": f"Umidade: {data['data']['humidity']}%", "icon": "assets/humidity.png"},
        {"text": f"Pressão: {data['data']['pressure']} hPa", "icon": "assets/pressure.png"},
        {"text": f"Vento: {data['data']['wind_velocity']} km/h {data['data']['wind_direction']}", "icon": "assets/wind.png"},
        {"text": f"Sensação Térmica: {data['data']['sensation']}°C", "icon": "assets/sensation.png"},
        {"text": f"Data: {data['data']['date']}", "icon": "assets/calendar.png"}
    ]

    # Exibe cada informação adicional com seu respectivo ícone
    x_offset = (screen_width - sum(d.textbbox((0, 0), info['text'], font=font_small)[2] for info in additional_info[:3]) - 140) / 2
    y_offset = 380

    for info in additional_info[:3]:
        icon = Image.open(info['icon']).resize((34, 34), Image.Resampling.LANCZOS)
        img.paste(icon, (int(x_offset), int(y_offset)), icon)
        d.text((x_offset + 30, y_offset), info['text'], fill="white", font=font_small)
        x_offset += d.textbbox((0, 0), info['text'], font=font_small)[2] + 70

    x_offset = (screen_width - sum(d.textbbox((0, 0), info['text'], font=font_small)[2] for info in additional_info[3:]) - 70) / 2
    y_offset += 40

    for info in additional_info[3:]:
        icon = Image.open(info['icon']).resize((24, 24), Image.Resampling.LANCZOS)
        img.paste(icon, (int(x_offset), int(y_offset)), icon)
        d.text((x_offset + 30, y_offset), info['text'], fill="white", font=font_small)
        x_offset += d.textbbox((0, 0), info['text'], font=font_small)[2] + 70

        dias_semana = {
        "Mon": "Seg", "Tue": "Ter", "Wed": "Qua", "Thu": "Qui", 
        "Fri": "Sex", "Sat": "Sáb", "Sun": "Dom"
    }
    # Adiciona a previsão diária
    y_offset = 800
    card_width = screen_width // 7 - 12  # Largura de cada card com espaço
    card_height = 250  # Altura do card
    card_spacing = 10  # Espaço entre os cards
    corner_radius = 15
    

    for idx, day in enumerate(daily_forecast):
        date_str = day['date_br']
        date_obj = datetime.strptime(date_str, "%d/%m/%Y")
        day_of_week_pt = dias_semana.get(date_obj.strftime("%a"), date_obj.strftime("%a"))
        day_and_month = date_obj.strftime("%d/%m")
        
        
        # Obtém a precipitação e as condições
        precip_value = day['rain']['precipitation']
        condition = day.get('text_icon', {}).get('text', {}).get('pt', 'Sem dados')

        # Lógica para escolher o ícone baseado nas condições climáticas
        if precip_value > 0:
            if "chuva" in condition.lower() and "noite" in condition.lower():
                icon_name = 'icon_night_rain'
            elif "nublado" in condition.lower():
                icon_name = 'icon_rain'
            else:
                icon_name = 'icon_default'
        else:
            if "sol" in condition.lower() or "claro" in condition.lower():
                icon_name = 'icon_sun'
            elif "nublado" in condition.lower():
                icon_name = 'icon_sun'
            else:
                icon_name = 'icon_default'

        icon_path = f"assets/{icon_name}.png"
        try:
            icon = Image.open(icon_path).resize((68, 68), Image.Resampling.LANCZOS)
        except IOError:
            icon = Image.open("assets/icon_default.png").resize((34, 34), Image.Resampling.LANCZOS)

        # Calcula a posição do card
        card_x = idx * (card_width + card_spacing) + 10
        card_y = y_offset
        
        # Recorta o fundo do card e aplica o desfoque
        card_background = img.crop((card_x, y_offset, card_x + card_width, y_offset + card_height))
        blurred_background = card_background.filter(ImageFilter.GaussianBlur(radius=13))

        # Cria uma camada transparente com o fundo desfocado
        card_layer = Image.new("RGBA", (card_width, card_height), (0, 0, 0, 0))
        card_layer.paste(blurred_background, (0, 0))

        # Desenha o contorno do card com bordas arredondadas
        draw_card = ImageDraw.Draw(card_layer)
        draw_card.rounded_rectangle(
            [0, 0, card_width, card_height],
            radius=corner_radius,
            outline=(255, 255, 255, 150),
            width=2
        )

        # Sobrepõe a camada transparente com o desfoque sobre a imagem principal
        img.paste(card_layer, (card_x, y_offset), card_layer)

        # Coordenadas centralizadas
        center_x = card_x + card_width // 2
        text_y_offset = card_y + 10

        # Insere os ícones e textos no card
        img.paste(icon, (card_x + 10, y_offset + 10), icon)

        # Exibe as temperaturas mínima e máxima
        min_temp = day['temperature']['min']
        max_temp = day['temperature']['max']
        temp_text = f"Min: {min_temp}°C, Max: {max_temp}°C"
        temp_bbox = d.textbbox((0, 0), temp_text, font=font_small)
        temp_x = center_x - (temp_bbox[2] - temp_bbox[0]) // 2
        d.text((temp_x, y_offset + 90), temp_text, fill="white", font=font_small)    
        
        
        # Centraliza o dia da semana
        day_of_week_bbox = d.textbbox((0, 0), day_of_week_pt, font=font_small)
        day_of_week_x = center_x - (day_of_week_bbox[2] - day_of_week_bbox[0]) // 2
        d.text((day_of_week_x, text_y_offset), day_of_week_pt, fill="white", font=font_small)
        text_y_offset += 30
        #d.text((card_x + 50, y_offset + 10), day_of_week_pt, fill="white", font=font_small)
       
        # Centraliza o dia do mês
        day_and_month_bbox = d.textbbox((0, 0), day_and_month, font=font_small)
        day_and_month_x = center_x - (day_and_month_bbox[2] - day_and_month_bbox[0]) // 2
        d.text((day_and_month_x, text_y_offset + 170), day_and_month, fill="white", font=font_small)

        # Centraliza a preciptação
        precip_text = f"{precip_value} mm"
        precip_bbox = d.textbbox((0, 0), precip_text, font=font_small)
        precip_x = center_x - (precip_bbox[2] - precip_bbox[0]) // 2
        d.text((precip_x, text_y_offset + 100), precip_text, fill="white", font=font_small)
        #d.text((card_x + 50, y_offset + 100), condition, fill="white", font=font_small)

        

    img.save("weather_image.png")

# URL e token da API
iTOKEN = "285b83f3f77172fb3628c75204dbe9a9"
iURL = f"http://apiadvisor.climatempo.com.br/api/v1/weather/locale/7564/current?token={iTOKEN}"

# Faz a requisição e processa os dados
iRESPONSE = requests.get(iURL)

if iRESPONSE.status_code != 200:
    print(f"Erro na requisição: {iRESPONSE.status_code} - {iRESPONSE.text}")
else:
    iRETORNO_REQ = json.loads(iRESPONSE.text)

    daily_forecast_data = get_daily_forecast(iTOKEN)

    if 'error' not in iRETORNO_REQ:
        generate_weather_image(iRETORNO_REQ, daily_forecast_data)
        print("Imagem gerada com sucesso: weather_image.png")
    else:
        print(iRETORNO_REQ['detail'])
