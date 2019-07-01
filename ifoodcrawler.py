import urllib.request, json
class IfoodCrawler:
    def __init__(self):
        self.base_headers = {
            'Accept' :  'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding' : 'identity;q=1',
            'Accept-Language':  'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection':   'keep-alive',
            'TE':   'Trailers',
            'Upgrade-Insecure-Requests':    '1',
            'User-Agent':   'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0'
        }

        self.host_marketplace = 'marketplace.ifood.com.br'
        self.host_api = 'www.ifood.com.br'

    def get_json(self, url, hdr):
        req = urllib.request.Request(url, headers=hdr)
        response = urllib.request.urlopen(req)
        return json.loads(response.read().decode('utf-8'))

    def get_merchants(self, latitude, longitude, zip_code, delivery_fee_max):
        url = f'https://marketplace.ifood.com.br/v1/merchants?latitude={latitude}&longitude={longitude}&zip_code={zip_code}&page=0&channel=IFOOD&size=50&delivery_fee_from=0&delivery_fee_to={delivery_fee_max}'
        self.base_headers['host'] = self.host_marketplace
        return self.get_json(url,self.base_headers)['merchants']
    
    def get_restaurant_info(self, uuid):
        url = f'https://www.ifood.com.br/api/restaurant/{uuid}'
        self.base_headers['host'] = self.host_api
        return self.get_json(url, self.base_headers)['data']['restaurant']
    
    def get_restaurant_menu(self, uuid):
        url = f'https://www.ifood.com.br/api/restaurants/{uuid}/menu'
        self.base_headers['host'] = self.host_api
        return self.get_json(url, self.base_headers)['data']['menu']
    
    def get_restaurant_flat_items(self, uuid, min_price, max_price):
        flat_menu = []
        for menu_group in self.get_restaurant_menu(uuid):
            for item in menu_group['itens']:
                cleaned_item = {
                    'name' : item['description'],
                    'price' : item.get('unitMinPrice', item.get('unitPrice', 'NaN'))
                }
                if cleaned_item['price'] >= min_price and cleaned_item['price'] <= max_price:
                    flat_menu.append(cleaned_item)
        flat_menu.sort(key=lambda item: item['price'])
        return flat_menu

    def coupon_query(self, latitude, longitude, zip_code, delivery_fee_max, min_price, max_price):
        merchants = self.get_merchants(latitude, longitude, zip_code, delivery_fee_max)
        merchants_full_info = list(map(lambda merchant: self.get_restaurant_info(merchant['id']), merchants ))

        filtered_restaurants_with_items = []
        for restaurant in merchants_full_info:
            if restaurant['closed'] == False and restaurant['unavailable'] == False and restaurant['minimunOrder'] <= max_price:
                filtered_restaurants_with_items.append({
                    'name' : restaurant['name'],
                    'minimunOrder' : restaurant['minimunOrder'],
                    'items' : self.get_restaurant_flat_items(restaurant['uuid'], min_price, max_price)
                })
                
        filtered_restaurants_with_items.sort(key=lambda rest:rest['minimunOrder'])
        return filtered_restaurants_with_items
