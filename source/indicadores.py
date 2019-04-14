# coding=utf-8
import datetime

accrualPeriodicityDays = {
  "R/P10Y": 360 * 10,
  "R/P4Y": 360 * 4,
  "R/P3Y": 360 * 3,
  "R/P2Y": 360 * 2,
  "R/P1Y": 360,
  "R/P6M": 30 * 6,
  "R/P4M": 30 * 4,
  "R/P3M": 30 * 3,
  "R/P2M": 30 * 2,
  "R/P1M": 30,
  "R/P0.5M": 30 * 0.5,
  "R/P0.33M": 30 * 0.33,
  "R/P1W": 7,
  "R/P0.5W": 7 * 0.5,
  "R/P0.33W": 7 * 0.33,
  "R/P1D": 1,
  "R/PT1H": 1,
  "R/PT1S": 1,
  "eventual": 0
}

def crearIndicadores(db):
  indicadores = {}

  # indicadores['por_organizacion'] = list(db['data-json'].aggregate([
  #   {"$sort": {"_id": -1}},
  #   {"$limit": 120},
  #   {"$unwind": "$dataset"},
  #   {"$group": {
  #     "_id": {
  #       "fecha": "$fecha",
  #       "organizacion": { "$arrayElemAt": [{ "$split": ["$dataset.source", "."] }, 0] }
  #     },
  #     "datasets": {"$sum": 1},
  #     "recursos": {"$sum": { "$size": "$dataset.distribution" }},
  #     "vistas_totales": {"$sum": "$dataset.vistas.totales"},
  #     "vistas_unicas": {"$sum": "$dataset.vistas.unicas"},
  #   }}
  # ]))

  # indicadores['por_categoria'] = list(db['data-json'].aggregate([
  #   {"$sort": {"_id": -1}},
  #   {"$limit": 120},
  #   {"$unwind": "$dataset"},
  #   {"$unwind": "$dataset.theme"},
  #   {"$group": {
  #     "_id": {
  #       "fecha": "$fecha",
  #       "categoria": "$dataset.theme"
  #     },
  #     "datasets": {"$sum": 1},
  #     "recursos": {"$sum": { "$size": "$dataset.distribution" }},
  #     "vistas_totales": {"$sum": "$dataset.vistas.totales"},
  #     "vistas_unicas": {"$sum": "$dataset.vistas.unicas"},
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

  # indicadores['datasets_por_frecuencia'] = list(db['data-json'].aggregate([
  #   {"$sort": {"_id": -1}},
  #   {"$limit": 1},
  #   {"$unwind": "$dataset"},
  #   {"$group": {
  #     "_id": {
  #       "fecha": "$fecha",
  #       "frecuencia": "$dataset.accrualPeriodicity"
  #     },
  #     "datasets": {"$sum": 1}
  #   }}
  # ]))

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

  indicadores['actualizacion_por_organizacion'] = list(db['data-json'].aggregate([
    {"$sort": {"_id": -1}},
    {"$limit": 1},
    {"$unwind": "$dataset"},
    {"$unwind": "$dataset.distribution"},
    {"$sort": {"dataset.distribution.modified": 1}},
    {"$project": {
      "dataset": "$dataset",
      "dias_recursos": {
        "$divide": [
          {"$subtract":[
            datetime.datetime.utcnow(), "$dataset.distribution.modified"
          ]}
          , 1000 * 60 * 60 * 24
        ]
      }
    }},
    {"$group": {
      "_id": {
        "dataset": "$dataset.title",
        "organizacion": { "$arrayElemAt": [{ "$split": ["$dataset.source", "."] }, 0] }
      },
      "dias_recursos": {"$min": "$dias_recursos"},
      "datasets": {"$push": "$dataset"}
    }},
    {"$project":{
      "dias_recursos":"$dias_recursos",
      "dataset": {"$arrayElemAt": ["$datasets", 0]}
    }},
    {"$project": {
      "dias": {"$min":["$dias_recursos",
        {"$divide": [
          {"$subtract":[
            datetime.datetime.utcnow(), 
            "$dataset.modified"
          ]}
          , 1000 * 60 * 60 * 24
        ]}
      ]},
      "accrualPeriodicity": "$dataset.accrualPeriodicity"
    }}
  ]))

  return indicadores
