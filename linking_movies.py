import rltk
import pandas as pd
import json


# RLTK IMDB Record
class IMDBRecord(rltk.Record):
    def __init__(self, raw_object):
        super().__init__(raw_object)
        self.name = ''

    @rltk.cached_property
    def id(self):
        return self.raw_object['url']

    @rltk.cached_property
    def name_string(self):
        return self.raw_object['name']

    @rltk.cached_property
    def year(self):
        return self.raw_object['year']

    @rltk.cached_property
    def genre(self):
        try:
            '''if ',' in self.raw_object['genre']:
              return self.raw_object['genre'].split(',')
            else:
              return self.raw_object['genre']'''
            return self.raw_object['genre']


        except:
            return ''


# RLTK AFI Record
class AFIRecord(rltk.Record):
    def __init__(self, raw_object):
        super().__init__(raw_object)
        self.name = ''

    @rltk.cached_property
    def id(self):
        return self.raw_object['url']

    @rltk.cached_property
    def name_string(self):
        return self.raw_object['title']

    @rltk.cached_property
    def year(self):
        try:
            '''if ',' in self.raw_object['release_date']:
              return self.raw_object['release_date'].split(',')[-1].strip()
            if '/' in self.raw_object['release_date']:
              return self.raw_object['release_date'].split('/')[-1].strip()'''
            return self.raw_object['release_date']
        except:
            return ''

    @rltk.cached_property
    def genre(self):
        try:
            return self.raw_object['genre']
        except:
            return ''





def year_match(r_imdb, r_afi):
    if ',' in r_afi:
        afi_year = r_afi.split(',')[-1].strip()
    elif '/' in r_afi:
        afi_year = r_afi.split('/')[-1].strip()
    else:
        try:
            if len(r_afi) != 0:
                afi_year = r_afi
            else:
                afi_year = ''
        except:
            afi_year = ''
    imdb_year = str(r_imdb)
    if afi_year == imdb_year:
        return 1
    else:
        return 0
    # return rltk.string_equal(imdb_year,afi_year)


def name_similarity(r_imdb, r_afi):
    # imdb_name = r_imdb['name_string']
    # afi_name = r_afi['name_string']
    imdb_name = r_imdb.lower()
    afi_name = r_afi.lower()

    # imdb_name = r_imdb.lower()
    # afi_name = r_afi.lower()

    return rltk.jaro_winkler_similarity(imdb_name, afi_name)
    # return rltk.levenshtein_similarity(imdb_name,afi_name)


def genre_similarity(r_imdb, r_afi):
    imdb_genre = set(map(lambda x: x.lower().strip(), r_imdb.split(',')))
    afi_genre = set(map(lambda x: x.lower().strip(), r_afi.split(',')))
    return rltk.hybrid_jaccard_similarity(imdb_genre, afi_genre)

def rule_based_method(r_imdb,r_afi):
   max_total_score = 0
   best_afi_movie = ''
   year_score = year_match(r_imdb.year,r_afi.year)
   if year_score == 1:
      genre_score = genre_similarity(r_imdb.genre,r_afi.genre)
      movie_score = name_similarity(r_imdb.name_string,r_afi.name_string)
      if genre_score == 0:
        total_score = 0.7*movie_score + 0.3*year_score
      else:
        total_score = 0.6*movie_score + 0.2*genre_score + 0.2*year_score
      if total_score > max_total_score:
        max_total_score = total_score
        best_afi_movie = r_afi
   elif year_score == 0:
      genre_score = genre_similarity(r_imdb.genre,r_afi.genre)
      movie_score = name_similarity(r_imdb.name_string,r_afi.name_string)
      if genre_score == 0:
        total_score = movie_score
      else:
        total_score = 0.8*movie_score + 0.2*genre_score
      if total_score > max_total_score:
        max_total_score = total_score
        best_afi_movie = r_afi
   if (max_total_score >= 0.8):
     return True, max_total_score
   else:
     return False, max_total_score

if __name__ == "__main__":

    imdb_file = 'imdb.jl'
    afi_file = 'afi.jl'

    # load Datasets
    ds_imdb = rltk.Dataset(reader=rltk.JsonLinesReader(imdb_file), record_class=IMDBRecord,
                           adapter=rltk.MemoryKeyValueAdapter())
    ds_afi = rltk.Dataset(reader=rltk.JsonLinesReader(afi_file), record_class=AFIRecord,
                          adapter=rltk.MemoryKeyValueAdapter())
    imdb_dataframe = ds_imdb.generate_dataframe()
    afi_dataframe = ds_afi.generate_dataframe()

    j_obj = []
    for i,r_imdb in imdb_dataframe.iterrows():
      score = 0
      best_match = ''
      for j,r_afi in afi_dataframe.iterrows():
        result,t_score = rule_based_method(r_imdb,r_afi)
        if result and t_score > score:
          score = t_score
          best_match = r_afi
      if score != 0:
        sim = {'imdb_movie':r_imdb['id'],'afi_movie':best_match['id']}
        j_obj.append(sim)
      else:
        sim = {'imdb_movie':r_imdb['id'],'afi_movie':None}
        j_obj.append(sim)

    json_object = json.dumps(j_obj)
    json_file = open('Rijul_Vohra_hw03_imdb_afi_el.json','w')
    json.dump(json_object,json_file)


