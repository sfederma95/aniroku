import requests

def get_anime_info(num):
    resp = requests.get(f'https://api.jikan.moe/v3/anime/{num}/')
    anime_by_id = resp.json()
    genres = [g['name'] for g in anime_by_id['genres']]
    anime_info = {
        'anime_id':num, 'anime_title':anime_by_id['title'],'anime_img_url':anime_by_id['image_url'], 'anime_type':anime_by_id['type'], 'anime_genres':genres
    }
    return anime_info

def byRating(el):
    return el.rating

def standardize(string):
    new_string = string.lower()
    new_string=new_string.capitalize()
    return new_string
