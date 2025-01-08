import requests
class SongFinder:
    def __init__(self, api_token):
        self.api_token = api_token
        self.base_url = "https://api.genius.com"

    def search_song(self, lyrics_snippet):
        """Search for songs on Genius using lyrics snippet."""
        headers = {
            "Authorization": f"Bearer {self.api_token}"
        }
        params = {
            "q": lyrics_snippet
        }
        response = requests.get(f"{self.base_url}/search", headers=headers, params=params)

        if response.status_code != 200:
            raise Exception(f"Genius API Error: {response.status_code} - {response.text}")

        data = response.json()
        hits = data["response"]["hits"]

        results = []
        for hit in hits:
            song = hit["result"]
            results.append({
                "title": song["title"],
                "artist": song["primary_artist"]["name"],
                "url": song["url"],
                "art_image_url": song["song_art_image_url"]
            })

        return results


