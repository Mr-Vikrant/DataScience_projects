
from sklearn.neighbors import NearestNeighbors
import numpy as np
from fuzzywuzzy import fuzz 

class Recommender:
    def __init__(self, metric, algorithm, k, data, decode_id_song):
        self.metric = metric
        self.algorithm = algorithm
        self.k = k
        self.data = data
        self.decode_id_song = decode_id_song
        self.data = data
        self.model = self._recommender().fit(data)
    
    def make_recommendation(self, new_song, n_recommendations):
        recommended = self._recommend(new_song=new_song, n_recommendations=n_recommendations)
        print("... Done")
        return recommended 
    
    def _recommender(self):
        return NearestNeighbors(metric=self.metric, algorithm=self.algorithm, n_neighbors=self.k, n_jobs=-1)
    
    def _recommend(self, new_song, n_recommendations):
        # Get the id of the recommended songs
        recommendations = []
        recommendation_ids = self._get_recommendations(new_song=new_song, n_recommendations=n_recommendations)
        # return the name of the song using a mapping dictionary
        recommendations_map = self._map_indices_to_artist_name(recommendation_ids)
        # Translate this recommendations into the ranking of song titles recommended
        for i, (idx, dist) in enumerate(recommendation_ids):
            recommendations.append(recommendations_map[idx])
        return recommendations
                 
    def _get_recommendations(self, new_song, n_recommendations):
        # Get the id of the song according to the text
        recom_song_id = self._fuzzy_matching(song=new_song)
        # Start the recommendation process
        print(f"Starting the recommendation process for {new_song} ...")
        # Return the n neighbors for the song id
        distances, indices = self.model.kneighbors(self.data[recom_song_id], n_neighbors=n_recommendations+1)
        return sorted(list(zip(indices.squeeze().tolist(), distances.squeeze().tolist())), key=lambda x: x[1])[:0:-1]
    
    def _map_indices_to_artist_name(self, recommendation_ids):
        # get reverse mapper
        return {artistID: name for name, artistID in self.decode_id_song.items()}
   
    def _fuzzy_matching(self, song):
        match_tuple = []
        # get match
        for name, idx in self.decode_id_song.items():
            ratio = fuzz.ratio(name.lower(), song.lower())
            if ratio >= 60:
                match_tuple.append((name, idx, ratio))
        # sort
        match_tuple = sorted(match_tuple, key=lambda x: x[2])[::-1]
        if not match_tuple:
            print(f"The recommendation system could not find a match for {song}")
            return
        return match_tuple[0][1]
    
    def recommendByUser(df,ID) :
        df_agg = df.groupby(['userID','name']).agg({'userArtistPlays':sum})
        g = df_agg['userArtistPlays'].groupby(level=0, group_keys=False)
        f = g.nlargest(3).reset_index()
        new_df = f.loc[f['userID'] == ID]
        return new_df