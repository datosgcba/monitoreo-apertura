# coding=utf-8 
def crearIndicadores(db):
  indicadores = {}

  # indicadores['por_organizacion'] = list(db['data-json'].aggregate([
  #   {"$sort": {"_id": -1}},
  #   {"$limit": 120},
  #   {"$unwind": "$dataset"},
  #   {"$project": {
  #     "fecha": "$fecha",
  #     "organizacion": { "$arrayElemAt": [{ "$split": ["$dataset.source", "."] }, 0] },
  #     "dataset": "$dataset.title",
  #     "recursos": { "$size": "$dataset.distribution" },
  #     "vistas": "$dataset.vistas"
  #   }},
  #   {"$group": {
  #     "_id": {
  #       "fecha": "$fecha",
  #       "organizacion": "$organizacion"
  #     },
  #     "datasets": {"$sum": 1},
  #     "recursos": {"$sum": "$recursos"},
  #     "vistas_totales": {"$sum": "$vistas.totales"},
  #     "vistas_unicas": {"$sum": "$vistas.unicas"},
  #   }}
  # ]))

  # indicadores['por_categoria'] = list(db['data-json'].aggregate([
  #   {"$sort": {"_id": -1}},
  #   {"$limit": 120},
  #   {"$unwind": "$dataset"},
  #   {"$unwind": "$dataset.theme"},
  #   {"$project": {
  #     "fecha": "$fecha",
  #     "categoria": "$dataset.theme",
  #     "dataset": "$dataset.title",
  #     "recursos": { "$size": "$dataset.distribution" },
  #     "vistas": "$dataset.vistas"
  #   }},
  #   {"$group": {
  #     "_id": {
  #       "fecha": "$fecha",
  #       "categoria": "$categoria"
  #     },
  #     "datasets": {"$sum": 1},
  #     "recursos": {"$sum": "$recursos"},
  #     "vistas_totales": {"$sum": "$vistas.totales"},
  #     "vistas_unicas": {"$sum": "$vistas.unicas"},
  #   }}
  # ]))

  # indicadores['busquedas'] = list(db['busquedas'].aggregate([
  #   {"$sort": {"_id": -1}},
  #   {"$limit": 120},
  #   {"$group": {
  #     "_id": {
  #       "fecha": "$fecha",
  #       "query": "$query"
  #     },
  #     "vistas_totales": {"$sum": "$vistas_totales"},
  #     "vistas_unicas": {"$sum": "$vistas_unicas"}
  #   }}
  # ]))

  indicadores['datasets_por_frecuencia'] = list(db['data-json'].aggregate([
    {"$sort": {"_id": -1}},
    {"$limit": 1},
    {"$unwind": "$dataset"},
    {"$group": {
      "_id": {
        "fecha": "$fecha",
        "frecuencia": "$dataset.accrualPeriodicity"
      },
      "datasets": {"$sum": 1}
    }}
  ]))

  # indicadores['recursos_por_formato'] = list(db['data-json'].aggregate([
  #   {"$sort": {"_id": -1}},
  #   {"$limit": 1},
  #   {"$unwind": "$dataset"},
  #   {"$unwind": "$dataset.distribution"},
  #   {"$group": {
  #     "_id": {
  #       "fecha": "$fecha",
  #       "formato": "$dataset.distribution.format"
  #     },
  #     "recursos": {"$sum": 1},
  #   }}
  # ]))

  # indicadores['datasets_por_keyword'] = list(db['data-json'].aggregate([
  #   {"$sort": {"_id": -1}},
  #   {"$limit": 1},
  #   {"$unwind": "$dataset"},
  #   {"$unwind": "$dataset.keyword"},
  #   {"$group": {
  #     "_id": {
  #       "fecha": "$fecha",
  #       "keyword": "$dataset.keyword"
  #     },
  #     "datasets": {"$sum": 1},
  #   }}
  # ]))

  # indicadores['datasets_por_publicador'] = list(db['data-json'].aggregate([
  #   {"$sort": {"_id": -1}},
  #   {"$limit": 1},
  #   {"$unwind": "$dataset"},
  #   {"$group": {
  #     "_id": {
  #       "fecha": "$fecha",
  #       "publicador": "$dataset.publisher.name"
  #     },
  #     "datasets": {"$sum": 1},
  #   }}
  # ]))

  # indicadores['datasets_por_fuente'] = list(db['data-json'].aggregate([
  #   {"$sort": {"_id": -1}},
  #   {"$limit": 1},
  #   {"$unwind": "$dataset"},
  #   {"$group": {
  #     "_id": {
  #       "fecha": "$fecha",
  #       "fuente": "$dataset.source"
  #     },
  #     "datasets": {"$sum": 1},
  #   }}
  # ]))

  return indicadores
